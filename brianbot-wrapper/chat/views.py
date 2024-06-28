from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# from .forms import ChatForm
from .models import Chat

class ChatView(LoginRequiredMixin, TemplateView):
    model = Chat
    template_name = 'chat/chat.html'
    success_url = '/query/chat'
    login_url = '/login'