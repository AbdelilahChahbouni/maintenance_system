from kivy.uix.screenmanager import Screen
from .utils import app_session

class TransactionChoiceScreen(Screen):
    def choose_in(self):
        #self.manager.get_screen("confirm").transaction_type = "IN"
        app_session["transaction_type"] = "IN"
        #self.manager.current = "confirm"
        self.manager.current = "scan"   # go scan before confirm

    def choose_out(self):
        #self.manager.get_screen("confirm").transaction_type = "OUT"
        app_session["transaction_type"] = "OUT"
        #self.manager.current = "confirm"
        self.manager.current = "scan"   # go scan before confirm
