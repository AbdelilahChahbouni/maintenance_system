# from kivy.uix.screenmanager import Screen
# from kivy.properties import StringProperty
# from utils.api import login

# from .utils import app_session

# class LoginScreen(Screen):
#     email = StringProperty("")
#     password = StringProperty("")

#     def do_login(self):
#         resp = login(self.email, self.password)
#         if "access_token" in resp:
#             app_session["token"] = resp["access_token"]
#             app_session["user_id"] = resp["user"]["id"]
#         if resp.get("success"):
#             self.manager.current = "dashboard"
#             self.manager.get_screen("dashboard").token = resp.get("token")
#         else:
#             self.ids.login_msg.text = resp.get("message")
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from utils.api import login
from .utils import app_session

class LoginScreen(Screen):
    email = StringProperty("")
    password = StringProperty("")
    print(email , password)

    def do_login(self):
        resp = login(self.email, self.password)

        if resp.get("success"):
            # Save the session values
            app_session["token"] = resp["token"]
            app_session["user_id"] = resp["user_id"]



            # Redirect to dashboard
            self.manager.current = "dashboard"

        else:
            # Show error message
            self.ids.login_msg.text = resp.get("message", "Login failed")
