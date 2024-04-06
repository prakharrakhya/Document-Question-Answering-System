import os
from PyPDF2 import PdfReader 
import pickle
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.llms.huggingface_hub import HuggingFaceHub
#from langchain_community.embeddings import huggingface
from langchain_community.vectorstores import faiss
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer , pipeline
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline


#1 get raw text(list of doc)
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

#2 splitting text to chunk
def get_chunks(raw_text):
    text_splitter = CharacterTextSplitter(
        separator="\n" , 
        chunk_size = 1000,
        chunk_overlap = 200,
        length_function = len 
    )
    chunks = text_splitter.split_text(raw_text)
    return chunks

#3 creating embeddings and vector store (to run things like symentic chunk)
def get_embeddings(chunks):
    #embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
    cwd = os.getcwd()
    #print(cwd)
    with open(cwd + '\models\embedder.pkl' , 'rb') as obj:
        embeddings = pickle.load(obj)
    vectorstore = faiss.FAISS.from_texts(chunks , embedding=embeddings)
    # store vector store as pickle
    return vectorstore

def similarity_search(vector_store:faiss.FAISS , query:str):
    retriever = vector_store.as_retriever()
    retriever.get_relevant_documents(query=query)
    

def get_conversation_chain(vectorstore):
    
    cwd = os.getcwd()
    load_path = cwd+'\models'    
    model = AutoModelForSeq2SeqLM.from_pretrained(load_path)
    tokenizer = AutoTokenizer.from_pretrained(load_path)
    pipe = pipeline("text2text-generation" , model=model , model_kwargs={"temperature":0.5, "max_length":1000000} , tokenizer=tokenizer , max_new_tokens=20)
    hf = HuggingFacePipeline(pipeline=pipe)
    memory = ConversationBufferMemory(memory_key='chat_history' , return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=hf,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

 
def Get_Response(message:str,chatHisotry):
    
    chats = list(chatHisotry)
    chatlist = []
    for k in chats:
        m = {'message':k.message , 'response':k.response}
        chatlist.append(m) 
    chat_history_text = " ".join([entry["message"] + " " + entry["response"] for entry in chatlist])

    pdf_path = [r'D:\projects\resume_PROJECTS\DocChat\test.pdf']
    template = '''
    these are the questions and responces we have already talked about 
    ''' + str(chatlist)
    text = get_pdf_text(pdf_path)
    chunks = get_chunks(text + template)
    vector_store = get_embeddings(chunks)
    chain = get_conversation_chain(vector_store)
    response = chain({'question':message})
    print(response)
    return response['answer']

