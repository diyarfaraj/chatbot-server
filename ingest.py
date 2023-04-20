import base64
from langchain.text_splitter  import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Pinecone
import pinecone
# from config import PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_NAME_SPACE
from cosmos_client import create_cosmos_client

def run_ingest():
    # Fetch the PDF data from Cosmos DB
    pdf_data = get_pdf_from_cosmos()

    # Decode the base64 PDF data
    pdf_bytes = base64.b64decode(pdf_data)
    print('pdf_bytes', pdf_bytes)
    # Load the raw PDF content
    loader = PyPDFLoader(pdf_bytes)
    raw_docs = loader.load()

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(raw_docs)

    # Create and store the embeddings in Pinecone
    embeddings = OpenAIEmbeddings()
    pinecone.init(api_key=PINECONE_API_KEY)
    index = pinecone.deinit.Index(index_name=PINECONE_INDEX_NAME)

    PineconeStore.from_documents(docs, embeddings, {
        "pinecone_index": index,
        "namespace": PINECONE_NAME_SPACE,
        "text_key": "text"
    })

    pinecone.deinit()

def get_pdf_from_cosmos():
    # Assuming you have a unique PDF in the container
    container = create_cosmos_client()
    for item in container.query_items(query='SELECT * FROM c WHERE CONTAINS(c.id, "pdf-")', enable_cross_partition_query=True):
        return item['data']
    return None

if __name__ == "__main__":
    run_ingest()
    print("Ingestion complete")
