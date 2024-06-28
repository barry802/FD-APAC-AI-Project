from django.http import HttpResponse
from datetime import datetime
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib import messages

from .forms import SignupForm, UserLoginForm

class SignupView(CreateView):
    form_class = SignupForm
    template_name = "home/register.html"
    def form_valid(self, form):
        response = super().form_valid(form)
        # Get the user's username and password in order to automatically authenticate user after registration
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        # Authenticate the user and log him/her in
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return response
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.warning(self.request, f"{field}: {error}")
        return redirect(self.request.META['HTTP_REFERER'])
    def get_success_url(self):
        return reverse("home")

class LogoutInterfaceView(LogoutView):
    template_name = 'home/logout.html'

class LoginInterfaceView(FormView):
    form_class = UserLoginForm
    template_name = 'home/login.html'
    def form_valid(self, form):
        response = super().form_valid(form)
        # Get the user's username and password and authenticate
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        # Authenticate the user and log him/her in
        user = authenticate(username=username, password=password)
        login(self.request, user)
        messages.success(self.request, "You are logged in")
        return response
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.warning(self.request, f"{error}")
        return redirect(self.request.META['HTTP_REFERER'])
    def get_success_url(self):
        return reverse("home")

class HomeView(TemplateView):
    template_name = 'home/welcome.html' 
    extra_context = {'today': datetime.today()}

class AuthorizedView(LoginRequiredMixin, TemplateView):
    template_name = 'home/authorized.html'
    login_url = '/admin'
