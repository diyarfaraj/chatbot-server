import unittest
import base64
import io
from flask_testing import TestCase
from app import app, UploadPdf
import pdb
import json
import os
import tempfile
from reportlab.pdfgen import canvas


class TestUploadPdf(TestCase):
    def create_app(self):
        app.config["TESTING"] = True
        return app

    def test_upload_pdf(self):
        with open("test_util/test_text.pdf", "rb") as f:
            content = f.read()
        print("content len", len(content))

        base64_pdf = base64.b64encode(content).decode("utf-8")
        data = {"file": (io.BytesIO(base64.b64decode(base64_pdf)), "test_text.pdf")}

        response = self.client.post(
            "/api/uploadPdf",
            content_type="multipart/form-data",
            data=data,
            follow_redirects=True,
        )

        print("json diyar: ", response.data)
        # os.remove(temp_pdf_file)
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


def create_temp_pdf_file(
    text=" jaja When I was 16, I landed my very first job at the enchanting Borås Zoo. This summer job",
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        # Create a PDF Canvas object
        c = canvas.Canvas(temp.name)

        # Add text to the PDF
        c.drawString(100, 750, text)

        # Save the PDF
        c.save()

    return temp.name


if __name__ == "__main__":
    unittest.main()
