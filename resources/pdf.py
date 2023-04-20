from flask import Flask, request
from flask_restful import Resource, Api
import base64
import os
import uuid
from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv
from cosmos_client import create_cosmos_client
from ingest import run_ingest

load_dotenv()

app = Flask(__name__)
api = Api(app)

container = create_cosmos_client()

class UploadPdf(Resource):
    def post(self):
        file = request.files.get('file')
        if not file:
            return {'error': 'No file provided'}, 400

        file_content = file.read()
        base64_pdf = base64.b64encode(file_content).decode('utf-8')
        
        client_ip = request.remote_addr
        pdf_item = {
            'id':f'pdf-{client_ip}',
            'fileName': file.filename,
            'mimeType': file.mimetype,
            'data': base64_pdf,
        }

        try:
            container.upsert_item(pdf_item)
            run_ingest()
            return {'success': True, 'message': 'File uploaded and stored in Cosmos DB'}, 200
        except Exception as error:
            print(f"Error storing the file in Cosmos DB: {error}")
            return {'error': f"Error storing the file in Cosmos DB: {error}"}, 500

class GetPdf(Resource):
    def get(self, pdf_id):
        try:
            pdf_item = container.read_item(item=pdf_id, partition_key=pdf_id)
            return {
                'id': pdf_item['id'],
                'fileName': pdf_item['fileName'],
                'mimeType': pdf_item['mimeType'],
                'data': pdf_item['data'],
            }, 200
        except Exception as error:
            print(f"Error retrieving the PDF from Cosmos DB: {error}")
            return {'error': f"Error retrieving the PDF from Cosmos DB: {error}"}, 500
