from flask import Flask, request
from flask_restful import Resource, Api
import base64
from dotenv import load_dotenv
from utils.ingest import run_ingest

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
                "message": "Successfully returned from ingestion",
            }, 200
        except Exception as error:
            import traceback

            print(f"Error ingesting file : {error}")
            print(f"Traceback: {traceback.format_exc()}")
            return {"error": f"Error ingesting file: {error}"}, 500
