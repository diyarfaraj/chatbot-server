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
from langchain.chat_models import ChatOpenAI

# from langchain.chains import ConversionChain
# from langchain.chains.conversion.memory import ConversionBufferMemory
from langchain.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate
import streamlit as st
import pdb

# Initialize Pinecone
pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment=os.environ["PINECONE_NAME_SPACE"],
)

# Initialize OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]

# _template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
# You can assume the question about the most recent state of the union address.
# Chat History:
# {chat_history}
# Follow Up Input: {question}
# Standalone question:"""
# CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

# template = """You are an AI assistant for answering questions about the most recent state of the union address.
# You are given the following extracted parts of a long document and a question. Provide a conversational answer.
# If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
# If the question is not about the most recent state of the union, politely inform them that you are tuned to only answer questions about the most recent state of the union.
# end each answer with a a smile ":)"
# Question: {question}
# =========
# {context}
# =========
# Answer in Markdown:"""
# QA_PROMPT = PromptTemplate(template=template, input_variables=["question", "context"])


class AskQuestion(Resource):
    def get(self):
        # data = request.get_json()

        question = request.args.get("question")
        history = request.args.get("history", [])
        if not question:
            return jsonify({"message": "No question in the request"}), 400
        template = """
        Use the following context (delimited by <ctx></ctx>) and the chat history (delimited by <hs></hs>) to answer the question:
        ------
        <ctx>
        {context}
        </ctx>
        ------
        <hs>
        {history}
        </hs>
        ------
        {question}
        Answer:
        """
        prompt = PromptTemplate(
            input_variables=["history", "context", "question"],
            template=template,
        )
        embeddings = OpenAIEmbeddings()

        index_name = os.environ["PINECONE_INDEX_NAME"]
        openai_api_key = os.environ["OPENAI_API_KEY"]

        docsearch = Pinecone.from_existing_index(
            index_name=index_name, embedding=embeddings
        )

        llm = OpenAI(
            batch_size=5, verbose=True, temperature=0.5, openai_api_key=openai_api_key
        )

        memory = ConversationBufferMemory(memory_key="history", input_key="question")

        print(docsearch)

        # https://stackoverflow.com/questions/76240871/how-do-i-add-memory-to-retrievalqa-from-chain-type-or-how-do-i-add-a-custom-pr for memeory

        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=docsearch.as_retriever(),
            verbose=True,
            chain_type_kwargs={
                "verbose": True,
                "prompt": prompt,
                "memory": memory,
            },
        )

        # https://medium.com/@avra42/how-to-build-a-personalized-pdf-chat-bot-with-conversational-memory-965280c160f8 good link for our purpose

        result = chain.run(query=question)
        print("real result ", result)
        response = {
            "answer": result,
        }

        return make_response(jsonify(response), 200)
