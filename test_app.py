import unittest
import base64
import io
from flask_testing import TestCase
from app import app, UploadPdf
import pdb
import json


class TestUploadPdf(TestCase):
    def create_app(self):
        app.config["TESTING"] = True
        return app

    def test_upload_pdf(self):
        with open("test_util/test_file.pdf", "rb") as f:
            content = f.read()
        print("content len", len(content))

        base64_pdf = base64.b64encode(content).decode("utf-8")
        data = {"file": (io.BytesIO(base64.b64decode(base64_pdf)), "test_file.pdf")}
        print("data length", len(data))
        pdb.set_trace()

        response = self.client.post(
            "/api/uploadPdf",
            content_type="multipart/form-data",
            data=data,
            follow_redirects=True,
        )
        print("json diyar: ", response.data)

        pdb.set_trace()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"success", response.data)
        self.assertIn(b"File uploaded and stored in Cosmos DB", response.data)

    def test_upload_no_file(self):
        response = self.client.post(
            "/api/uploadPdf",
            content_type="multipart/form-data",
            data={},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"error", response.data)
        self.assertIn(b"No file provided", response.data)


if __name__ == "__main__":
    unittest.main()
