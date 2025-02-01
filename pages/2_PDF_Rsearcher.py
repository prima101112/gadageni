import streamlit as st
import time
import threading
from common import api_interaction
from langchain_community.document_loaders import PyPDFLoader
from common import pdfrag
import os

st.set_page_config(
    page_title="Just Chat with pdf",
    page_icon="👋",
)

st.title("AI Chat search in pdf's")
st.markdown("Chat with OpenAI")

@st.cache_resource
def initialize_qa_chain():
    return None

def submitPDF():
    with st.form(key="PDF_Researcher"):
        allcvs = st.file_uploader(label="insert all cv's", accept_multiple_files=True)
        submit_button = st.form_submit_button(label="Analyze")

    qa_chain = initialize_qa_chain()

    if submit_button and allcvs:
        temp_dir = "pdfs"
        vectorstore = None
        for uploaded_file in allcvs:
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_file.getvalue())
            
            st.write("filename:", uploaded_file.name)
            
            documents = pdfrag.load_pdf(temp_file_path)
            chunks = pdfrag.split_text(documents)
            
            vectorstore = pdfrag.create_or_update_vectorstore(chunks, existing_vectorstore=vectorstore)

        qa_chain = pdfrag.build_rag(vectorstore)
        
    return qa_chain

def chat_interface(qa_chain):
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.creation_time = time.time()

    def clear_memory():
        st.session_state.messages = []
        st.session_state.creation_time = time.time()
            
    def auto_clear_memory():
        time.sleep(420)
        clear_memory()

    threading.Thread(target=auto_clear_memory, daemon=True).start()

    st.session_state.messages.sort(key=lambda x: x.get('timestamp', 0))

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": time.time()})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Thinking..."):
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
            full_message = "with previous conversation : " + context + "\n\n answer this : " + user_input + ""
            print(full_message)
            
            if qa_chain and hasattr(qa_chain, 'invoke'):
                bot_response = qa_chain.invoke(full_message)
            else:
                # If qa_chain is empty or doesn't have invoke method, use direct LLM call
                bot_response = api_interaction.getAIResponse("OpenAI", context, user_input)
            
        st.session_state.messages.append({"role": "assistant", "content": bot_response, "timestamp": time.time()})
        with st.chat_message("assistant"):
            st.markdown(bot_response)

    if time.time() - st.session_state.creation_time > 420:
        clear_memory()

if 'qa_chain' not in st.session_state:
    st.session_state.qa_chain = None

qa_chain = submitPDF()
if qa_chain:
    st.session_state.qa_chain = qa_chain
chat_interface(st.session_state.qa_chain)
