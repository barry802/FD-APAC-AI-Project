from decouple import config
from openai import OpenAI
from chat import *

client = OpenAI(
    api_key=config('OPENAI_API_KEY')
)

ASSISTANT_ID = "asst_twKVAH3W4fVAhjmEWQprAEkY"

# Upload file
file = client.files.create(
    file=open(
        "HR_docs/Travel_Expense_Policy.txt",
        "rb",
    ),
    purpose="assistants",
)

# Update Assistant
assistant = client.beta.assistants.update(
    ASSISTANT_ID,
    tools=[{"type": "file_search"}]
)

thread, run = chat.create_thread_and_run(input("Q?: "))
