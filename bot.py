import cv2
import numpy as np
from mss import mss
from ultralytics import YOLO
import pygetwindow
import time
import os
import mouse
import keyboard
import random
from termcolor import colored
import torch
import sys

class Bot:
    def __init__(self):
        self.object_detector, self.label_names = self.initialize_model()
        self.is_active = False

    @staticmethod
    def animated_print_typing(text, color="white", delay=0.0005):
        for char in text:
            sys.stdout.write(colored(char, color))
            sys.stdout.flush()
            time.sleep(delay)
        print("")

    @staticmethod
    def display_logo():
        os.system("cls")
        Bot.animated_print_typing("""
                                                                                      
,--. ,--.  ,---.   ,-----.    ,--.   ,--.                      ,--.            ,--.   
|  | |  | /  O  \ '  .--./    |  |-. |  |,--.,--.,--,--,--.    |  |-.  ,---. ,-'  '-. 
|  | |  ||  .-.  ||  |        | .-. '|  ||  ||  ||        |    | .-. '| .-. |'-.  .-' 
'  '-'  '|  | |  |'  '--'\    | `-' ||  |'  ''  '|  |  |  |    | `-' |' '-' '  |  |   
 `-----' `--' `--' `-----'     `---' `--' `----' `--`--`--'     `---'  `---'   `--'   
                                                                                      
""", "green", delay=0.0005)

    @staticmethod
    def capture_screen(window):
        with mss() as screen_capture:
            screenshot_data = screen_capture.grab(window)
            screenshot_bgr = cv2.cvtColor(np.array(screenshot_data), cv2.COLOR_RGB2BGR)
            screenshot_rgb = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2RGB)
            return screenshot_rgb

    @staticmethod
    def initialize_model() -> tuple[YOLO, list]:
        print(colored("[✨] Loading detection model...", "yellow"))
        detection_model = YOLO("train.pt")

        if torch.cuda.is_available():
            detection_model.to("cuda")
            print(colored("[✅] Model loaded on GPU!", "green"))
        else:
            detection_model.to("cpu")
            print(colored("[⚠️] GPU not available, using CPU.", "yellow"))

        labels = detection_model.names
        return detection_model, labels

    @staticmethod
    def get_window_details():
        try:
            windows_with_title = pygetwindow.getWindowsWithTitle("TelegramDesktop")

            if not windows_with_title:
                raise ValueError("No matching windows found.")

            telegram_window = windows_with_title[0]

            if not telegram_window.isActive:
                telegram_window.minimize()
                telegram_window.restore()

            window_properties = {
                "height": telegram_window.height,
                "left": telegram_window.left,
                "top": telegram_window.top,
                "width": telegram_window.width,
            }
            return window_properties
        except Exception as e:
            print(colored(f"[❌] Error: Unable to locate TelegramDesktop window. {e}", "red"))
            os._exit(0)

    @staticmethod
    def process_predictions(predictions, label_names, application_window):
        for prediction in predictions:
            for detection_box in prediction.boxes:
                confidence_score = round(detection_box.conf.item(), 2)
                detected_label = label_names[int(detection_box.cls)]

                if detected_label == "bomb":
                    continue

                if detected_label == "snowman" or confidence_score > 0.8: 
                    if detected_label == "next_button":
                        delay_time = random.uniform(1.0, 5.0)  
                        print(colored(f"[⏳] Next game detected, waiting for bot to start", "cyan"))
                        time.sleep(delay_time)

                    x1, y1, x2, y2 = map(int, detection_box.xyxy[0])
                    center_x, center_y = application_window["left"] + (x1 + x2) // 2, application_window["top"] + (y1 + y2) // 2   
                    mouse.move(center_x, center_y, absolute=True)
                    mouse.click()

    @staticmethod
    def display_overlay(predictions):
        for prediction in predictions:
            overlay_frame = prediction.plot()

        cv2.waitKey(1) 

    @staticmethod
    def handle_activation():
        print(colored("[🚀] Activating...", "blue"))
        return True

    @staticmethod
    def handle_deactivation():
        print(colored("[🛑] Deactivating...", "magenta"))
        return False

    @staticmethod
    def wait_for_window():
        print(colored("[ℹ️] Bot is running. Please enable Blum to continue...", "cyan"))
        print(colored("[⚙️] Press 'space' to enable or 's' to disable!", "yellow"))
        print(colored("[💡] Note: Please activate the Play button and then enable the bot. The bot will automatically press Play in future rounds.", "cyan"))

    def run(self):
        self.display_logo()
        self.wait_for_window()

        while True:
            if self.is_active:
                try:
                    application_window = self.get_window_details()
                    current_frame = self.capture_screen(application_window)

                    predictions = self.object_detector.predict(current_frame, verbose=False)
                    self.process_predictions(predictions, self.label_names, application_window)
                    self.display_overlay(predictions)

                    if keyboard.is_pressed('v'):
                        self.is_active = self.handle_deactivation()

                except Exception as error:
                    print(colored(f"[💥] Error during prediction: {error}", "red"))
                    break
            else:
                if keyboard.is_pressed('space'):
                    self.is_active = self.handle_activation()

                time.sleep(0.01)

if __name__ == "__main__":
    bot = Bot()
    bot.run()
