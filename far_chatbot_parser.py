import os
from dotenv import load_dotenv
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage
import logging
import pymysql
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint import MemorySaver
import redis
import json

# Sets the current working directory to be the same as the file.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load environment file for secrets (development env only!).
try:
    if load_dotenv('.env') is False:
        raise TypeError
except TypeError:
    print('Unable to load .env file.')
    quit()

llm = AzureChatOpenAI(
    deployment_name=os.environ['OPENAI_GPT_MODEL'],
    openai_api_version=os.environ['OPENAI_VERSION'],
    openai_api_key=os.environ['OPENAI_API_KEY'],
    azure_endpoint=os.environ['OPENAI_BASE'],
    openai_organization=os.environ['OPENAI_ORGANIZATION']
)


class FarChatbotParser:
    """
    Take a user question and generate RAG-style answer.
    """
    # Create a logger
    logger = logging.getLogger('far_chatbot_sql_bot')

    # Set the level of this logger. This level acts as a threshold.
    # Any message below this level will be ignored
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    handler = logging.FileHandler('logs/far_chatbot_parser.log')

    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    def __init__(self):
        self.db = None

        # If the APP_ENV is development, use 'localhost' as the redis host, if not, use 'redis'.
        if os.getenv('APP_ENV') == 'development':
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        else:
            self.redis_client = redis.Redis(host='redis', port=6379, db=0)

        self.sql_connect()
        if self.db:
            self.tables = self.db.get_usable_table_names()
        self.conversation_histories = {}  # Stores conversations by thread ID

    def sql_connect(self):
        try:
            # Connect to the database using the environment variables.
            db_conn_str = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_SERVER')}/{os.getenv('DB_NAME')}"
            self.db = SQLDatabase.from_uri(db_conn_str)
            self.logger.info(f"Database connection succeeded! {db_conn_str}")
        except pymysql.OperationalError as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError("Failed to connect to database") from e

    def create_tools(self):
        """
        Create a toolkit to interact with the database.
        """
        toolkit = SQLDatabaseToolkit(db=self.db, llm=llm)
        return toolkit.get_tools()

    def get_or_create_conversation(self, thread_id):
        history = self.redis_client.get(thread_id)
        if history is None:
            return []
        return json.loads(history)

    def save_conversation(self, thread_id, conversation_history):
        self.redis_client.set(thread_id, json.dumps(conversation_history))

    def construct_prompt(self, conversation_history, retrieved_data):
        """
        After the retrieval step, construct an additional prompt based on the user's query, the conversation so far, and the retrieved data for the new question.
        :param conversation_history:
        :param retrieved_data:
        :return:
        """
        context = (f"Conversation history: {conversation_history}\nRetrieved Data: {retrieved_data}."
                   f"\nBased on the retrieved data and the conversation history, generate a comprehensive response."
                   f"\nKeep in mind that you are responding to questions about faculty service data in Faculty Activity Reports (FAR) for the University of Michigan."
                   f"\nIf you believe the user's question is not related to faculty service, do not answer it. Please inform them and ask them to rephrase it.")
        return context

    def chat(self, question, thread_id=''):
        """
        Chat with the AI to generate answers to questions based on the data available in the FAR database.
        :param question: The question to ask the AI.
        :param thread_id: The thread ID for the conversation.
        """
        try:
            tools = self.create_tools()

            SQL_PREFIX = """You are an agent designed to interact with a SQL database that stores Faculty Activity Reports (FAR) data for the University of Michigan.
                        Specifically, you are answering questions related to faculty service data.
                        If the question is not related to faculty service (even if it is related to the FAR database generally), do not continue except to tell the user that you are unable to answer the question and ask them to rephrase it so that it is related to faculty service data.
                        
                        If the question is faculty service related, continue following the instructions.
                        Given an input question, create a syntactically correct SQL query to run, then look at the results of the query and return the answer.
                        Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
                        You can order the results by a relevant column to return the most interesting examples in the database.
                        Never query for all the columns from a specific table, only ask for the relevant columns given the question.
                        You have access to tools for interacting with the database.
                        Only use the below tools. Only use the information returned by the below tools to construct your final answer.
                        You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

                        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

                        To start you should ALWAYS look at the tables in the database to see what you can query.
                        Do NOT skip this step.
                        Then you should query the schema of the most relevant tables. The table you will want to focus on most is 'far_snapshot_service_positions'.

                        If you are asked about department-specific questions, you can look up the name of and the department ID for the department in the departments table.
                        Most tables have a farID foreign key. You can use that column to join on far.far, which has the deptID field. Departments will usually be referred to by their acronym (e.g. CSE, BME, AERO, etc.), but you can look up the full name in the departments table.
                        
                        Answers should always return the name of the department, even if the user asked the question in terms of the department ID.
                        """

            if thread_id == '':
                # Randomly generate a thread id if one is not provided
                thread_id = f"{os.urandom(16).hex()}"

            conversation_history = self.get_or_create_conversation(thread_id)
            conversation_history.append(("user", question))
            conversation = {"messages": conversation_history}

            self.logger.debug(f"Asking question: {question}")

            system_message = SystemMessage(content=SQL_PREFIX)
            # Create a React agent to interact with the database
            graph = create_react_agent(llm, tools, messages_modifier=system_message, checkpointer=MemorySaver())
            config = {
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 50 # default is 25
            }

            # Step 1: Retrieve Data (the "R" in RAG)
            retrieved_data = ""
            try:
                for s in graph.stream(conversation, config, stream_mode="values"):
                    message = s["messages"][-1]
                    self.logger.debug(f"Graph Message: {message}")
                    if isinstance(message, tuple):
                        retrieved_data = message
                    else:
                        retrieved_data = message.content

            except Exception as e:
                self.logger.error(f"An error occurred while retrieving data: {str(e)}")
                raise


            self.logger.debug(f"Retrieved SQL data: {retrieved_data}")

            # Step 2: Construct a contextual prompt with the retrieved data (the "A" in RAG)
            final_prompt = self.construct_prompt(conversation_history, retrieved_data)

            # Step 3: Generate the response using the contextual prompt (the "G" in RAG)
            system_message = SystemMessage(content=final_prompt)
            response = llm.generate(messages=[[system_message]])

            generated_answer = response.generations[0][0].text.strip()
            conversation_history.append(("ai", generated_answer))

            # Save updated conversation history
            self.save_conversation(thread_id, conversation_history)
            self.logger.debug(f"Generated answer: {generated_answer}")

            return {'answer': generated_answer, 'thread_id': thread_id}

        except Exception as e:
            self.logger.error(f"An error occurred in the chat method: {str(e)}")
            raise e
