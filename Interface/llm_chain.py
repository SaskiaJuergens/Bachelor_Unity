from prompt_templates import memory_prompt_template
from langchain.chains import LLMChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.llms import CTransformers
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
import chromadb
import yaml
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
config = {
    "openai_api_key": "",
    "chat_history_path": "chat_session/"
}

client = OpenAI(api_key=config["openai_api_key"])

def create_chat_memory(chat_history):
    return ConversationBufferWindowMemory(memory_key="history", chat_memory=chat_history, k=3)

def create_prompt_from_template(template):
    return PromptTemplate.from_template(template)

def create_llm_chain(llm, chat_prompt, memory):
    return LLMChain(llm=llm, prompt=chat_prompt, memory=memory)

def load_normal_chain(chat_history):
    return chatChain(chat_history)


class chatChain:
    def __init__(self, chat_history, model_name="gpt-3.5-turbo"): 
        self.memory = create_chat_memory(chat_history)

        prompt = memory_prompt_template
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1500,
            openai_api_key=config["openai_api_key"] 
        )
        
        chat_prompt = create_prompt_from_template(memory_prompt_template)
        self.llm_chain = create_llm_chain(llm, chat_prompt, self.memory)

    def run(self, user_input):
        return self.llm_chain.run(human_input=user_input, history=self.memory.chat_memory.messages, stop="Human:")
    

def ask_gpt35(user_input, chat_history, system_prompt=""):
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    # Umwandlung der Chatverlauf-Nachrichten
    for msg in chat_history:
        if isinstance(msg, dict):
            # Falls es bereits ein dict ist
            role = msg.get("role", "").lower()
            if role == "human":
                role = "user"
            elif role == "ai":
                role = "assistant"
            if role in ["user", "assistant", "system"]:
                messages.append({"role": role, "content": msg["content"]})
        elif hasattr(msg, "type") and hasattr(msg, "content"):
            # Falls es LangChain-Objekte wie HumanMessage oder AIMessage sind
            role = msg.type.lower()
            if role == "human":
                role = "user"
            elif role == "ai":
                role = "assistant"
            messages.append({"role": role, "content": msg.content})
        else:
            print("Unknow message format:", msg)

    # Benutzer-Eingabe als letzter Schritt
    messages.append({"role": "user", "content": user_input})

    # OpenAI Aufruf
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content
