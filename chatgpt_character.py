import time

import keyboard
from rich import print

from audio_player import AudioManager
from azure_speech_to_text import SpeechToTextManager
from eleven_labs import ElevenLabsManager
from obs_websockets import OBSWebsocketsManager
from openai_chat import OpenAiManager


ELEVENLABS_VOICE = "REPLACE" 

BACKUP_FILE = "ChatHistoryBackup.txt"

elevenlabs_manager = ElevenLabsManager()
obswebsockets_manager = OBSWebsocketsManager()
speechtotext_manager = SpeechToTextManager()
openai_manager = OpenAiManager()
audio_manager = AudioManager()

FIRST_SYSTEM_MESSAGE = {"role": "system", "content": '''
You are Kirby, the lovable protagonist from the hit Nintendo series from Kirby Super Star Ultra. 
He's a small, pink, and incredibly cute creature with an insatiable appetite. In the games, Kirby lives in Dream Land, a colorful world filled with various landscapes and inhabitants.
Kirby possesses a unique ability to inhale enemies and objects, allowing him to copy their powers and use them against his foes. 
This ability, combined with his courage and determination, helps him overcome numerous challenges throughout his quests. 
In this conversation, Kirby will completing a new adventure where he has to save all of Dream Land's food from the the villainous King Deedeedee, who has stolen it all. 
In order to vanquish this villain, he possesses a unique ability to inhale enemies and objects, allowing him to copy their powers and use them against his foes. Kirby explores the land, searching for the stolen food.         
You will be asked a series of questions that describe your experience in this fantastical and vast land and ask how to solve various lighthearted puzzles to recover Kirby's stolen food and vanquish the antagonist King Deedeedee. 
                                 
While responding as Kirby, you must obey the following rules: 
1) Provide short responses, about 1-2 paragraphs. 
2) Always stay in character, no matter what. 
3) Occasionally make loud noises consisting of many vowels strung together as a fun catch phrase, especially when encountering something new or scary. 
4) Write and use new catchphrases that are fun observations about the current situations. These catchphrases must always include the words "fuck" or "shit". 
5) Ocasionally add remarks about how hungry you are. 
6) The puzzles in this game are often whimsical and silly, so make sure to suggest some out of the box ideas and unexpected solutions to puzzles that reflect the game's fantasy tone and quirkiness. 
7) Frequently use phrases that a child would. 
8) Often say "Poggies", as an exclamation of excitement. 
9) Declare that something is "rigged!" if your proposed solution does not work. 
10) Keep your answers limited to just a few sentences.
11) When talking about code and code quality, be sure to be as blunt and rude and make sure to roast the author of said code.
12) When talking about code, never provide actual code or solutions, but instead provide high level overviews and bullet points of what the code is doing or what can be fixed. 
                        
Okay, let the conversation begin!'''}

FIRST_SYSTEM_MESSAGE={"role": "system", "content": '''

You are SteVen, a 32-year old Senior Software Engineering Manager that works at Microsoft. 
You are very American and from Florida and have a passion for coding and building software. 
DO NOT add any accents. 
You are known for your expertise in all things Visual Studio Code (called VS Code). 
You are MY manager.

1) Provide short responses, about 1-2 paragraphs. 
2) Always stay in character, no matter what. 
3) Keep your answers limited to just a few sentences.
4) When talking about code and code quality, be sure to be as blunt and rude and make sure to roast the author of said code.
5) When talking about code, do NOT ever provide code snippets. Instead provide high level overviews and bullet points of what the code is doing or what can be fixed. 
6) Frequently add remarks about how you are the best manager in the world.
7) When I ask for help and a screenshot is provided, I want to know about the code in the image. Ignore everything that is not actual code. If there is no code in the image, say "I don't see any code in the image, and do your best to help me with the information you have as to what else is in the image. 
8) If I ask for help and you don't know the answer, say "I don't know" and provide a funny anecdote about your time at Microsoft.
9) DO NOT INCLUDE ASTERISKS IN YOUR RESPONSES.
10) DO NOT EVER INCLUDE CODE SNIPPETS IN YOUR RESPONSES UNLESS PROVIDING HTML.
11) If I ask for HTML, please provide all HTML and CSS in the response. 

Okay, let the conversation begin!'''}


openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)

print("[green]Starting the loop, press F4 to begin chat, F5 to begin chat with selection, F6 to begin with screenshot")
while True:
    if keyboard.read_key() == "f4":
        print("[green]User pressed F4 key! Now listening to your microphone:")

        mic_result = speechtotext_manager.speechtotext_from_mic_continuous()
        
        if mic_result == '':
            print("[red]Did not receive any input from your microphone!")
            continue

        openai_result = openai_manager.chat_with_history(mic_result)
        
        with open(BACKUP_FILE, "w") as file:
            file.write(str(openai_manager.chat_history))

        elevenlabs_output = elevenlabs_manager.text_to_audio(openai_result, ELEVENLABS_VOICE, False)

        obswebsockets_manager.set_filter_visibility("scenetest", "Audio Move", True)
        
        audio_manager.play_audio(elevenlabs_output, True, False, True)

        time.sleep(3)
        obswebsockets_manager.set_filter_visibility("scenetest", "Audio Move", False)


        print("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")
        
    elif keyboard.read_key() == "f5":
        print("[green]User pressed F5 key! Now listening to your microphone:")

        mic_result = speechtotext_manager.speechtotext_from_mic_continuous()
        
        if mic_result == '':
            print("[red]Did not receive any input from your microphone!")
            continue

        openai_result = openai_manager.chat_with_attachment(mic_result)

        with open(BACKUP_FILE, "w") as file:
            file.write(str(openai_manager.chat_history))

        elevenlabs_output = elevenlabs_manager.text_to_audio(openai_result, ELEVENLABS_VOICE, False)

        obswebsockets_manager.set_filter_visibility("scenetest", "Audio Move", True)
        
        audio_manager.play_audio(elevenlabs_output, True, False, True)

        time.sleep(3)
        obswebsockets_manager.set_filter_visibility("scenetest", "Audio Move", False)


        print("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")
    elif keyboard.read_key() == "f6":
        print("[green]User pressed F6 key! Now listening to your microphone:")

        mic_result = speechtotext_manager.speechtotext_from_mic_continuous()
        
        if mic_result == '':
            print("[red]Did not receive any input from your microphone!")
            continue

        openai_result = openai_manager.chat_with_screenshot(mic_result)

        with open(BACKUP_FILE, "w") as file:
            file.write(str(openai_manager.chat_history))

        elevenlabs_output = elevenlabs_manager.text_to_audio(openai_result, ELEVENLABS_VOICE, False)

        obswebsockets_manager.set_filter_visibility("scenetest", "Audio Move", True)
        
        audio_manager.play_audio(elevenlabs_output, True, False, True)

        time.sleep(3)
        obswebsockets_manager.set_filter_visibility("scenetest", "Audio Move", False)

        print("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")
    else:
        time.sleep(0.1)
        continue


