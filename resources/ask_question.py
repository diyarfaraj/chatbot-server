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


class AskQuestion(Resource):
    def get(self):
        # data = request.get_json()

        question = request.args.get("question")
        if not question:
            return jsonify({"message": "No question in the request"}), 400
        template = """
        Use the following context (delimited by <ctx></ctx>) and the chat history (delimited by <hs></hs>) to answer the question,  Act as a worldclass helpful and professinal AI assistant.
  Answer the question in the same language as the question is being asked.
   You will provide me with answers from the given info about the man with name Diyar Faraj.
   For each question, scan the whole provided document before you give your answer.
   If you cant find the answer, say "Mm, can't find any data about it." and beg for the question to be rephrased:
        ------
        <ctx>
        {context}
        </ctx>
        ------
        <hs>
        {chat_history}
        </hs>
        ------
        {question}
        Answer:
        """
        prompt = PromptTemplate(
            input_variables=["chat_history", "context", "question"],
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

        memory = ConversationBufferMemory(
            memory_key="chat_history", input_key="question"
        )

        print(docsearch)

        # https://stackoverflow.com/questions/76240871/how-do-i-add-memory-to-retrievalqa-from-chain-type-or-how-do-i-add-a-custom-pr for memeoryy

        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            chain_type="stuff",
            retriever=docsearch.as_retriever(),
            memory=memory,
            condense_question_prompt=prompt
            # chain_type_kwargs={
            #     "verbose": True,
            #     "prompt": prompt,
            #     "memory": memory,
            # },
        )

        # todo: memory is not working properly

        # https://medium.com/@avra42/how-to-build-a-personalized-pdf-chat-bot-with-conversational-memory-965280c160f8 good link for our purpose

        result = chain({"question": question})["answer"]
        print("chain memory ", chain.memory)
        response = {
            "answer": result,
        }

        return make_response(jsonify(response), 200)
