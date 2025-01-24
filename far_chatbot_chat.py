import os
from langchain_openai import AzureChatOpenAI
import logging

# Production
from flaskapp.far_chatbot_parser import FarChatbotParser
# Development
# from far_chatbot_parser import FarChatbotParser

llm = AzureChatOpenAI(
        deployment_name=os.environ['OPENAI_GPT_MODEL'],
        openai_api_version=os.environ['OPENAI_VERSION'],
        openai_api_key=os.environ['OPENAI_API_KEY'],
        azure_endpoint=os.environ['OPENAI_BASE'],
        openai_organization=os.environ['OPENAI_ORGANIZATION']
    )

# This class is responsible for handling a session with ChatGPT
class FarChatbotChat:
    # Create a logger
    logger = logging.getLogger('far_chatbot_chat')

    # Set the level of this logger. This level acts as a threshold.
    # Any message below this level will be ignored
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    handler = logging.FileHandler('logs/far_chatbot_chat.log')

    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    def far_chatbot_ask (self, question, thread_id = ''):
        """
        This function is responsible for chatting with the AI about FAR activity.
        :param question:
        :param thread_id:
        :return:
        """
        try:
            return FarChatbotParser().chat(question, thread_id)
        except Exception as e:
            raise e
