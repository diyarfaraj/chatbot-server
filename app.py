from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from resources.pdf import UploadPdf
from resources.ask_question import AskQuestion
import json

from resources.users import BLACKLIST, UserLogin, UserLogout, UserRegister


app = Flask(__name__)
CORS(app)
api = Api(app)

# TODO: make these configurable:
# create members account
# openai api key
# system message
# pinecone info
# azure cosnmos info


@api.representation("application/json")
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


@app.before_request
def before_request():
    if "Authorization" in request.headers:
        token = request.headers["Authorization"].replace("Bearer ", "")
        if token in BLACKLIST:
            return jsonify({"message": "Token has been blacklisted"}), 401


api.add_resource(UploadPdf, "/api/uploadPdf")
api.add_resource(AskQuestion, "/api/ask")
api.add_resource(UserRegister, "/api/register")
api.add_resource(UserLogin, "/api/login")
api.add_resource(UserLogout, "/api/logout")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
