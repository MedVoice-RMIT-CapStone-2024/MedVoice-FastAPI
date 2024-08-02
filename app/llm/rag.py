from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import PGVector
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings import OllamaEmbeddings
from difflib import SequenceMatcher
import time, asyncio
from ..core.db_config import settings
from ..crud import crud_embedding
from ..schemas.embedding import EmbeddingCreate
from .replicate_models import init_replicate
from ..db.session import *
from uuid import uuid4

async def llamaguard_evaluate_safety(question):
    return "safe"

class BaseRAGSystem:
    def __init__(self):
        self.llm = init_replicate()
        self.rag_chain = None
        self.vectorstore = None
        self.conversation_state = {}

    async def query_model(self, question, streaming=False):
        if self.rag_chain is None:
            return "No documents have been indexed yet."

        start_time = time.perf_counter()
        answer = ""

        if streaming:
            async for token in self.async_token_stream(question):
                self.token_callback(token)
                answer += token + " "
        else:
            answer = self.rag_chain.invoke(question)

        end_time = time.perf_counter()
        print(f"\nRaw output runtime: {end_time - start_time} seconds\n")
        return answer.strip()

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    async def handle_question(self, question, streaming=False):
        similar_question = None
        for prev_question in self.conversation_state:
            if self.similar(prev_question, question) > 0.8:
                similar_question = prev_question
                break

        if similar_question:
            return self.conversation_state[similar_question]
        else:
            answer = await self.query_model(question, streaming=streaming)
            self.conversation_state[question] = answer
            return answer

    async def async_token_stream(self, question: str):
        response = self.rag_chain.invoke(question)
        for token in response.split():
            yield token
            await asyncio.sleep(0.01)

    def token_callback(self, token):
        print(token, end=' ', flush=True)

class RAGSystem_JSON(BaseRAGSystem):
    def __init__(self, file_path):
        super().__init__()
        asyncio.run(self.index_json(file_path))

    async def index_json(self, file_path):
        print("Loading JSON data")
        loader = JSONLoader(file_path, jq_schema=".patients[]", text_content=False)
        docs = loader.load()

        print("Creating embeddings")
        embedding = OllamaEmbeddings(base_url="http://ollama:11434", model="nomic-embed-text")

        CONNECTION_STRING = settings.DATABASE_URL
        COLLECTION_NAME = 'embeddings.json_documents'

        self.vectorstore = PGVector.from_documents(
            documents=docs,
            embedding=embedding,
            collection_name=COLLECTION_NAME,
            connection_string=CONNECTION_STRING,
        )

        print("Inserting mock embeddings")
        async with SessionLocal() as session:
            for doc, vec in zip(docs, self.vectorstore.embeddings):
                embedding_create = EmbeddingCreate(
                    document_id=uuid4(),
                    content=doc.page_content,  # Ensure the content is stored as JSON
                    embedding=vec  # Already a list from PGVector
                )
                print(f"Inserting embedding for document ID: {embedding_create.document_id}")
                await crud_embedding.create_embedding(session, embedding_create)

        print("Creating retriever")
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 6},
        )

        prompt = hub.pull("rlm/rag-prompt")

        def create_rag_chain():
            return (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )

        self.rag_chain = create_rag_chain()

        print("JSON File indexed successfully")
        return {"message": "JSON File indexed successfully"}

if __name__ == "__main__":
    import asyncio
    async def main():
        chatbot = RAGSystem_JSON("assets/patients.json")
        await chatbot.index_json("assets/patients.json")

        # Mock query
        question = "What is the medical diagnosis for patient Adam?"
        answer = await chatbot.handle_question(question)
        print(f"Question: {question}\nAnswer: {answer}")

    asyncio.run(main())
