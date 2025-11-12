# from kivy.uix.screenmanager import Screen
# from kivy.properties import StringProperty

# class ScanScreen(Screen):
#     token = StringProperty("")
#     user_id = StringProperty("")
#     part_id = StringProperty("")

#     def go_confirm(self):
#         confirm_screen = self.manager.get_screen("confirm")
#         confirm_screen.part_id = self.part_id
#         confirm_screen.transaction_type = "OUT"
#         confirm_screen.token = self.token
#         confirm_screen.user_id = self.user_id
#         self.manager.current = "confirm"

import cv2
from pyzbar.pyzbar import decode
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from utils.api import extract_part_id , get_machines
from utils.api import get_machines
from .utils import app_session



class ScanScreen(Screen):
    def on_enter(self):
        # Start camera loop
        self.capture = cv2.VideoCapture(0)
        self.event = Clock.schedule_interval(self.update, 1.0 / 30.0)

    def on_leave(self):
        # Stop camera loop
        Clock.unschedule(self.event)
        self.capture.release()

    def update(self, dt):

        ret, frame = self.capture.read()
        if not ret:
            return

        # Convert BGR → RGB for Kivy
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to texture
        buffer = frame_rgb.flatten()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buffer, bufferfmt='ubyte', colorfmt='rgb')
        texture.flip_vertical()

        self.ids.camera_feed.texture = texture

        # Scan for QR codes
        decoded_objs = decode(frame)
        if decoded_objs:
            data = decoded_objs[0].data.decode("utf-8")
            part_id = extract_part_id(data)  # QR text
            print("QR Detected:", part_id)
            token = app_session.get("token")
            confirm = self.manager.get_screen("confirm")
            #confirm.ids.part_id_input.text = part_id
            confirm.transaction_type = "OUT"  # or "IN" depending on choice
            #confirm.machines = [{"text": m["name"], "id": m["id"]} for m in get_machines(token)]  # fetch machines
            confirm.machines = [m["name"] for m in get_machines(token)]
            confirm.part_id = part_id
            confirm.transaction_type = app_session.get("transaction_type")

            self.manager.current = "confirm"

