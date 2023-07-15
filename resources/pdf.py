from flask import Flask, request
from flask_restful import Resource, Api
import base64
import os
import uuid
from dotenv import load_dotenv

# from cosmos_client import create_cosmos_client
from ingest import run_ingest
import PyPDF2
from io import BytesIO

load_dotenv()

app = Flask(__name__)
api = Api(app)


class UploadPdf(Resource):
    def post(self):
        file = request.files.get("file")
        if not file:
            return {"error": "No file provided"}, 400

        file_content = file.read()
        pdf_bytes = base64.b64encode(file_content)

        client_ip = request.remote_addr
        pdf_item = {
            "id": f"pdf-{client_ip}",
            "fileName": file.filename,
            "mimeType": file.mimetype,
            "data": pdf_bytes.decode("utf-8"),
        }

        try:
            # container.upsert_item(pdf_item)
            run_ingest(pdf_item)
            return {
                "success": True,
                "message": "File uploaded and stored in Cosmos DB",
            }, 200
        except Exception as error:
            import traceback

            print(f"Error ingesting or storing the file in Cosmos DB: {error}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                "error": f"Error ingesting or storing the file in Cosmos DB: {error}"
            }, 500


class GetPdf(Resource):
    def get(self, pdf_id):
        try:
            pdf_item = container.read_item(item=pdf_id, partition_key=pdf_id)
            return {
                "id": pdf_item["id"],
                "fileName": pdf_item["fileName"],
                "mimeType": pdf_item["mimeType"],
                "data": pdf_item["data"],
            }, 200
        except Exception as error:
            print(f"Error retrieving the PDF from Cosmos DB: {error}")
            return {"error": f"Error retrieving the PDF from Cosmos DB: {error}"}, 500
