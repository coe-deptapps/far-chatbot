import os
from langchain_openai import AzureChatOpenAI
import logging

from scripts.far_dei_parser import FarDeiParser

llm = AzureChatOpenAI(
        deployment_name=os.environ['OPENAI_GPT_MODEL'],
        openai_api_version=os.environ['OPENAI_VERSION'],
        openai_api_key=os.environ['OPENAI_API_KEY'],
        azure_endpoint=os.environ['OPENAI_BASE'],
        openai_organization=os.environ['OPENAI_ORGANIZATION']
    )

# This class is responsible for handling a session with ChatGPT
class FarDeiChat:
    # Create a logger
    logger = logging.getLogger('far_dei_chat')

    # Set the level of this logger. This level acts as a threshold.
    # Any message below this level will be ignored
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    handler = logging.FileHandler('../logs/far_dei_chat.log')

    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    def far_dei_ask (self, question, thread_id = ''):
        """
        This function is responsible for chatting with the AI about FAR DEI activity.
        :param question:
        :param thread_id:
        :return:
        """
        try:
            return FarDeiParser().chat(question, thread_id)
        except Exception as e:
            raise e
