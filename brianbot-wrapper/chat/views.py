from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from decouple import config
from openai import OpenAI, RateLimitError, APIConnectionError
# from .forms import ChatForm
from chat.models import BrianBot


client = OpenAI(
    api_key=config('OPENAI_API_KEY')
)


class ChatView(LoginRequiredMixin, TemplateView):
    # model = BrianBot
    template_name = 'chat/chat.html'
    success_url = '/query/chat'
    login_url = '/login'

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