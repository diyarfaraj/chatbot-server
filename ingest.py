import base64
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Pinecone
import pinecone
import os
from dotenv import load_dotenv

load_dotenv()
# from config import PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_NAME_SPACE
from cosmos_client import create_cosmos_client
import tempfile

pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],  # find at app.pinecone.io
    environment=os.environ["PINECONE_NAME_SPACE"],  # next to api key in console
)
index_name = os.environ["PINECONE_INDEX_NAME"]


def run_ingest(pdf_item):
    # Fetch the PDF data from Cosmos DB
    pdf_data = pdf_item[
        "data"
    ]  # TODO: make the data from the PDF file is available and correctly formatted

    # Decode the base64 PDF data
    pdf_bytes = base64.b64decode(pdf_data)

    # Save the PDF bytes to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_bytes)
        temp_file_path = temp_file.name

    # Load the raw PDF content
    loader = PyPDFLoader(temp_file_path)
    raw_docs = loader.load_and_split()

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    docs = text_splitter.split_documents(raw_docs)
    print("diyar docs 0: ", docs[10])
    # for doc in docs:
    #     new_url = doc.metadata["source"]
    #     doc.metadata.update({"source": doc})

    # Create and store the embeddings in Pinecone
    embeddings = OpenAIEmbeddings()
    print(f"Going to add {len(docs)} to Pinecone")
    Pinecone.from_documents(docs, embeddings, index_name=index_name)

    # pinecone.deinit()
    # Remove the temporary file
    os.unlink(temp_file_path)
    print("Ingestion complete")


def get_pdf_from_cosmos():
    # Assuming you have a unique PDF in the container
    container = create_cosmos_client()
    for item in container.query_items(
        query='SELECT * FROM c WHERE CONTAINS(c.id, "pdf-")',
        enable_cross_partition_query=True,
    ):
        return item["data"]
    return None


if __name__ == "__main__":
    print("Ingestion started")
    run_ingest()
    print("Ingestion complete")
