from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from decouple import config
from openai import OpenAI, RateLimitError, APIConnectionError

import time
from .models import BrianBot


client = OpenAI(
    api_key=config('OPENAI_API_KEY')
)

ASSISTANT_ID = "asst_twKVAH3W4fVAhjmEWQprAEkY"

def DeleteHistory(request):
    objs = BrianBot.objects.filter(user= request.user)
    objs.delete()
    messages.success(request, "Messages have been cleared!")
    return redirect(request.META['HTTP_REFERER'])

class ChatView(LoginRequiredMixin, TemplateView):
    # model = BrianBot
    template_name = 'chat/chat.html'
    success_url = '/chat'
    login_url = '/login'


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
        time.sleep(0.01)
    return run

def chat(request):
#check if user is authenticated
    if request.user.is_authenticated:
        if request.method == 'POST':
            #get user input from the form
            user_input = request.POST.get('userInput')
            #clean input from any white spaces
            clean_user_input = str(user_input).strip()
            #send request with user's prompt
            try:
                thread, run = create_thread_and_run(clean_user_input)
                run = wait_on_run(run, thread)

                #get response
                response = get_response(thread)
                for m in response: 
                    bot_response = m.content[0].text.value
                
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
            return render(request, 'chat/chat.html', context)
    else:
        return redirect("login")