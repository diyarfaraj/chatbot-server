from flask import Flask, request, make_response
from flask_restful import Resource, Api
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
from resources.pdf import UploadPdf, GetPdf
import json


app = Flask(__name__)
CORS(app)
api = Api(app)


@api.representation("application/json")
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


api.add_resource(UploadPdf, "/api/uploadPdf")
api.add_resource(GetPdf, "/api/getPdf/<string:pdf_id>")


if __name__ == "__main__":
    app.run(debug=True)
