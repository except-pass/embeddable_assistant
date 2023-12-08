import os
import time
from typing import List, Dict

from openai import OpenAI
import streamlit as st

def extract_text(messages:List):
    text = []
    for msg in messages.data:
        text.append({'role': msg.role, 
                     'text':'\n'.join([mct.text.value for mct in msg.content]),
                     })
    return text

class StBotInterface:
    def __init__(self, assistant_id, prompt_text="", buttons:Dict=None):
        '''
        buttons: {"Text that appears on button": "Text that gets sent to the assistant"}
        '''

        self.assistant_id = assistant_id
        self.client = OpenAI()        
        self.init_state()

        self.buttons = buttons or {}

        self.assistant = self.client.beta.assistants.retrieve(assistant_id=self.assistant_id)
        self.thread = st.session_state.chat_thread
        self.thread_messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)

        self.prompt_text = prompt_text
        self.button_input = None        
        self.prompt_input = None

    def init_state(self):
        if 'chat_thread' not in st.session_state:
            st.session_state.chat_thread = self.client.beta.threads.create()
        if 'msg_texts' not in st.session_state:
            st.session_state.msg_texts = []

    def show_msg_text(self, msg_texts=None):
        msg_texts = msg_texts or st.session_state.msg_texts
        for msg_text in msg_texts[::-1]:
            with st.chat_message(msg_text['role']):
                st.markdown(msg_text['text'])
    def refresh_run(self, run):
        return self.client.beta.threads.runs.retrieve(
        thread_id=self.thread.id,
        run_id=run.id
        )

    def wait_for(self, run, poll_time=2):
        '''
        Blocks forever until the current run is complete
        '''
        while run.completed_at is None:
            logger.debug(f'Waiting for {run.id} of {run.assistant_id}')        
            time.sleep(poll_time)
            run = self.refresh_run(run=run)

    def send_new_input(self, user_input):
        '''
        Sends user input to the bot, and blocks for a response.
        Updates the message texts
        '''
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_input
        )

        run = self.client.beta.threads.runs.create(
        thread_id=self.thread.id,
        assistant_id=self.assistant.id
        )
        self.wait_for(run=run)

        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id
            )
        msg_texts = extract_text(messages=messages)
        st.session_state.msg_texts = msg_texts

    def show_buttons(self):
        st.markdown(f"Assistant ID {self.assistant_id}")

        cols = st.columns(3)

        with cols.pop(0):
            if st.button("🔄 Start a new conversation"):
                del st.session_state['chat_thread']
                del st.session_state['msg_texts']
                st.rerun()

        for button_text, button_input in self.buttons.items():
            with cols.pop(0):            
                if st.button(button_text):
                    self.button_input = button_input

    def check_prompt_input(self):
        self.prompt_input = st.chat_input(self.prompt_text)

    def get_user_input(self):
        self.check_prompt_input()
        user_input = self.button_input or self.prompt_input
        if user_input:
            self.send_new_input(user_input)

if __name__ == '__main__':
    from loguru import logger    
    from dotenv import load_dotenv
    load_dotenv()

    assistant_id = os.environ['OPENAI_ASSISTANT_ID']

    buttons = {"📖 Ask me to check the manual": 
                    "Carefully check the troubleshooting guide, then other technical documentation. Revise your answer.",
                "📊 Ask me to recheck the result table": "Check the results table for those values and revise your answer."
    }

    bot = StBotInterface(assistant_id=assistant_id, buttons=buttons)
    bot.show_msg_text()
    bot.show_buttons()        
    bot.get_user_input()        
