from flask import Flask, request
from flask_restful import Resource, Api
import base64
import os
import uuid
from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
api = Api(app)

COSMOS_DB_ACCOUNT_URI = os.environ["COSMOS_DB_ACCOUNT_URI"]
COSMOS_DB_ACCOUNT_KEY = os.environ["COSMOS_DB_ACCOUNT_KEY"]
DATABASE_ID = os.environ['DATABASE_ID']
CONTAINER_ID = os.environ['CONTAINER_ID']

client = CosmosClient(COSMOS_DB_ACCOUNT_URI, COSMOS_DB_ACCOUNT_KEY)
database = client.get_database_client(DATABASE_ID)
container = database.get_container_client(CONTAINER_ID)

class UploadPdf(Resource):
    def post(self):
        file = request.files.get('file')
        if not file:
            return {'error': 'No file provided'}, 400

        file_content = file.read()
        base64_pdf = base64.b64encode(file_content).decode('utf-8')

        pdf_item = {
            'id': str(uuid.uuid4()),
            'fileName': file.filename,
            'mimeType': file.mimetype,
            'data': base64_pdf,
        }

        try:
            container.upsert_item(pdf_item)
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
