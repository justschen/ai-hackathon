import os

import boto3
import pyautogui
import tiktoken
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from botocore.exceptions import NoCredentialsError
from openai import AzureOpenAI, OpenAI
from rich import print

from AUTHANDKEYS import OPEN_AI_KEY
from s3 import S3Uploader

s3 = S3Uploader()



def num_tokens_from_messages(messages, model='gpt-4'):
  try:
      encoding = tiktoken.encoding_for_model(model)
      num_tokens = 0
      for message in messages:
          num_tokens += 4 
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  
                  num_tokens += -1 
      num_tokens += 2  
      return num_tokens
  except Exception:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.""")
      

class OpenAiManager:
    
    def __init__(self):
        self.chat_history = [] # Stores the entire conversation
        try:
            self.client = OpenAI(api_key=OPEN_AI_KEY)
            # using azure open ai
            # os.environ["AZURE_OPENAI_ENDPOINT"] = "URL THAT LOGAN PROVIDED OUR ENDPOINT"
            # os.environ["CHAT_COMPLETIONS_DEPLOYMENT_NAME"] = "gpt-4o" # gpt-4o, Turbo, Gpt4, depends on what deployments we have.
            # os.environ["AZURE_OPENAI_API_VERSION"] = "VERSION"
            # os.environ["AZURE_OPENAI_API_KEY"] = "FILL IN WITH API KEY"
                
            # self.client = AzureOpenAI(
            #     azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            #     api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            #     api_key=os.environ["AZURE_OPENAI_API_KEY"],
            # )
        except TypeError:
            exit("Ooops! Issue with setting API for open ai or azure AI")

    # Asks a question with no chat history
    def chat(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        # Check that the prompt is under the token context limit
        chat_question = [{"role": "user", "content": prompt}]
        if num_tokens_from_messages(chat_question) > 8000:
            print("The length of this chat question is too large for the GPT model")
            return

        print("[yellow]\nProcessing...")

        image_url = s3.upload_and_return_url()

        content = [
                    {"type": "text", "text": prompt},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    },
                    },
                ]

        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                "role": "user",
                "content": content
                }
            ],
            max_tokens=300,
            )

        # Process the answer
        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        return openai_answer

    # Asks a question that includes the full conversation history
    def chat_with_history(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        # Add our prompt into the chat history
        self.chat_history.append({"role": "user", "content": prompt})

        # Check total token limit. Remove old messages as needed
        # print(f"[coral]Chat History has a current token length of {num_tokens_from_messages(self.chat_history)}")
        # while num_tokens_from_messages(self.chat_history) > 8000:
        #     self.chat_history.pop(1) 
        #     print(f"Popped a message! New token length is: {num_tokens_from_messages(self.chat_history)}")

        print("[yellow]\nProcessing...", self.chat_history)
        completion = self.client.chat.completions.create(
          model="gpt4o", # gpt-4o, Turbo, Gpt4, depends on what deployments we have.
          messages=self.chat_history
        )

        # Add this answer to our chat history
        self.chat_history.append({"role": completion.choices[0].message.role, "content": completion.choices[0].message.content})

        # Process the answer
        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        return openai_answer
    
    # Function to read file content
    def read_file_content(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()

    def chat_with_attachment(self, prompt="", screenshot_path=""):
        if not prompt:
            print("Didn't receive input!")
            return
        image_url = s3.upload_and_return_url_no_screenshot(screenshot_path)
        content = [
                    {"type": "text", "text": prompt},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    },
                    },
                ]

        # Add the file content to the end of the prompt
        self.chat_history.append({"role": "user", "content": content})
        # Add our prompt into the chat history
        print("[yellow]\nProcessing...")
        completion = self.client.chat.completions.create(
          model="gpt-4o",
          messages=self.chat_history
        )

        self.chat_history.remove({"role": "user", "content": content})

        # Add this answer to our chat history
        self.chat_history.append({"role": completion.choices[0].message.role, "content": completion.choices[0].message.content})

        # Process the answer
        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        return openai_answer
    
    def chat_with_screenshot_64(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return
        

        image_url = s3.stupidS3JustBase64()

        content = [
                    {"type": "text", "text": prompt},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    },
                    },
                ]

        # Add the file content to the end of the prompt
        self.chat_history.append({"role": "user", "content": content})

        # Add our prompt into the chat history

        print("[yellow]\nProcessing...")
        completion = self.client.chat.completions.create(
          model="gpt-4o",
          messages=self.chat_history
        )

        # Add this answer to our chat history
        self.chat_history.append({"role": completion.choices[0].message.role, "content": completion.choices[0].message.content})

        # Process the answer
        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        return openai_answer
    
    def chat_with_screenshot(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return
        

        image_url = s3.upload_and_return_url()
        print(image_url)

        content = [
                    {"type": "text", "text": prompt},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    },
                    },
                ]

        # Add the file content to the end of the prompt
        self.chat_history.append({"role": "user", "content": content})

        # Add our prompt into the chat history

        print("[yellow]\nProcessing...")
        completion = self.client.chat.completions.create(
          model="gpt-4o",
          messages=self.chat_history
        )

        # Add this answer to our chat history
        self.chat_history.append({"role": completion.choices[0].message.role, "content": completion.choices[0].message.content})

        # Process the answer
        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        return openai_answer

   

if __name__ == '__main__':
    openai_manager = OpenAiManager()

    # CHAT TEST
    chat_without_history = openai_manager.chat_with_screenshot("help")
    print(chat_without_history)

