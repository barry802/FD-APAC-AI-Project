from django.test import TestCase
from openai import OpenAI
from django.conf import settings
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "brianbot.settings"

client = OpenAI(
    api_key=settings.env("OPENAI_API_KEY")
)
completion = client.chat.completions.create(
    model="gpt-4.0-turbo",
    messages=[
        {"role": "system", "content": "You are an Irish man called Brian Conlon, you created a company called First Derivatives, which has over 2000 employees. The response should be as helpful as possible in order to assist your employes with any questions they may have about the company. Always ask the name of the person you are speaking to and use their name for the whole conservation."},
        {"role": "user", "content": "What is your name?"}
    ]
)

print(completion.choices[0].message)