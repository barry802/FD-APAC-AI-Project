from django.test import TestCase
from decouple import config
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import ToolCall, ToolCallDelta
from openai.types.beta.threads import Message, MessageDelta
from openai.types.beta.threads.runs import ToolCall, RunStep
from openai.types.beta import AssistantStreamEvent

import time
import json
import uuid
import traceback



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


class EventHandler(AssistantEventHandler):
   def __init__(self, thread_id, assistant_id):
       super().__init__()
       self.output = None
       self.tool_id = None
       self.thread_id = thread_id
       self.assistant_id = assistant_id
       self.run_id = None
       self.run_step = None
       self.function_name = ""
       self.arguments = ""
      
   @override
   def on_text_created(self, text) -> None:
       print(f"\nassistant on_text_created > ", end="", flush=True)

   @override
   def on_text_delta(self, delta, snapshot):
       # print(f"\nassistant on_text_delta > {delta.value}", end="", flush=True)
       print(f"{delta.value}")

   @override
   def on_end(self, ):
       print(f"\n end assistant > ",self.current_run_step_snapshot, end="", flush=True)

   @override
   def on_exception(self, exception: Exception) -> None:
       """Fired whenever an exception happens during streaming"""
       print(f"\nassistant > {exception}\n", end="", flush=True)

   @override
   def on_message_created(self, message: Message) -> None:
       print(f"\nassistant on_message_created > {message}\n", end="", flush=True)

   @override
   def on_message_done(self, message: Message) -> None:
       print(f"\nassistant on_message_done > {message}\n", end="", flush=True)

   @override
   def on_message_delta(self, delta: MessageDelta, snapshot: Message) -> None:
       # print(f"\nassistant on_message_delta > {delta}\n", end="", flush=True)
       pass

   def on_tool_call_created(self, tool_call):
       # 4
       print(f"\nassistant on_tool_call_created > {tool_call}")
       self.function_name = tool_call.function.name       
       self.tool_id = tool_call.id
       print(f"\on_tool_call_created > run_step.status > {self.run_step.status}")
      
       print(f"\nassistant > {tool_call.type} {self.function_name}\n", flush=True)

       keep_retrieving_run = client.beta.threads.runs.retrieve(
           thread_id=self.thread_id,
           run_id=self.run_id
       )

       while keep_retrieving_run.status in ["queued", "in_progress"]: 
           keep_retrieving_run = client.beta.threads.runs.retrieve(
               thread_id=self.thread_id,
               run_id=self.run_id
           )
          
           print(f"\nSTATUS: {keep_retrieving_run.status}")      
      
   @override
   def on_tool_call_done(self, tool_call: ToolCall) -> None:       
       keep_retrieving_run = client.beta.threads.runs.retrieve(
           thread_id=self.thread_id,
           run_id=self.run_id
       )
      
       print(f"\nDONE STATUS: {keep_retrieving_run.status}")
      
       if keep_retrieving_run.status == "completed":
           all_messages = client.beta.threads.messages.list(
               thread_id=current_thread.id
           )

           print(all_messages.data[0].content[0].text.value, "", "")
           return
      
       elif keep_retrieving_run.status == "requires_action":
           print("here you would call your function")

      
   @override
   def on_run_step_created(self, run_step: RunStep) -> None:
       # 2       
       print(f"on_run_step_created")
       self.run_id = run_step.run_id
       self.run_step = run_step
       print("The type ofrun_step run step is ", type(run_step), flush=True)
       print(f"\n run step created assistant > {run_step}\n", flush=True)

   @override
   def on_run_step_done(self, run_step: RunStep) -> None:
       print(f"\n run step done assistant > {run_step}\n", flush=True)

   def on_tool_call_delta(self, delta, snapshot): 
       if delta.type == 'function':
           # the arguments stream thorugh here and then you get the requires action event
           print(delta.function.arguments, end="", flush=True)
           self.arguments += delta.function.arguments
       elif delta.type == 'code_interpreter':
           print(f"on_tool_call_delta > code_interpreter")
           if delta.code_interpreter.input:
               print(delta.code_interpreter.input, end="", flush=True)
           if delta.code_interpreter.outputs:
               print(f"\n\noutput >", flush=True)
               for output in delta.code_interpreter.outputs:
                   if output.type == "logs":
                       print(f"\n{output.logs}", flush=True)
       else:
           print("ELSE")
           print(delta, end="", flush=True)

   @override
   def on_event(self, event: AssistantStreamEvent) -> None:
       # print("In on_event of event is ", event.event, flush=True)

       if event.event == "thread.run.requires_action":
           print("\nthread.run.requires_action > submit tool call")
           print(f"ARGS: {self.arguments}")

def submit_messages(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant_id,
        event_handler=EventHandler(thread.id, ASSISTANT_ID),
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
        time.sleep(0.01)
    return run

new_thread = client.beta.threads.create()
prompt = "What is your name?" 
client.beta.threads.messages.create(thread_id=new_thread.id, role="user", content=prompt)

with client.beta.threads.runs.stream(
    thread_id=new_thread.id,
    assistant_id=ASSISTANT_ID,
    instructions=prompt,
    event_handler=EventHandler(new_thread.id, ASSISTANT_ID),
) as stream:
    stream.until_done()