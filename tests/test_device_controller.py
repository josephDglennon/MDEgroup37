import tkinter as tk
from tkinter import ttk, filedialog
import os

class BooleanToggleApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Boolean Toggle App")

        self.recording = False

        # create and configure the Start/Stop button
        self.toggle_button = tk.Button(master, text="Start Recording", command=self.toggle)
        self.toggle_button.pack(pady=10)

        # create a button to open the assessments viewer menu
        self.view_assessments_button = tk.Button(master, text="View Assessments", command=self.open_assessments_viewer)
        self.view_assessments_button.pack(pady=10)

        # create a button to load assessment file
        self.load_assessment_button = tk.Button(master, text="Load Assessment File", command=self.load_assessment_file)
        self.load_assessment_button.pack(pady=10)

    def toggle(self):
        # toggle the boolean value
        self.recording = not self.recording

        # update the button text based on the boolean value
        if self.recording:
            self.toggle_button.config(text="Stop Recording")
        else:
            self.toggle_button.config(text="Start Recording")

    def open_assessments_viewer(self):
        # create a new window for viewing assessments
        assessments_viewer_window = tk.Toplevel(self.master)
        assessments_viewer_window.title("Assessments Viewer")

        # add a treeview to display assessments
        tree = ttk.Treeview(assessments_viewer_window, columns=("Assessment", "Status"), show="headings")
        tree.heading("Assessment", text="Assessment")
        tree.heading("Status", text="Status")
        tree.pack(pady=10)

        # you can insert assessments here or load them from a file

    def load_assessment_file(self):
        # get the current working directory
        current_dir = os.getcwd()

        # construct the path to the folder within the same directory
        folder_in_same_directory = os.path.join(current_dir, "assessments")

        # open a file dialog to select an assessment file
        file_path = filedialog.askopenfilename(title="Select an Assessment File",
                                               initialdir=folder_in_same_directory,
                                               filetypes=[("Assessment files", "*.json;*.xml")])

        if file_path:
            # load the selected assessment file and display its content in the console for now
            with open(file_path, 'r') as file:
                assessment_content = file.read()
                print(f"Loaded Assessment File:\n{assessment_content}")

# create the main window
root = tk.Tk()

# create an instance of the BooleanToggleApp class
app = BooleanToggleApp(root)

# run the Tkinter event loop
root.mainloop()
