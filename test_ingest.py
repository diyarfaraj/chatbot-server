import unittest
from unittest.mock import MagicMock, patch
import base64
from ingest import run_ingest, get_pdf_from_cosmos


class TestIngest(unittest.TestCase):
    @patch("ingest.create_cosmos_client")
    def test_get_pdf_from_cosmos(self, mock_create_cosmos_client):
        mock_container = MagicMock()
        mock_create_cosmos_client.return_value = mock_container

        mock_item = {"data": "test_pdf_data"}
        mock_container.query_items.return_value = [mock_item]

        result = get_pdf_from_cosmos()
        self.assertEqual(result, "test_pdf_data")

    def test_get_pdf_from_cosmos_no_item(self):
        with patch("ingest.create_cosmos_client") as mock_create_cosmos_client:
            mock_container = MagicMock()
            mock_create_cosmos_client.return_value = mock_container
            mock_container.query_items.return_value = []

            result = get_pdf_from_cosmos()
            self.assertIsNone(result)

    @patch("ingest.get_pdf_from_cosmos")
    @patch("ingest.PyPDFLoader")
    @patch("ingest.RecursiveCharacterTextSplitter")
    @patch("ingest.OpenAIEmbeddings")
    @patch("ingest.pinecone")
    @patch("ingest.PineconeStore")
    def test_run_ingest(
        self,
        mock_pinecone_store,
        mock_pinecone,
        mock_openai_embeddings,
        mock_text_splitter,
        mock_pypdf_loader,
        mock_get_pdf_from_cosmos,
    ):
        mock_get_pdf_from_cosmos.return_value = base64.b64encode(
            b"test_pdf_data"
        ).decode("utf-8")

        run_ingest()

        mock_get_pdf_from_cosmos.assert_called_once()
        mock_pypdf_loader.assert_called_once()
        mock_text_splitter.assert_called_once()
        mock_openai_embeddings.assert_called_once()
        mock_pinecone.init.assert_called_once()
        mock_pinecone.deinit.assert_called_once()
        mock_pinecone_store.from_documents.assert_called_once()


if __name__ == "__main__":
    unittest.main()
