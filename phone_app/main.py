from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from screens.login_screen import LoginScreen
from screens.dashboard_screen import DashboardScreen
from screens.scan_screen import ScanScreen
from screens.confirm_screen import ConfirmScreen
from screens.transaction_choice_screen import TransactionChoiceScreen
from screens.confirm_screen import ConfirmScreen
from kivy.core.window import Window
from kivy.utils import get_color_from_hex


Window.clearcolor = get_color_from_hex("#070942")
class MainScreenManager(ScreenManager):
    pass


class PhoneApp(App):
    def build(self):
        Builder.load_file("kivy_files/login.kv")
        Builder.load_file("kivy_files/dashboard.kv")
        Builder.load_file("kivy_files/scan.kv")
        Builder.load_file("kivy_files/confirm.kv")
        Builder.load_file("kivy_files/transaction_choice_screen.kv")
        

        sm = MainScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(ScanScreen(name="scan"))
        sm.add_widget(ConfirmScreen(name="confirm"))
        sm.add_widget(TransactionChoiceScreen(name="transaction_choice"))
        


        return sm


if __name__ == "__main__":
    PhoneApp().run()











# from kivy.app import App
# from kivy.uix.screenmanager import ScreenManager
# from screens.login_screen import LoginScreen
# from screens.dashboard_screen import DashboardScreen
# from screens.scan_screen import ScanScreen
# from screens.confirm_screen import ConfirmScreen

# class MaintenanceApp(App):
#     def build(self):
#         sm = ScreenManager()
#         sm.add_widget(LoginScreen(name="login"))
#         sm.add_widget(DashboardScreen(name="dashboard"))
#         sm.add_widget(ScanScreen(name="scan"))
#         sm.add_widget(ConfirmScreen(name="confirm"))
#         return sm

# if __name__ == "__main__":
#     MaintenanceApp().run()
