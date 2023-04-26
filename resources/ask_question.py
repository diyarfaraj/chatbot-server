import os
import json
import pinecone
import openai
from flask import request, jsonify
from flask_restful import Resource

# Initialize Pinecone
pinecone.init(api_key=os.environ["PINECONE_API_KEY"])
pinecone.deinit()

# Initialize OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]


def generate_answer(prompt):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    answer = response.choices[0].text.strip()
    return answer


class AskQuestion(Resource):
    def post(self):
        data = request.get_json()

        question = data.get("question")
        history = data.get("history", [])

        if not question:
            return jsonify({"message": "No question in the request"}), 400

        # Fetch and process documents
        # TODO: Implement your logic for fetching documents from your data source (e.g., Cosmos DB)

        # Generate embeddings for the question and documents
        # TODO: Use the embeddings model of your choice
        embeddings = OpenAIEmbeddings()

        # Perform similarity search
        index_name = os.environ["PINECONE_INDEX_NAME"]
        Pinecone.from_existing_index(docs, embeddings, index_name=index_name)
        similarities = index.fetch(
            [question_embedding], ids=[doc["id"] for doc in documents]
        )
        sorted_similarities = sorted(
            similarities.items(), key=lambda x: x[1], reverse=True
        )

        # Prepare the context for generating the answer
        context = " ".join([documents[i]["text"] for i, _ in sorted_similarities[:3]])
        prompt = f"Question: {question}\n\n{context}\n\nAnswer:"

        # Generate the answer
        answer = generate_answer(prompt)

        response = {
            "answer": answer,
            "source_docs": [
                {"id": doc_id, "text": documents[i]["text"]}
                for i, doc_id in sorted_similarities[:3]
            ],
        }

        return jsonify(response), 200


def fetch_top_document(index, question):
    # Add the code for fetching the top document and its text using Pinecone
    pass
