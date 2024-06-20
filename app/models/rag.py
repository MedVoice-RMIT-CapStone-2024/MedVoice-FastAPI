from langchain.chains import LLMChain
from langchain_community.llms import Replicate
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.document_loaders import PyPDFLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain import hub 
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from difflib import SequenceMatcher

import time, asyncio

from .replicate_models import initialize_llm, llamaguard_evaluate_safety

class RAGSystem:
    def __init__(self, file_path):
        self.llm = initialize_llm()
        self.rag_chain = None
        self.conversation_state = {}
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

    async def query_model(self, question):
        if self.rag_chain is None:
            return "No documents have been indexed yet."

        if await llamaguard_evaluate_safety(question) == " unsafe":
            answer="Sorry, I cannot answer this question, please try again"
            print(answer)
        else:
            start_time = time.perf_counter()
            answer = self.rag_chain.invoke(question)
            end_time = time.perf_counter()

            print(f"\nRaw output runtime: {end_time - start_time} seconds\n")
        
        return answer

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def interactive_system(self):
        while True:
            question = input("Please enter your question or type 'exit' to end the conversation: ")
            if question.lower() == 'exit':
                self.conversation_state = {}
                print("Ending the current conversation...")
                break
            elif question.lower() == 'new':
                self.conversation_state = {}
                print("Starting a new conversation...")
                continue
            else:
                # Check if a similar question has been asked before
                similar_question = None
                for prev_question in self.conversation_state:
                    if self.similar(prev_question, question) > 0.8:
                        similar_question = prev_question
                        break

                if similar_question:
                    print(f"As per my previous answer: {self.conversation_state[similar_question]}")
                else:
                    # Use asyncio.run to run the coroutine and get the result
                    answer = asyncio.run(self.query_model(question))
                    self.conversation_state[question] = answer
