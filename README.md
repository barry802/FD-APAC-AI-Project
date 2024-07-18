![Banner](https://i.imgur.com/90jeGwr.png)
# Brian Bot
Your personal HR assistant.

## Description
The project generates a local AI client specifically designed to handle all HR queries for your company. 

## Quickstart
1. Clone the repo 
```
git clone https://github.com/barry802/FD-APAC-AI-Project.git
```
2. Enter the "brianbot-wrapper" directory
```
cd brianbot-wrapper
```
3. Install requirements
```
pip install -r requirements.txt
```
4. Launch the AI instance
```
python manage.py runserver
```
5. Open the hosting link in your browser
(e.g. https://127.0.0.1:8000/)

## Troubleshooting
In some cases the requirements are not installed correctly due to naming conflicts. 
Most common cause is the ```pythn-decouple``` package
### Solution
1. ```pip uninstall decouple```
2. ```pip install python-decouple```
3. Repeat steps 4 & 5 from above quickstart guide

