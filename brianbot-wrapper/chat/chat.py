from openai import OpenAI
from decouple import config
import time


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

# Upload file
file = client.files.create(
    file=open(
        "HR_docs/Travel_Expenses_Policy.txt",
        "rb",
    ),
    purpose="assistants",
)

# Update Assistant
assistant = client.beta.assistants.update(
    ASSISTANT_ID,
    tools=[{"type": "file_search"}]
)


# Running threads
thread1, run1 = create_thread_and_run(input("How can I help you? "))
# Wait for Run 1
run1 = wait_on_run(run1, thread1)
pretty_print(get_response(thread1))
