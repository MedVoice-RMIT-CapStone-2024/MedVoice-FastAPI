from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.document_loaders import PyPDFLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain import hub 
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings import OllamaEmbeddings
from difflib import SequenceMatcher

import time, asyncio

from .replicate_models import init_replicate, llamaguard_evaluate_safety

class BaseRAGSystem:
    def __init__(self):
        self.llm = init_replicate()
        self.rag_chain = None
        self.conversation_state = {}

    async def query_model(self, question):
        if self.rag_chain is None:
            return "No documents have been indexed yet."

        # if await llamaguard_evaluate_safety(question) == " unsafe":
        #     return "Sorry, I cannot answer this question, please try again"
        # else:
        start_time = time.perf_counter()
        answer = self.rag_chain.invoke(question)
        end_time = time.perf_counter()
        print(f"\nRaw output runtime: {end_time - start_time} seconds\n")
        return answer

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    async def handle_question(self, question):
        # Check for a similar question
        similar_question = None
        for prev_question in self.conversation_state:
            if self.similar(prev_question, question) > 0.8:
                similar_question = prev_question
                break

        if similar_question:
            return self.conversation_state[similar_question]
        else:
            answer = await self.query_model(question)
            self.conversation_state[question] = answer
            return answer

class RAGSystem_PDF(BaseRAGSystem):
    def __init__(self, file_path):
        super().__init__()
        self.index_pdf(file_path)

    def index_pdf(self, file_path):
        # Indexing: Load
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        # Indexing: Split
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )
        all_splits = text_splitter.split_documents(docs)

        # Indexing: Store
        embedding = OllamaEmbeddings(model="nomic-embed-text")
        vectorstore = Chroma.from_documents(
            documents=all_splits,
            embedding=embedding,
        )
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 6},
        )

        # Store retriever for later use
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
        self.index_json(file_path)
    
    def index_json(self, file_path):
        loader = JSONLoader(file_path, jq_schema=".prizes[]", text_content=False)
        docs = loader.load()

        # Indexing: Store
        embedding = OllamaEmbeddings(model="nomic-embed-text")
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embedding,
        )
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 6},
        )

        # Store retriever for later use
        prompt = hub.pull("rlm/rag-prompt")

        def create_rag_chain():
            return (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | self.llm 
                | StrOutputParser()
            )

        self.rag_chain = create_rag_chain()
        
        return {"message": "JSON File indexed successfully"}
    
