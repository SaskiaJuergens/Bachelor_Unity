import json
from langchain.schema.messages import HumanMessage, AIMessage #https://api.python.langchain.com/en/latest/messages/langchain_core.messages.human.HumanMessage.html

#list comprehension 
#creating a list of the messages from the chat
#saving the list as a chat session
def save_chat_history_json(chat_history, file_path):
    with open(file_path, "w") as f:
        json_data = [message.dict() for message in chat_history] #list of the messages
        json.dump(json_data, f) #speichern der liste

def load_chat_history_json(file_path):
    with open(file_path, "r") as f:
        json_data = json.load(f)
        messages = [HumanMessage(**message) if message["type"] == "human" else AIMessage(**message) for message in json_data]
        return messages
    