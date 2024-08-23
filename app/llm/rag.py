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
    def __init__(self, file_path=None, json_data=None):
        """
        Initialize the RAGSystem_JSON with either a file path to a JSON file
        or the JSON data itself.

        :param file_path: Path to the JSON file (optional)
        :param json_data: JSON data as a dictionary (optional)
        """
        super().__init__()

        if file_path:
            self.index_json_from_file(file_path)
        elif json_data:
            self.index_json_from_data(json_data)
        else:
            raise ValueError("Either file_path or json_data must be provided.")

    def index_json_from_file(self, file_path):
        """
        Load and index the JSON data from a file.

        :param file_path: Path to the JSON file
        """
        loader = JSONLoader(file_path, jq_schema=".patients[]", text_content=False)
        docs = loader.load()
        self.index_documents(docs)

    def index_json_from_data(self, json_data):
        """
        Load and index the JSON data directly from a dictionary.

        :param json_data: JSON data as a dictionary
        """
        # Convert the JSON data into a list of documents if necessary
        if isinstance(json_data, dict) and "patients" in json_data:
            patients = json_data["patients"]
        else:
            raise ValueError("The provided JSON data is not in the expected format.")

        # Convert each patient dictionary to a document with concatenated fields as "page content"
        docs = [
            {"page_content": self.create_page_content(patient), "metadata": {}} 
            for patient in patients
        ]
        self.index_documents(docs)

    def create_page_content(self, patient):
        """
        Create a string that concatenates relevant fields from the patient dictionary.

        :param patient: A dictionary representing a patient's data
        :return: A concatenated string of the patient's data
        """
        return "\n".join(f"{key}: {value}" for key, value in patient.items())

    def index_documents(self, docs):
        """
        Index the provided documents.

        :param docs: List of documents to index
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )
        texts = text_splitter.split_documents(docs)

        embedding = OllamaEmbeddings(base_url="http://ollama:11434", model="nomic-embed-text")

        CONNECTION_STRING = vector_settings.DATABASE_URL
        COLLECTION_NAME = 'embeddings.json_documents'

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
            # Here, docs is a list of dictionaries with a "page_content" key
            return "\n\n".join(doc["page_content"] for doc in docs)

        def create_rag_chain():
            return (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )

        self.rag_chain = create_rag_chain()

        return {"message": "JSON data indexed successfully"}

    
# async def main():
#     chatbot = RAGSystem_JSON("sample-data.json")
#     print(chatbot.index_json("sample-data.json"))

#     # Mock query
#     question = "Who won the chemistry prize in 2021?"
#     answer = await chatbot.handle_question(question)
#     print(f"Question: {question}\nAnswer: {answer}")

# if __name__ == "__main__":
#     asyncio.run(main())
