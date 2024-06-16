import os
import time

from elevenlabs import generate, play, save, set_api_key, stream, voices

from AUTHANDKEYS import ELEVENLABS_API_KEY

try:
  set_api_key(ELEVENLABS_API_KEY)
except TypeError:
  exit("Ooops! You forgot to set ELEVENLABS_API_KEY in your environment!")

class ElevenLabsManager:

    def __init__(self):
        all_voices = voices()
        print(f"\nAll ElevenLabs voices: \n{all_voices}\n")

    def text_to_audio(self, input_text, voice="", save_as_wave=True, subdirectory=""):
        audio_saved = generate(
          text=input_text,
          voice=voice,
          model="eleven_monolingual_v1"
        )
        if save_as_wave:
            file_name = f"recording{str(hash(input_text))}.wav"
        else:
          file_name = f"msg-{str(hash(input_text))}.mp3"
        tts_file = os.path.join(os.path.abspath(os.curdir), subdirectory, file_name)
        save(audio_saved,tts_file)
        return file_name

    def text_to_audio_played(self, input_text, voice=""):
        audio = generate(
          text=input_text,
          voice=voice,
          model="eleven_monolingual_v1"
        )
        play(audio)

    def text_to_audio_streamed(self, input_text, voice=""):
        audio_stream = generate(
          text=input_text,
          voice=voice,
          model="eleven_monolingual_v1",
          stream=True
        )
        stream(audio_stream)


if __name__ == '__main__':
    elevenlabs_manager = ElevenLabsManager()

    elevenlabs_manager.text_to_audio_streamed("Test test test test", "SteVen")
    time.sleep(2)
    elevenlabs_manager.text_to_audio_played("Test test test test", "SteVen")
    time.sleep(2)
    file_path = elevenlabs_manager.text_to_audio("Test test test test", "SteVen")
    print("Finished with all tests")

    time.sleep(30)
