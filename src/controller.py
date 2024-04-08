
import gui
import storage
import sensors
import settings

class Controller:
    def __init__(self):
        self.root = gui.MainWindow()
        self.db_manager = storage.DatabaseManager()
        self.recorder = sensors.Recorder()
        self.context_pane = self.root.context_pane
        self.subviews = {}

    def _add_subview(self, Subview):
        subview = Subview(self.context_pane)

    def start(self):
        self.root.mainloop()

    