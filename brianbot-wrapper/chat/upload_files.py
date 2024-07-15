from openai import OpenAI
from decouple import config
# import os

client = OpenAI(
    api_key=config('OPENAI_API_KEY')
)

ASSISTANT_ID = "asst_twKVAH3W4fVAhjmEWQprAEkY"
# ASSISTANT_ID = assistant.id

# File Management
## Create vector to store files
vector_store = client.beta.vector_stores.create(name="HR Policies")

## Ready the files for upload to OpenAI
file_paths = ["HR_docs/Travel Expense Policy.pdf",
              "HR_docs/Furlough Policy.pdf",
              "HR_docs/Global Travel Policy.pdf",
              "HR_docs/Joiners Policy.pdf",
              "HR_docs/Workplace Drug & Alcohol Policy.pdf"]
file_streams = [open(str(path), "rb") for path in file_paths]

## Use the upload and poll SDK helper to upload the files, add them to the vector store,
## and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)    

# ### You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)

## Update assistant
assistant = client.beta.assistants.update(
    ASSISTANT_ID,
    tools=[{"type": "file_search"}],
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
)

