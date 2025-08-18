import json
from langchain.schema.messages import HumanMessage, AIMessage, SystemMessage #https://api.python.langchain.com/en/latest/messages/langchain_core.messages.human.HumanMessage.html
from datetime import datetime
import re
import streamlit as st

#list comprehension 
#creating a list of the messages from the chat
#saving the list as a chat session
def save_chat_history_json(chat_history, file_path):
    with open(file_path, "w") as f:
        json_data = []
        for message in chat_history:
            if isinstance(message, HumanMessage):
                json_data.append({"type": "human", "content": message.content})
            elif isinstance(message, AIMessage):
                json_data.append({"type": "ai", "content": message.content})
            elif isinstance(message, SystemMessage):
                json_data.append({"type": "system", "content": message.content})
            else:
                print(f"Unknown message type, skipping: {message}")
        json.dump(json_data, f, indent=2)

        # json_data = [message if isinstance(message, dict) else message.dict() for message in chat_history]

        # json.dump(json_data, f) #speichern der liste

  

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
    return datetime.now().strftime("%Y_%m_%d_%H_%M") #Year Month Day Hour Minute Second



def next_prompt_recommendation(chat_history, ask_gpt35_func, system_prompt):
    # Chatverlauf textuell zusammenfassen 
    chat_history_text = ""
    for m in chat_history.messages[-6:]: #nur letzten 6 Nachrichten
        #chat_history_text += f"{m.role}: {m.content}\n"
        role = getattr(m, "type", "unknown")
        chat_history_text += f"{role}: {m.content}\n"


    next_steps_prompt = f"""

    {chat_history_text}

    Please analyze the previous dialogue and any provided system model (e.g., DFD) to determine:
    - Whether important security-relevant information is missing for a thorough STRIDE threat modeling.
    - What specific additional data could make the analysis more complete.
    - What logical next steps or follow-up questions could be taken.

    Your tasks (strict output format required):

    1. Answer the user’s question or fulfill their request on the IT security topic, clearly pointing out any gaps or missing details that prevent a complete and accurate STRIDE threat modeling. The answer must be factually relevant and specific to the provided scenario.
    2. Suggest explicitly which additional details, data, or context the user could provide to improve the accuracy and depth of the threat analysis. These suggestions must be concrete and relevant, for example: describe the network topology, provide authentication methods used, specify technologies or frameworks, include user roles, or outline existing security controls.
    3. Propose practical next steps the user can take after receiving your initial analysis, such as specific research actions, further data collection, validation of assumptions, risk assessments, or targeted mitigation planning appropriate to the user’s knowledge level.
    4. Offer ideas for what the user might ask next to deepen or broaden the analysis, including precise follow-up questions about overlooked threat categories, potential attack vectors, system design concerns, or missing STRIDE elements.
    5. Emphasize the importance of completeness and precision in the provided input information and explain why these factors directly affect the quality and usefulness of the STRIDE threat modeling.
    6. Format your response exactly in this numbered order without adding any other bullet point style, headings, or extra commentary. Each numbered point must contain a complete and meaningful sentence or paragraph — no empty items, no placeholders, no unfinished statements.
    7. Do not repeat or reference these instructions in your output.

    Output only the numbered list in the correct order.
    """

    #GPT wird aufgerufen
    next_steps_text = ask_gpt35_func(
        user_input=next_steps_prompt,
        chat_history=chat_history.messages,
        system_prompt=system_prompt
    )

    #Die Optionen werden extrahiert (Regex)
    #option_lines sind die Auswahlmöglichkeiten
    #feedback_question ist nur der Titel über diesen Optionen
    option_lines = re.findall(r"^\d+\.\s*(.*)$", next_steps_text, re.MULTILINE)
    feedback_question = next_steps_text.split("\n")[-1].strip()

    return option_lines, feedback_question
