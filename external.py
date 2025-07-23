import os
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import Docx2txtLoader


def load_docx() -> List[Document]:
    documents = []

    for file_path in os.listdir("./docs"):
        loader = Docx2txtLoader(f"./docs/{file_path}")
        documents.extend(loader.load())

    return documents
