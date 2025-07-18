from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()


client = OpenAI(api_key="")

def ask_gpt35(user_input, chat_history, system_prompt=""):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content


