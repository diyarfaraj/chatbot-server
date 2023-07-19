from flask import Flask, request, make_response
from flask_restful import Resource, Api
from flask_cors import CORS
from resources.pdf import UploadPdf
from resources.ask_question import AskQuestion
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
api.add_resource(AskQuestion, "/api/ask")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
