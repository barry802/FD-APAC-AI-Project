from django.urls import path

from . import views

urlpatterns = [
    path('', views.chat, name="chat"),
    path('clear', views.DeleteHistory, name="clear"),
]