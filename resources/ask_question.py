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
        chat_history = request.args.get("history", [])
        if not question:
            return jsonify({"message": "No question in the request"}), 400
        question_prompt_template = """Use the following portion of a long document to see if any of the text is relevant to answer the question. 
        Return any relevant text in a professional manner.
        {context}
        Question: {question}
        Relevant text:"""
        QUESTION_PROMPT = PromptTemplate(
            template=question_prompt_template, input_variables=["context", "question"]
        )

        combine_prompt_template = """Given the following extracted parts of a long document and a question, create a final answer as Diyar Farajs AI assistant . 
        If you don't know the answer, just say that you don't know. Don't try to make up an answer. End each reply with a happy emoji

        QUESTION: {question}
        =========
        {summaries}
        =========
        Answer:"""
        COMBINE_PROMPT = PromptTemplate(
            template=combine_prompt_template, input_variables=["summaries", "question"]
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

        memory = ConversationBufferMemory()  # add this to chat

        chain = load_qa_chain(
            llm,
            chain_type="map_reduce",
            question_prompt=QUESTION_PROMPT,
            combine_prompt=COMBINE_PROMPT,
        )
        docs = docsearch.similarity_search(question)

        result = chain.run(
            input_documents=docs,
            question=question,
        )

        response = {
            "answer": result,
        }

        return make_response(jsonify(response), 200)
