import unittest
from unittest.mock import patch
import base64
from ingest import run_ingest, get_pdf_from_cosmos


class TestIngest(unittest.TestCase):
    @patch("ingest.create_cosmos_client")
    def test_run_ingest(self, mock_create_cosmos_client):
        # Mocking the container client
        mock_container_client = mock_create_cosmos_client.return_value
        mock_container_client.query_items.return_value = [
            {"id": "pdf-1", "data": base64.b64encode(b"test_pdf_data").decode("utf-8")}
        ]

        with patch("ingest.PyPDFLoader.load") as mock_load, patch(
            "ingest.CharacterTextSplitter.split_documents"
        ) as mock_split_documents:
            # Mocking PyPDFLoader.load() and CharacterTextSplitter.split_documents() methods
            mock_load.return_value = ["This is some sample text from the PDF."]
            mock_split_documents.return_value = [
                {
                    "id": "doc-1",
                    "text": "This is some sample text from the PDF.",
                    "metadata": {"source": "pdf-1", "split_num": 0},
                }
            ]

            run_ingest()

            # Check if the PDF data is fetched
            self.assertTrue(mock_create_cosmos_client.called)
            self.assertTrue(mock_container_client.query_items.called)

            # Check if the PDF data is split
            self.assertTrue(mock_load.called)
            self.assertTrue(mock_split_documents.called)


if __name__ == "__main__":
    unittest.main()
