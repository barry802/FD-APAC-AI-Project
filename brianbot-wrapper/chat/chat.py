from openai import OpenAI, APIConnectionError, RateLimitError
from decouple import config
# from django.shortcuts import render, redirect
# from django.http import HttpResponse
from django.contrib import messages
import time

# from .models import BrianBot


client = OpenAI(
    api_key=config('OPENAI_API_KEY')
)

ASSISTANT_ID = "asst_twKVAH3W4fVAhjmEWQprAEkY"
# ASSISTANT_ID = assistant.id

def submit_messages(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    run = submit_messages(ASSISTANT_ID, thread, user_input)
    return thread, run


# Pretty printing helper
def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()


# Waiting in a loop
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


# File Management
## Create vector to store files
vector_store = client.beta.vector_stores.create(name="HR Policies")

## Ready the files for upload to OpenAI
file_paths = ["HR_docs/Travel_Expenses_Policy.txt"]
file_streams = [open(path, "rb") for path in file_paths]

## Use the upload and poll SDK helper to upload the files, add them to the vector store,
## and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)    

### You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)

# Update Assistant
assistant = client.beta.assistants.update(
    ASSISTANT_ID,
    tools=[{"type": "file_search"}],
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
)

def chat():        
    try:   
        while True: 
            user_input = input("user: ")
            if user_input.lower() in ["quit", "exit", "bye"]:
                break
            # Running threads
            thread1, run1 = create_thread_and_run(user_input)
            # Wait for Run 1
            run1 = wait_on_run(run1, thread1)
            pretty_print(get_response(thread1))
    
        print("assistant: Have a good day! Goodbye")
    
    except APIConnectionError as e:
        #Handle connection error here
        messages.warning(request, "Failed to connect to OpenAI API, check your internet connection")

    except RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
        messages.warning(request, "You exceeded your current quota, please check your plan and billing details.")
        messages.warning(request, "If you are a developper change the API Key")

chat()