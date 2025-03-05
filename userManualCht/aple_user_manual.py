# import os
# import glob
# import time
# from dotenv import load_dotenv
# from langchain_groq import ChatGroq
# from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains import create_retrieval_chain
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain.schema import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter

# # Load environment variables
# load_dotenv()

# groq_api_key = os.getenv('GROQ_API_KEY')
# llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192", temperature=0)
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# FAISS_INDEX_PATH = "data/faiss_index"
# vectors = None

# # 🔹 Simple answer prompt
# prompt = ChatPromptTemplate.from_template(
#     "Using the provided context, answer the user's query in a simple and concise manner.\n\n"
#     "Context: {context}\n\nQuery: {input}\n\nAnswer:"
# )

# class EndpointRetriever:
#     _instance = None  # Singleton instance

#     def __new__(cls, file_path):
#         if cls._instance is None:
#             cls._instance = super(EndpointRetriever, cls).__new__(cls)
#             cls._instance.file_path = file_path
#             cls._instance.vectors = None
#         return cls._instance

#     def vector_embedding(self):
#         """Creates or loads FAISS vector embeddings."""
#         embeddings = HuggingFaceEmbeddings()
        
#         if self.vectors is not None:
#             print("FAISS index already loaded, skipping reload.")
#             return {"status": "FAISS index already loaded."}

#         if os.path.exists(FAISS_INDEX_PATH) and glob.glob(f"{FAISS_INDEX_PATH}/*"):
#             print("Loading existing FAISS index...")
#             self.vectors = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
#             return {"status": "Loaded existing FAISS index."}

#         # Creating vector embeddings
#         with open(self.file_path, 'r', encoding="utf-8") as file:
#             text = file.read()

#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=2000)
#         chunks = text_splitter.split_text(text)

#         documents = [Document(page_content=chunk) for chunk in chunks]
#         self.vectors = FAISS.from_documents(documents, embeddings)
#         self.vectors.save_local(FAISS_INDEX_PATH)

#         return {"status": "FAISS index successfully created."}  # No unnecessary print statements

#     def retrieval(self, query):
#         """Retrieves the most relevant answer based on the user's query."""
#         if not self.vectors:
#             print("Vector store not initialized. Please run the embedding function first.")
#             return None

#         document_chain = create_stuff_documents_chain(llm, prompt)
#         retriever = self.vectors.as_retriever()
#         retrieval_chain = create_retrieval_chain(retriever, document_chain)

#         response = retrieval_chain.invoke({'context': 'Your context here', 'input': query})

#         try:
#             return response['answer']
#         except Exception as e:
#             print(f"Error: {e}")
#             return None

#     def process_query(self, query):
#         """Main function that initializes embeddings and processes the query."""
#         start_time = time.time()  # Start time for measuring response time
#         vector_status = None
#         if self.vectors is None:
#             vector_status = self.vector_embedding()  # Initialize vectors if not loaded
#         else:
#             vector_status = {"status": "Loaded existing FAISS index."}  # If FAISS is already loaded
        
#         # Process the query directly
#         answer = self.retrieval(query)

#         end_time = time.time()  # End time after query processing
#         response_time = round(end_time - start_time, 2)  # Calculate response time

#         return {
#             "vector_status": vector_status,  # Include vector status in response
#             "query": query,
#             "Model Response": answer,
#             "response_time": f"{response_time} seconds"  # Include response time
#         }

# text_file_path = "data/document.txt"  # Change this to your actual text file

# retriever = EndpointRetriever(text_file_path)

# retriever.vector_embedding()

# query = "how to setup cellular service"

# response = retriever.process_query(query)

# print("\n--- Query Response ---")
# print(response)


# folder of text file----------------------------------------------------------------------------------------------------------------

import os
import glob
import time
import threading
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# Get API key and initialize LLM
groq_api_key = os.getenv('GROQ_API_KEY')
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192", temperature=0)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# FAISS index path
FAISS_INDEX_PATH = "data/faiss_index"

# Define prompt structure
prompt = ChatPromptTemplate.from_template(
    "You are an AI assistant trained on Apple's iPhone user manual. "
    "Your task is to provide clear, step-by-step guidance based on the official Apple support documentation.\n\n"
    
    "Follow this structured format in your response:\n"
    "**Title:** [Brief title of the solution]\n"
    "**Steps:**\n"
    "1. [Step 1]\n"
    "2. [Step 2]\n"
    "3. [Step 3]\n"
    "4. [Step 4]\n"
    "5. [Additional steps if required]\n\n"
    
    "- [Mention related settings in one line if applicable]\n\n"
    
    "Now, using the provided context, answer the user's query accordingly.\n\n"
    
    "**Context:** {context}\n"
    "**User Query:** {input}\n\n"
    "**Answer:**"
)


class EndpointRetriever:
    _instance = None  # Singleton instance

    def __new__(cls, folder_path):
        if cls._instance is None:
            cls._instance = super(EndpointRetriever, cls).__new__(cls)
            cls._instance.folder_path = folder_path
            cls._instance.vectors = None
        return cls._instance

    def load_text_files(self):
        """Loads all text files from a folder in parallel and merges content."""
        print("Scanning folder for text files...")
        text_files = glob.glob(os.path.join(self.folder_path, "*.txt"))

        if not text_files:
            print("No text files found.")
            return ""

        print(f"{len(text_files)} files found. Reading in parallel...")

        def read_file(file_path, content_list):
            with open(file_path, 'r', encoding="utf-8") as file:
                content_list.append(file.read())

        content_list = []
        threads = [threading.Thread(target=read_file, args=(fp, content_list)) for fp in text_files]
        
        for thread in threads: thread.start()
        for thread in threads: thread.join()

        print("All text files loaded!")
        return "\n".join(content_list)

    def vector_embedding(self):
        """Creates or loads FAISS vector embeddings."""
        embeddings = HuggingFaceEmbeddings()

        if self.vectors is not None:
            print("FAISS index already in memory.")
            return {"status": "FAISS already loaded."}

        if os.path.exists(FAISS_INDEX_PATH) and glob.glob(f"{FAISS_INDEX_PATH}/*"):
            print("Loading existing FAISS index...")
            self.vectors = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            return {"status": "FAISS loaded from disk."}

        print("Creating new FAISS index...")

        text = self.load_text_files()
        if not text:
            print("No data available for indexing.")
            return {"status": "No data to process."}

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=100)  # Optimized chunk size
        chunks = text_splitter.split_text(text)

        print(f"{len(chunks)} chunks created. Embedding now... please wait...")

        documents = [Document(page_content=chunk) for chunk in chunks]
        self.vectors = FAISS.from_documents(documents, embeddings)
        self.vectors.save_local(FAISS_INDEX_PATH)

        print("FAISS index saved!")
        return {"status": "FAISS created & saved."}

    def retrieval(self, query):
        """Retrieves the most relevant answer based on the user's query."""
        if not self.vectors:
            print("FAISS index not found. Run vector_embedding first.")
            return None

        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = self.vectors.as_retriever(search_kwargs={"k": 3})  # Retrieve top 3 matches
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        response = retrieval_chain.invoke({'context': 'Your context here', 'input': query})

        return response.get('answer', "No relevant information found.")

    def process_query(self, query):
        """Main function that initializes embeddings and processes the query."""
        start_time = time.time()

        if self.vectors is None:
            print("FAISS not loaded. Initializing...")
            vector_status = self.vector_embedding()
        else:
            vector_status = {"status": "Loading existing FAISS index"}

        print("Retrieving...")
        answer = self.retrieval(query)

        response_time = round(time.time() - start_time, 2)
        print(f"Query completed in {response_time} seconds.")

        return {
            "output": vector_status,
            "query": query,
            "Model Response": answer,
            "response_time": f"{response_time} seconds"
        }


# **Main Execution**
# if __name__ == "__main__":
#     text_folder_path = "/Users/macbook/Desktop/headless_app_chat_with_api/userManualCht/scraped_texts"
#     retriever = EndpointRetriever(text_folder_path)

#     # Load FAISS index at startup
#     retriever.vector_embedding()

#     # Interactive loop for queries
#     while True:
#         query = input("Enter your query (type 'exit' to quit): ").strip()

#         if query.lower() == "exit":
#             print("Exiting...")
#             break  # Stop execution

#         response = retriever.process_query(query)
#         print("\n--- Model Response ---")
#         print(response["Model Response"])
