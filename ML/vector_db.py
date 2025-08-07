from pinecone import Pinecone
import os
import openai
from dotenv import load_dotenv
from chunker import chunk_pdf_text

load_dotenv()

try:
    pineconeClient = Pinecone(api_key = os.getenv("PINECONE-KEY"))
    print('Pinecone client creation successfull')
    index_name = "pdfData-hackrx"
    if not pineconeClient.has_index(index_name):
        pineconeClient.create_index_for_model(
            name=index_name,
            cloud="aws",
            region="ap-south-1",
            embed={
                "model":"llama-text-embed-v2",
                "field_map":{"text": "chunk_text"}
            }
        )
except Exception as e:
    print(f"Pinecone client creation failed with error : {e}")

