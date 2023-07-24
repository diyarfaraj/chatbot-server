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
from langchain.chains import (
    RetrievalQA,
    ConversationalRetrievalChain,
    LLMChain,
    ConversationChain,
)
from langchain.memory import ConversationBufferMemory
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

# from langchain.chains import ConversionChain
# from langchain.chains.conversion.memory import ConversionBufferMemory
from langchain.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate
import utils.cosmos_client

# Initialize Pinecone
pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment=os.environ["PINECONE_NAME_SPACE"],
)

# Initialize OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]


class AskQuestion(Resource):
    cosmos_container = utils.cosmos_client.create_cosmos_client("messages")

    def get(self):
        # data = request.get_json()

        question = request.args.get("question")
        if not question:
            return jsonify({"message": "No question in the request"}), 400
        template = """You are a worldclass helpful and professinal AI assistant.
        Answer the question in the same language as the question is being asked.
        You will provide me with answers from the given info about the man with name Diyar Faraj.
        For each question, scan the whole provided document before you give your answer.
        Keep your answers as complete as possible, and always be polite and professional.
        If you cant find the answer, say "Mm, can't find any data about it." and beg for the question to be rephrased.
        Answer the question in the same language as the question. 

        {context}

        {chat_history}
        Human: {human_input}
        Chatbot:"""

        prompt = PromptTemplate(
            input_variables=["chat_history", "human_input", "context"],
            template=template,
        )

        embeddings = OpenAIEmbeddings()
        index_name = os.environ["PINECONE_INDEX_NAME"]
        openai_api_key = os.environ["OPENAI_API_KEY"]

        docsearch = Pinecone.from_existing_index(
            index_name=index_name, embedding=embeddings
        )
        docs = docsearch.similarity_search(question)

        llm = OpenAI(
            batch_size=5, verbose=True, temperature=0.5, openai_api_key=openai_api_key
        )

        memory = ConversationBufferMemory(
            memory_key="chat_history", input_key="human_input"
        )

        chain = load_qa_chain(llm=llm, chain_type="stuff", memory=memory, prompt=prompt)

        # todo: memory is not working properly
        result = chain(
            {"input_documents": docs, "human_input": question}, return_only_outputs=True
        )
        print("chain memory ", chain.memory.buffer)

        # save question and answer in cosmosDB
        client_ip = request.headers.get("Client-IP")
        if client_ip is None:
            client_ip = "127.0.0.1"

        utils.cosmos_client.save_question_answer(
            self.cosmos_container, question, result["output_text"], client_ip
        )

        response = {
            "answer": result,
        }

        return make_response(jsonify(response), 200)
