# ai-hackathon
vs code internal hackathon project

### Setup
- in python 3.9.2, not sure if it matters. creating venv works best.

### Installs
- install requirements, there are some wonky ones
- i didn't add a bunch in the requiurements.txt sorrry
- for sure need: `watchdog numpy scipy soundfile boto3 botocore pyautogui pydub PyQt5 sounddevice pygame` which weren't added to requirements

### Requirements
- OpenAI API (Azure Open AI works too)
- Eleven Labs API (I can provide, DM me)
- Azure Speech (can use VS Code speech, can also use personal set up)
- AWS (for s3, or run the risk of having huge base64 images)
- Can ignore the OBS code.
- See the `AUTHANDKEYS.py` file to put your keys in.

### How to use the app!
- `sudo python app.py`
- A floating head will appear. Navigate buttons via the menu bar at the top of the screen
- Click `Actions`-> `Chat` or `Chat with Context`. Screenshots will also trigger the listener.
- After you've finished talking, press `p` in the terminal to stop listening and start the request.

### Note:
- If trying using Azure Open AI, might have some limitations
- Not sure if the gpt-4o deployment is working atm. Others should be okay, but then screenshot and image processing will not work. 

### Key Files:
- AUTHANDKEYS.py: auth and keys
- openai_chat.py: changing deployment model, azure vs regular open ai
- app.py: main logic, lot's of hardcoded stuff

<img width="750" alt="Screen Shot 2024-06-16 at 4 47 46 PM" src="https://github.com/justschen/ai-hackathon/assets/54879025/b93d0223-3d98-450a-8f01-28006ce6c8d2">
