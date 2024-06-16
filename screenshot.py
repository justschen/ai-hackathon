import os
import shutil
import subprocess
import time

from PyQt5.QtCore import QObject, pyqtSignal
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from s3 import S3Uploader


class ScreenshotHandler(FileSystemEventHandler):
    
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(('.png', '.jpg', '.jpeg')):
            new_path = os.path.join(os.path.dirname(event.src_path), "SCREENSHOTDONOTREMOVE.png")
            os.rename(event.src_path, new_path)
            target_directory = os.path.expanduser('~/hackathon')
            os.makedirs(target_directory, exist_ok=True)
            target_path = os.path.join(target_directory, "SCREENSHOTDONOTREMOVE.png")
            shutil.move(new_path, target_path)
            print(f"Moved to: {target_path}")
            self.s3_manager = S3Uploader()
            self.s3_manager.upload_and_return_url_no_screenshot(target_path)
            return event.src_path
        else:
            print(f"File created but not a screenshot: {event.src_path}")

def get_screenshot_directory():
    try:
        # result = subprocess.run(
        #     ["defaults", "read", "com.apple.screencapture", "location"],
        #     capture_output=True,
        #     text=True,
        #     check=True
        # )
        path = None
        if not path:
            return os.path.expanduser("~/Desktop")
        return os.path.expanduser(path)  # Ensure the path is correctly expanded
    except Exception as e:
        print(f"Error finding screenshot directory: {e}")
        return os.path.expanduser("~/Desktop")

if __name__ == "__main__":
    screenshot_path = get_screenshot_directory()
    
    # Check if the directory exists
    if not os.path.exists(screenshot_path):
        print(f"Screenshot directory does not exist: {screenshot_path}")
        exit(1)

    event_handler = ScreenshotHandler()
    observer = Observer()
    observer.schedule(event_handler, screenshot_path, recursive=False)
    observer.start()

    print(f"Monitoring {screenshot_path} for screenshots...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()