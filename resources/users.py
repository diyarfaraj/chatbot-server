# users.py
import os
from azure.cosmos import CosmosClient, PartitionKey
from flask_restful import Resource, reqparse
from utils.cosmos_client import create_cosmos_client
from werkzeug.security import generate_password_hash, check_password_hash

import jwt
import datetime
from flask import jsonify, make_response

SECRET_KEY = os.getenv("SECRET_KEY")


class UserRegister(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("username", required=True, help="Username is required")
        self.parser.add_argument("password", required=True, help="Password is required")
        self.client = create_cosmos_client("users")

    def post(self):
        data = self.parser.parse_args()
        hashed_password = generate_password_hash(data["password"], method="sha256")

        # add user to db
        new_user = {
            "id": data["username"],
            "username": data["username"],
            "password": hashed_password,
            "created_at": datetime.datetime.utcnow().isoformat(),
        }

        self.client.create_item(body=new_user)
        return {"message": "User created successfully"}, 201


class UserLogin(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("username", required=True, help="Username is required")
        self.parser.add_argument("password", required=True, help="Password is required")
        self.client = create_cosmos_client("users")

    def post(self):
        data = self.parser.parse_args()
        user = self.client.read_item(
            item=data["username"], partition_key=data["username"]
        )

        if not user:
            return {"message": "User not found"}, 404

        if check_password_hash(user["password"], data["password"]):
            token = jwt.encode(
                {
                    "username": user["username"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
                },
                SECRET_KEY,
                algorithm="HS256",
            )

            return {"token": token}, 200

        return {"message": "Password is incorrect"}, 401


# This is an in-memory store for blacklisted tokens. Redis should be used for prod environments
BLACKLIST = set()


class UserLogout(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("token", required=True, help="Token is required")

    def post(self):
        data = self.parser.parse_args()
        token = data["token"]
        BLACKLIST.add(token)
        return {"message": "User logged out successfully"}, 200
