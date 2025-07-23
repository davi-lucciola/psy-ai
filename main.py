import os
import dotenv as env
import streamlit as st
from typing import List
from langchain.globals import set_debug

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_text_splitters import CharacterTextSplitter

from external import load_docx
from prompts import PSY_AI_PROMPT


set_debug(True)


def create_docs_ebeddings(documents: List[Document]) -> FAISS:
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=250)
    texts = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    return FAISS.from_documents(texts, embeddings)


def stream_answer_only(stream_generator):
    for chunk in stream_generator:
        if "answer" in chunk:
            yield chunk["answer"]


st.title("PsyAI")


if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "model" not in st.session_state:
    env.load_dotenv()
    API_KEY = os.getenv("OPENAI_API_KEY")

    st.session_state["model"] = ChatOpenAI(
        api_key=API_KEY, model="gpt-4.1", temperature=0.7
    )

if "embeddings_retriever" not in st.session_state:
    docs = load_docx()
    vector_store = create_docs_ebeddings(docs)
    st.session_state["embeddings_retriever"] = vector_store.as_retriever()


for role, content in st.session_state["messages"]:
    with st.chat_message(role):
        st.markdown(content)


if prompt := st.chat_input("Do que você precisa?"):
    st.session_state["messages"].append(("user", prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        llm: ChatOpenAI = st.session_state["model"]
        chat_template = ChatPromptTemplate(
            [("system", PSY_AI_PROMPT), *st.session_state["messages"]]
        )

        awnser_chain = create_stuff_documents_chain(llm, chat_template)

        retrieval_chain = create_retrieval_chain(
            st.session_state["embeddings_retriever"], awnser_chain
        )

        stream = retrieval_chain.stream({"input": prompt})
        response = st.write_stream(stream_answer_only(stream))

    st.session_state["messages"].append(("assistant", response))
