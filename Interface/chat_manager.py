import json
from langchain.schema.messages import HumanMessage, AIMessage, SystemMessage #https://api.python.langchain.com/en/latest/messages/langchain_core.messages.human.HumanMessage.html
from datetime import datetime

#list comprehension 
#creating a list of the messages from the chat
#saving the list as a chat session
def save_chat_history_json(chat_history, file_path):
    with open(file_path, "w") as f:
        json_data = [message if isinstance(message, dict) else message.dict() for message in chat_history]

        json.dump(json_data, f) #speichern der liste

  

from langchain.schema import HumanMessage, AIMessage, SystemMessage

def load_chat_history_json(file_path):
    with open(file_path, "r") as f:
        json_data = json.load(f)
        messages = []
        for message in json_data:
            msg_type = message.get("type")
            if msg_type == "human":
                messages.append(HumanMessage(**message))
            elif msg_type == "ai":
                messages.append(AIMessage(**message))
            elif msg_type == "system":
                messages.append(SystemMessage(**message))
            else:
                # Ignoriere ungültige Einträge oder logge eine Warnung
                print(f"Unknown message type in history: {msg_type}")
        
        return messages


#session_state managment
def get_timestamp():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S") #Year Month Day Hour Minute Second