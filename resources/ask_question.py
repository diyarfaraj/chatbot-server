import os
import json
import pinecone
import openai
from flask import request, jsonify, make_response
from flask_restful import Resource
from langchain import OpenAI, VectorDBQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.document_loaders import TextLoader
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains import LLMChain
import pdb

# Initialize Pinecone
pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment=os.environ["PINECONE_NAME_SPACE"],
)

# Initialize OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]


class AskQuestion(Resource):
    def get(self):
        # data = request.get_json()

        question = request.args.get("question")
        # history = data.get("history", [])
        print(question)
        if not question:
            return jsonify({"message": "No question in the request"}), 400

        embeddings = OpenAIEmbeddings()
        llm = OpenAI(temperature=0)
        # Perform similarity search
        index_name = os.environ["PINECONE_INDEX_NAME"]

        vStore = Pinecone.from_existing_index(
            index_name=index_name, embedding=embeddings
        )
        question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT)
        doc_chain = load_qa_chain(llm, chain_type="map_reduce")
        retriever = vStore.as_retriever(seach_type="similarity", search_kwrgs={"k": 2})
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        )
        qa = ConversationalRetrievalChain(
            retriever=retriever,
            question_generator=question_generator,
            memory=memory,
            combine_docs_chain=doc_chain,
        )
        # documents = docsearch.similarity_search(question)
        # model = VectorDBQA.from_chain_type(
        #     llm=OpenAI(), chain_type="map_reduce", vectorstore=vStore
        # )
        # Convert Document objects to a JSON serializable format
        # result = model.run(question)

        result = qa({"question": question})
        print(result)
        # pdb.set_trace()

        response = {
            "answer": result["answer"],
        }
        print(response)

        return make_response(jsonify(response), 200)


def fetch_top_document(index, question):
    # Add the code for fetching the top document and its text using Pinecone
    # TODO: Implement your logic for fetching the top document and its text using Pinecone
    pass


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
