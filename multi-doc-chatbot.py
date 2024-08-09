import os
import sys
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
import streamlit as st
from htmlTemplates import css, bot_template, user_template

st.set_page_config(page_title="Customer service",
                       page_icon="🤖")

col1, col2, col3 = st.columns(3)

#Sorry about the code being untidy. its a mix of a few github repositories and I havent had time to tidy it up.

#To begin the conversation the button must be clicked, as this will clear the history of the previous conversation, preventing bugs.


def click_button():
    with open('chathistory.txt', 'r+') as f:
        f.truncate(0)
    


st.write(css, unsafe_allow_html=True)
with col2:
    st.header("Customer service ")
query = st.text_input("Your question:")

st.markdown(
    """
<style>
button {
    height: 100px;
    padding-top: 10px !important;
    padding-bottom: 10px !important;
}
</style>
""",
    unsafe_allow_html=True,
)
with col2:
    st.button('Begin conversation', on_click=click_button)  





def displayconvo(history, i = 0):
    for msg in history:
        i += 1
        if i % 2 != 0:
            st.write(user_template.replace(
                "{{MSG}}", msg), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", msg), unsafe_allow_html=True)
            

     


print("test")
load_dotenv('.env')
documents = []
# Create a List of Documents from all of our files in the ./docs folder
for file in os.listdir("docs"):
    if file.endswith(".pdf"):
        pdf_path = "./docs/" + file
        loader = PyPDFLoader(pdf_path)
        documents.extend(loader.load())
    elif file.endswith('.docx') or file.endswith('.doc'):
        doc_path = "./docs/" + file
        loader = Docx2txtLoader(doc_path)
        documents.extend(loader.load())
    elif file.endswith('.txt'):
        text_path = "./docs/" + file
        loader = TextLoader(text_path)
        documents.extend(loader.load())

# Split the documents into smaller chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
documents = text_splitter.split_documents(documents)

# Convert the document chunks to embedding and save them to the vector store
vectordb = Chroma.from_documents(documents, embedding=OpenAIEmbeddings(), persist_directory="./data")
vectordb.persist()

# create our Q&A chain
pdf_qa = ConversationalRetrievalChain.from_llm(
    ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo'),
    retriever=vectordb.as_retriever(search_kwargs={'k': 6}),
    return_source_documents=True,
    verbose=False
)

yellow = "\033[0;33m"
green = "\033[0;32m"
white = "\033[0;39m"

chat_history = []

pastquery = None

history = []
while True:
    if pastquery != query and query != "":
        f = open('chathistory.txt','a')
        f.write(query+"\n")
        
        
        
        if query == "exit" or query == "quit" or query == "q" or query == "f":
            print('Exiting')
            sys.exit()
        if query == '':
            continue
        result = pdf_qa.invoke(
            {"question": query, "chat_history": chat_history})
        print(f"{white}Answer: " + result["answer"])
        chat_history.append((query, result["answer"]))
        
        f.write(result["answer"]+"\n")
        f.close()
        
        f = open('chathistory.txt','r')
        history = f.readlines()
        displayconvo(history)
        pastquery = query