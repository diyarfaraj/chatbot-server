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

question_prompt_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

Chat History:
{context}
Follow Up Input: {question}
Standalone question::"""
QUESTION_PROMPT = PromptTemplate(
    template=question_prompt_template, input_variables=["context", "question"]
)

combine_prompt_template = """Given the following extracted parts of a long document and a question
If you don't know the answer, just say that you don't know. Don't try to make up an answer.

QUESTION: {question}
=========
{summaries}
=========
Answer in English:"""
COMBINE_PROMPT = PromptTemplate(
    template=combine_prompt_template, input_variables=["summaries", "question"]
)


class AskQuestion(Resource):
    def get(self):
        # data = request.get_json()

        question = request.args.get("question")
        history = request.args.get("history", [])
        print(question)
        if not question:
            return jsonify({"message": "No question in the request"}), 400

        embeddings = OpenAIEmbeddings()
        llm = ChatOpenAI(
            verbose=True,
            temperature=0,
        )
        index_name = os.environ["PINECONE_INDEX_NAME"]

        vStore = Pinecone.from_existing_index(
            index_name=index_name, embedding=embeddings
        )

        docsearch = vStore.similarity_search(question)
        print("docsearch : ", docsearch)
        # docs = vStore.as_retriever()
        # print("vstore as retriver: ", docs)

        # todo: make sure the docs (pineconde insformation ) is returned correctly, seems like a nested structure.
        # TODO: har laddat upp en doc till python-test men verkar konstigt form. gör en ny ingestion och print info men kommentera ut innan det skickas till pinecone
        # ----------------------------------------------------------------
        # chain = load_qa_chain(
        #     llm,
        #     chain_type="stuff",
        #     return_map_steps=True,
        #     question_prompt=QUESTION_PROMPT,
        #     combine_prompt=COMBINE_PROMPT,
        # )

        qa = ConversationalRetrievalChain.from_llm(
            llm=llm, retriever=vStore.as_retriever(), return_source_documents=True
        )
        print("diyar chain: ", qa)
        result = qa({"question": question, "chat_history": history})
        # qa = ConversationalRetrievalChain.from_llm(
        #     llm=llm, retriever=docs, return_source_documents=True
        # )
        # print("diyar result: ", qa)

        # result = qa({"question": question, "chat_history": history})
        print("diyar result: ", result)

        response = {
            "answer": result["answer"],
        }

        return make_response(jsonify(response), 200)
