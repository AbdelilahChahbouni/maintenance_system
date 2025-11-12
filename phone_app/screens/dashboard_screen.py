# from kivy.uix.screenmanager import Screen
# from kivy.properties import StringProperty

# class DashboardScreen(Screen):
#     token = StringProperty("")
#     user_id = StringProperty("")   # we will get it from login later

#     def go_scan(self):
#         scan_screen = self.manager.get_screen("scan")
#         scan_screen.token = self.token
#         scan_screen.user_id = self.user_id
#         self.manager.current = "scan"

#     def go_add_stock(self):
#         confirm_screen = self.manager.get_screen("confirm")
#         confirm_screen.transaction_type = "IN"
#         confirm_screen.token = self.token
#         confirm_screen.user_id = self.user_id
#         self.manager.current = "confirm"
from kivy.uix.screenmanager import Screen

class DashboardScreen(Screen):
    def go_to_transaction_choice(self):
        self.manager.current = "transaction_choice"

    def logout(self):
        self.manager.current = "login"

