from openai import OpenAI, APIConnectionError, RateLimitError
from decouple import config
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import time

from .models import BrianBot


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

def chat(request):        
    if request.user.is_authenticated:
        if request.method == 'POST':
            #get user input from the form
            user_input = request.POST.get('userInput')
            #clean input from any white spaces
            clean_user_input = str(user_input).strip()
            #send request with user's prompt
            try:
                response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                            {
                                "role": "user",
                                "content": clean_user_input,
                            }
                        ],
                    )
                #get response
                
                bot_response = response.choices[0].message.content
                
                obj, created = BrianBot.objects.get_or_create(
                    user=request.user,
                    messageInput=clean_user_input,
                    bot_response=bot_response,
                )    
            except APIConnectionError as e:
                #Handle connection error here
                messages.warning(request, "Failed to connect to OpenAI API, check your internet connection")

            except RateLimitError as e:
                #Handle rate limit error (we recommend using exponential backoff)
                messages.warning(request, "You exceeded your current quota, please check your plan and billing details.")
                messages.warning(request, "If you are a developper change the API Key")
            return redirect(request.META['HTTP_REFERER'])
        else:
            #retrieve all messages belong to logged in user
            get_history = BrianBot.objects.filter(user=request.user)
            context = {'get_history':get_history}
            return render(request, 'index.html', context)
    else:
        return redirect("login")

chat()