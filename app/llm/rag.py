from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.document_loaders import PyPDFLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import PGVector
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings import OllamaEmbeddings
from difflib import SequenceMatcher
import time, asyncio

from .replicate_models import init_replicate 
# from .replicate_models import llamaguard_evaluate_safety
from ..core.db_config import vector_settings

async def llamaguard_evaluate_safety(question):
    return " safe"

class BaseRAGSystem:
    def __init__(self):
        self.llm = init_replicate()
        self.rag_chain = None
        self.vectorstore = None
        self.conversation_state = {}

    def clear_state(self):
        """Clear the conversation state to reset the system."""
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

class RAGSystem_PDF(BaseRAGSystem):
    def __init__(self, file_path):
        super().__init__()
        self.index_pdf(file_path)

    def index_pdf(self, file_path):
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )
        texts = text_splitter.split_documents(docs)

        embedding = OllamaEmbeddings(base_url="http://ollama:11434", model="nomic-embed-text")

        CONNECTION_STRING = vector_settings.DATABASE_URL
        COLLECTION_NAME = 'embeddings.pdf_documents'

        self.vectorstore = PGVector.from_documents(
            embedding=embedding,
            documents=texts,
            collection_name=COLLECTION_NAME,
            connection_string=CONNECTION_STRING,
        )

        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 6},
        )

        prompt = hub.pull("rlm/rag-prompt")

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        def create_rag_chain():
            return (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )

        self.rag_chain = create_rag_chain()

        return {"message": "PDF indexed successfully"}

class RAGSystem_JSON(BaseRAGSystem):
    def __init__(self, file_path):
        super().__init__()
        self.clear_state()
        self.index_json(file_path)

    def index_json(self, file_path):
        loader = JSONLoader(file_path, jq_schema=".patients[]", text_content=False)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )
        texts = text_splitter.split_documents(docs)

        embedding = OllamaEmbeddings(base_url="http://ollama:11434", model="nomic-embed-text")

        CONNECTION_STRING = vector_settings.DATABASE_URL
        COLLECTION_NAME = 'embeddings.json_documents'

        # Initialize the vector store without adding documents first
        vectorstore = PGVector(
            embedding=embedding,
            collection_name=COLLECTION_NAME,
            connection_string=CONNECTION_STRING,
        )

        # Drop the existing tables or collection if needed
        vectorstore.drop_tables()  # Drops all tables if needed

        # Alternatively, you could delete the specific collection
        vectorstore.delete_collection()  # Deletes the specific collection

        # Now, create the collection with the new documents
        vectorstore.create_collection()

        # Now, create the collection with the new documents
        self.vectorstore = PGVector.from_documents(
            embedding=embedding,
            documents=texts,
            collection_name=COLLECTION_NAME,
            connection_string=CONNECTION_STRING,
        )

        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 6},
        )

        prompt = hub.pull("rlm/rag-prompt")

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        def create_rag_chain():
            return (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )

        self.rag_chain = create_rag_chain()

        return {"message": "JSON File indexed successfully"}
    
# async def main():
#     chatbot = RAGSystem_JSON("sample-data.json")
#     print(chatbot.index_json("sample-data.json"))

#     # Mock query
#     question = "Who won the chemistry prize in 2021?"
#     answer = await chatbot.handle_question(question)
#     print(f"Question: {question}\nAnswer: {answer}")

# if __name__ == "__main__":
#     asyncio.run(main())