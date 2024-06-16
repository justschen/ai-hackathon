import os

import boto3

from AUTHANDKEYS import AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY


import base64

import pyautogui
from botocore.exceptions import NoCredentialsError

# # List all S3 buckets to verify credentials
# response = s3_client.list_buckets()
# print("Existing buckets:")
# for bucket in response['Buckets']:
#     print(f"  {bucket['Name']}")

# Set environment variables
os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
os.environ['AWS_REGION'] = AWS_REGION


class S3Uploader:
    def __init__(self):
        # Set environment variables
        self.s3_client = boto3.client('s3')

    def upload_to_s3(self, file_name, bucket, object_name=None):
        s3_client = boto3.client('s3')
        try:
            response = s3_client.upload_file(file_name, bucket, object_name or file_name)
        except FileNotFoundError:
            print("The file was not found")
            return None
        except NoCredentialsError:
            print("Credentials not available")
            return None
        return f'https://{bucket}.s3.amazonaws.com/{object_name or file_name}'

    def upload_and_return_url(self):
        screenshot = pyautogui.screenshot()
        fileName = f"screenshot-{str(hash(screenshot.tobytes))}.png"
        screenshot.save(fileName)
        image_url = self.upload_to_s3(fileName, 'vscode-hackathon-test')
        if image_url:
            print(f'Image URL: {image_url}')
            return image_url
        else:
            print('Failed to upload image')
            return None
        
    def upload_and_return_url_no_screenshot(self, screenshot_path):
        image_url = self.upload_to_s3(screenshot_path, 'vscode-hackathon-test')
        if image_url:
            print(f'Image URL: {image_url}')
            return image_url
        else:
            print('Failed to upload image')
            return None
    
    def stupidS3JustBase64(self):
        screenshot = pyautogui.screenshot()
        fileName = f"screenshot-{str(hash(screenshot.tobytes))}.png"
        screenshot.save(fileName)
        with open(fileName, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        if encoded_string:
            return f'data:image/jpeg;base64,{encoded_string}'
        else:
            print('Failed to upload image')
            return None

if __name__ == '__main__':
    s3manager = S3Uploader()

    #TEST
    result = s3manager.stupidS3JustBase64()
    print(result)


