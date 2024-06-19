from django.test import TestCase
from openai import OpenAI
from decouple import config

client = OpenAI(
    api_key=config('OPENAI_API_KEY')
)

## Create HR Assistant
# assistant = client.beta.assistants.create(
#     name="Brian Bot",
#     instructions="You are an Irish man named Brian Conlon, you created a company called First Derivatives, which has over 2000 employees. The response should be as helpful as possible in order to assist your employes with any questions they may have about the company.",
#     model="gpt-4-turbo",
#     tools=[{"type": "file_search"}],
# )

ASSISTANT_ID = "asst_twKVAH3W4fVAhjmEWQprAEkY"

# Testing API Calls
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="What is you name?"
)

## Runs
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=ASSISTANT_ID,
    instructions="Always ask the name of the person you are speaking to and use their name for the whole conservation. They are a First Derivatives employee."
)

if run.status == 'completed':
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    print(messages)
else: 
    print(run.status)





## File Search
vector_store = client.beta.vector_stores.create(name="HR Documents")
file_paths = ["HR_docs/Global_Travel_Policy.txt", "HR_docs/Travel_Expenses_Policy.txt"]
file_streams = [open(path, "rb") for path in file_paths]

file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)    

print(file_batch.status)
print(file_batch.file_counts)