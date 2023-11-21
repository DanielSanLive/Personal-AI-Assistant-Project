Set up steps 

import dependencies using pip or pip3
pip install speechrecognition
pip install pyttsx3
pip install wikipedia
pip install wolframalpha
pip install pygame
pip install openai

pip install ipython google-cloud-texttospeech

Our AI Assistant can also query openAI's GPT to speak results for us
to try it for yourself

first, install openAI with this command
pip install openai

also, install dotenv to load our openAI API key from an environment file
pip install python-dotenv

Create an openai account and get an API key, you will also need to acquire your organisation key
https://openai.com/api/

in your project folder, create a .env file and add
OPENAI_API_KEY
OPENAI_ORG

Create your method to query openAI API, similar to what was used in the main.py file