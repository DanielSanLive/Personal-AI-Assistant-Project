# Hello! Welcome to the AI Assisntant project by Daniel Jones
# for more information, please read the readme file, available in my GitHub portfolio repository

from datetime import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha
import keyboard
import math

# Google TTS
import google.cloud.texttospeech as tts
import pygame
import time

# OpenAI GPT-4
from openai import OpenAI

# Credentials
import os
from dotenv import load_dotenv
load_dotenv()

# Mute ALSA errors...
from ctypes import *
from contextlib import contextmanager

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    try: 
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        print('')

# Parameters
tts_type = 'google' # google or local
activationWords = ['computer', 'assistant']

# Browser Configuration
# Setting the path
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
firefox_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
webbrowser.register('firefox', None, webbrowser.BackgroundBrowser(firefox_path))

# Wolfram Alpha Client
appId = '4KW3WX-WLL4L88VVH'
wolframClient = wolframalpha.Client(appId)

# Local Speech engine initialization
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) # 0 = Male, # 1 = Female

# Google TTS Client
def google_text_to_wav(voice_name: str, text: str):
    language_code = "-".join(voice_name.split("-")[:2])

    # Set the text input to be synthesized
    text_input = tts.SynthesisInput(text=text)

    # Build the voice request, select the language code (en-US) and the voice
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )

    # Select the type of audio file you want returned
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input, voice=voice_params, audio_config=audio_config
    )

    return response.audio_content


# Defining commands for the computer to recognize when I use my voice, using Google's API.
def parseCommand():
    with noalsaerr():
        listener = sr.Recognizer()
        print('Listening for a command')
       

    with sr.Microphone() as source:
        listener.pause_threshold = 2
        input_speech = listener.listen(source)

    try: 
        print('Recognizing speech...')
        query = listener.recognize_google(input_speech, language='en_gb')  
        print(f'The input speech was: {query}') 
    except Exception as exception:
        print('I did not quite catch that')
        speak('I did not quite catch that')
        print(exception)
        return 'none'
    
    return(query)

def speak(text, rate=120):
    time.sleep(0.3)
    try:
        if tts_type == 'local':
            engine.setProperty('rate', rate)
            engine.say(text)
            engine.runAndWait()
        elif tts_type == 'google':
            speech = google_text_to_wav('en-US-Neural2-C', text)
            pygame.mixer.init(frequency=12000, buffer=4096)
            speech_sound = pygame.mixer.Sound(speech)
            
            pygame.mixer.Channel(0).play(speech_sound)
            speech_length = speech_sound.get_length()  # Calculate speech length
            pygame.mixer.Channel(0).get_busy()
            pygame.time.wait(int(speech_length * 1000))  # Wait for speech to finish
            
            pygame.mixer.quit()

    ## Standard keyboard interrupt is Ctrl=C. This interupts Google's speech synthesis.        
    except KeyboardInterrupt:
        try:
            if tts_type == 'google':
                pygame.mixer.quit()
        except:
            pass
        return
  

def search_wikipedia(query = ''):
    searchResults = wikipedia.search(query)
    if not searchResults:
        print('No wikipedia result')
        return 'No results found.'
    try:
        wikiPage = wikipedia.page(searchResults[0])
    except wikipedia.DisambiguationError as error:
        wikiPage = wikipedia.page(error.options[0])
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary)
    return wikiSummary  

def listOrDict(var):
     if isinstance(var, list):
         return var[0]['plaintext']
     else:
         return var['plaintext']

def search_wolframAlpha(query = ''):
    response = wolframClient.query(query)

    # @success: wolfram Alpha was able to resolve the query
    # @numpods: Number of results returned
    # pod: List of results. This can also contain subpods
    if response['@success'] == 'false':
        return 'Could not compute'
    
    # Query resolved
    else:
        result = ''
        # Question
        pod0 = response['pod'][0]
        pod1 = response['pod'][1]
        # may contain the answer, has the highest confidence value
        # if it's primary, or has the title of result or definition, then its the official result
        if (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
         result = listOrDict(pod1['subpod'])
         #remove the bracketed sections
         return result.split('(')[0]
        else:
         question = listOrDict(pod0['subpod'])
         # remove the bracketed sections
         return question.split('(')[0]

client = OpenAI()

def query_openai(prompt = ""):
    client.organization=os.environ['OPENAI_ORG']
    client.api_key=os.environ['OPENAI_API_KEY']

    response = client.completions.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.3,
        max_tokens=80,
    )

    return response.choices[0].text

# Main loop

if __name__ == '__main__':
    speak('All systems nominal and ready, Captain.', 120)

    while True: 
        # Parse commands as a list
        query = parseCommand().lower().split()

        if query[0] in activationWords and len(query) > 1:
            query.pop(0)

        # List Commands
        if query[0] == 'say':
            if 'hello' in query:
                speak('Greetings, Captain.') 
            else:
                query.pop(0) # remove say
                speech = ' '.join(query)
                speak(speech)  

        # OpenAI Queries
        if query[0] == 'insight':
            query.pop(0)
            query = ' '.join(query)
            speech = query_openai(query)
            speak("Ok")
            speak(speech)


        # Navigating to Websites
        if query[0] == 'go' and query[1] == 'to':
            speak('Opening...')
            query = ' '.join(query[2:])
            webbrowser.get('firefox').open_new(query)

        # Wikipedia
        if query[0] == 'wikipedia':
            query = ' '.join(query[1:])
            speak('Querying the universal database.')
            time.sleep(2)
            speak(search_wikipedia(query))

        # Wolfram Alpha
        if query[0] == 'compute' or query[0] == 'computer':
            query = ' '.join(query[1:])
            speak('Computing')
            try:
                result = search_wolframAlpha(query)
                speak(result)
            except:
                speak('Unable to comply.')  

        # Journal Entries or Note taking
        if query[0] == 'log':
            speak('Ready to record your entry')
            newNote = parseCommand().lower()
            now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            with open('note_%s.txt', 'w') as newFile:
                newFile.write(now)
                newFile.write(' ')
                newFile.write(newNote)
                speak('Entry recorded')

        if query[0] == 'exit':
            speak('Logging off')
            break        

