import os
import dotenv as env
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from prompts import PSY_AI_PROMPT


st.title("PsyAI")


if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "model" not in st.session_state:
    env.load_dotenv()
    API_KEY = os.getenv("OPENAI_API_KEY")

    st.session_state["model"] = ChatOpenAI(
        api_key=API_KEY, model="gpt-4.1-nano", temperature=0.7
    )


for role, content in st.session_state["messages"]:
    with st.chat_message(role):
        st.markdown(content)


if prompt := st.chat_input("Do que você precisa?"):
    st.session_state["messages"].append(("user", prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        llm: ChatOpenAI = st.session_state["model"]
        prompt = ChatPromptTemplate(
            [("system", PSY_AI_PROMPT), *st.session_state["messages"]]
        )
        stream = llm.stream(input=prompt.format_messages())
        response = st.write_stream(stream)

    st.session_state["messages"].append(("assistant", response))
