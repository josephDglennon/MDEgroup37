
import os
import sounddevice
import device_controller
import customtkinter
from customtkinter import (
    CTk,
    CTkFrame,
    CTkButton,
    CTkEntry,
    CTkTextbox,
    CTkLabel,
    CTkFont,
    CTkScrollableFrame,
    CTkCheckBox,
    CTkProgressBar
)

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

class MainWindow(CTk):
    def __init__(self):
        super().__init__()

        self.title("UAS Damage Assessment")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar menu frame
        self.sidebar = CTkFrame(self, width=140, corner_radius=0, fg_color='gray14')
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        # sidebar header
        self.sidebar_title = CTkLabel(self.sidebar, text="Menu", font=CTkFont(size=20, weight="bold"))
        self.sidebar_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # sidebar menu buttons
        self.new_test_button = CTkButton(self.sidebar, text="New Test", command=self.new_test_button_handler)
        self.new_test_button.grid(row=1, column=0, padx=20, pady=10)

        self.open_test_button = CTkButton(self.sidebar, text="Open Test", command=self.open_test_button_handler)
        self.open_test_button.grid(row=2, column=0, padx=20, pady=10)

        self.settings_button = CTkButton(self.sidebar, text="Settings", command=self.settings_button_handler)
        self.settings_button.grid(row=3, column=0, padx=20, pady=10)

        # context container
        self.context_pane = CTkFrame(self, fg_color='green', corner_radius=0)
        self.context_pane.grid(row=0, column=1, rowspan=4, columnspan=4, sticky="nsew")
        self.context_pane.grid_rowconfigure(0, weight=1)
        self.context_pane.grid_columnconfigure(0, weight=1)

        # context frames
        self.context_frames = {}
        for frame_class in (TestSummaryFrame, EditTestFrame, OpenTestFrame, SettingsFrame):

            frame_instance = frame_class(self.context_pane, self)
            
            self.context_frames[frame_class] = frame_instance

            frame_instance.grid(row=0, column=0, sticky='nsew')
            frame_instance._corner_radius = 0

        self.show_frame(EditTestFrame)

    def show_frame(self, frame_class):
        frame_instance = self.context_frames[frame_class]
        frame_instance.tkraise()

    def new_test_button_handler(self):
        self.show_frame(EditTestFrame)
        return
    
    def open_test_button_handler(self):
        self.show_frame(OpenTestFrame)
        return

    def settings_button_handler(self):
        self.show_frame(SettingsFrame)
        return 


class TestSummaryFrame(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._fg_color = 'red'


class EditTestFrame(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.columnconfigure((0,1), weight=0)
        self.columnconfigure(2, weight=1)
        self.rowconfigure((0,1,2,3,4,5,6,7), weight=0)

        # header label
        self.header_label = CTkLabel(self, text="Edit Test Data", font=CTkFont(size=20, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=20, pady=20)

        # test name label and field
        self.test_name_label = CTkLabel(self, text='Test name:', font=CTkFont(size=14), justify='left', anchor='w', height=14)
        self.test_name_label.grid(row=1, column=0, sticky='nsew', padx=20)
        self.test_name_entry = CTkEntry(self, width=250)
        self.test_name_entry.grid(row=2, column=0, sticky='w', padx=20) 

        # test notes label and field
        self.test_notes_label = CTkLabel(self, text='Notes:', font=CTkFont(size=14))
        self.test_notes_label.grid(row=3, column=0, sticky='ws', padx=20)
        self.test_notes_box = CTkTextbox(self, height=100, width=250, border_color='gray36', border_width=2, fg_color='gray20')
        self.test_notes_box.grid(row=4, column=0, padx=20)

        # audio/signal sample recording panel
        self.sample_recording_frame = CTkFrame(self, fg_color='gray14', width=250)
        self.sample_recording_frame.grid(row=5, column=0, padx=20, pady=20, sticky='nsew')
        self.sample_recording_frame.grid_columnconfigure((0,1,2), weight=1)
        self.sample_recording_frame.rowconfigure((0,1,2), weight=0)

        # sample recording panel buttons
        self.sample_recording_frame_header = CTkLabel(self.sample_recording_frame, text='Recording Sample', font=CTkFont(size=14))
        self.sample_recording_frame_header.grid(row=0, column=0, columnspan=3)
        self.sample_cursor_time = CTkLabel(self.sample_recording_frame, text='00:00 / 00:00')
        self.sample_cursor_time.grid(row=1, column=0, columnspan=3)
        self.record_button = CTkButton(self.sample_recording_frame, text='Record', command=None, width=75, fg_color='red3', hover_color='red4')
        self.record_button.grid(row=2, column=0, padx=2, pady=3, sticky='nsew')
        self.play_button = CTkButton(self.sample_recording_frame, text='Play', command=None, width=75)
        self.play_button.grid(row=2, column=1, padx=2, pady=3, sticky='nsew')
        self.stop_button = CTkButton(self.sample_recording_frame, text='Stop', command=None, width=75)
        self.stop_button.grid(row=2, column=2, padx=2, pady=3, sticky='nsew')

        # process sample button
        self.process_button = CTkButton(self, text='Process Sample', command=None, font=CTkFont(size=14), width=250, fg_color='green3', hover_color='green4')
        self.process_button.grid(row=6, column=0)

        # process progress bar
        self.progress_bar = CTkProgressBar(self, width=250)
        self.progress_bar.grid(row=7, column=0, pady=10)

        # tags frame and label
        self.tags_frame = CTkFrame(self, fg_color='gray14', width=400)
        self.tags_frame.grid_columnconfigure(0, weight=1)
        self.tags_frame.grid_rowconfigure(0, weight=1)
        self.tags_frame.grid(row=1, column=1, rowspan=4, sticky='nsew')
        self.tags_frame_header = CTkLabel(self.tags_frame, text='Tags', font=CTkFont(size=14))
        self.tags_frame_header.grid(row=0, column=0, sticky='n', pady=5)
        
        # new tag button
        self.new_tag_button = CTkButton(self, text='+ New Tag', fg_color='gray17', hover_color='gray14', width=60, command=None)
        self.new_tag_button.grid(row=5, column=1, sticky='nw', pady=10)

        # tag scroll window
        self.tag_scroll_frame = CTkScrollableFrame(self.tags_frame, fg_color='gray14')
        self.tag_scroll_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        self.tag_scroll_frame.grid_columnconfigure(1, weight=1)

        # example tag item
        tag_item_frame = CTkFrame(self.tag_scroll_frame, fg_color='gray20')
        tag_item_frame.grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        tag_item_frame.grid_columnconfigure((0,1,2), weight=1)
        tag_active_button = CTkCheckBox(tag_item_frame, text='', width=15, border_width=2)
        tag_active_button.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        tag_item_name = CTkLabel(tag_item_frame, text='Tag1')
        tag_item_name.grid(row=0, column=1)
        tag_delete_button = CTkButton(tag_item_frame, text='X', width=15, border_width=0, fg_color='red3', hover_color='red4')
        tag_delete_button.grid(row=0, column=2, sticky='e', padx=5)

        tag_item_frame1 = CTkFrame(self.tag_scroll_frame, fg_color='gray20')
        tag_item_frame1.grid(row=1, column=1, sticky='ew', pady=5, padx=5)
        tag_item_frame1.grid_columnconfigure((0,1,2), weight=1)
        tag_active_button1 = CTkCheckBox(tag_item_frame1, text='', width=15, border_width=2)
        tag_active_button1.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        tag_item_name1 = CTkLabel(tag_item_frame1, text='Tag2')
        tag_item_name1.grid(row=0, column=1)
        tag_delete_button1 = CTkButton(tag_item_frame1, text='X', width=15, border_width=0, fg_color='red3', hover_color='red4')
        tag_delete_button1.grid(row=0, column=2, sticky='e', padx=5)

        tag_item_frame2 = CTkFrame(self.tag_scroll_frame, fg_color='gray20')
        tag_item_frame2.grid(row=2, column=1, sticky='ew', pady=5, padx=5)
        tag_item_frame2.grid_columnconfigure((0,1,2), weight=1)
        tag_active_button2 = CTkCheckBox(tag_item_frame2, text='', width=15, border_width=2)
        tag_active_button2.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        tag_item_name2 = CTkLabel(tag_item_frame2, text='Tag3')
        tag_item_name2.grid(row=0, column=1)
        tag_delete_button2 = CTkButton(tag_item_frame2, text='X', width=15, border_width=0, fg_color='red3', hover_color='red4')
        tag_delete_button2.grid(row=0, column=2, sticky='e', padx=5)

        # save, cancel, delete buttons
        self.button_bar = CTkFrame(self, fg_color='gray17', width=250, height=30)
        self.button_bar.grid(row=8, column=0, columnspan=2, sticky='nsew', pady=20, padx=20)
        self.button_bar.grid_columnconfigure((0,1), weight=0)
        self.button_bar.grid_columnconfigure(2, weight=1)
        self.save_button = CTkButton(self.button_bar, text='Save', command=None, width=75, fg_color='green3', hover_color='green4')
        self.save_button.grid(row=0, column=0, padx=2, pady=3, sticky='w')
        self.cancel_button = CTkButton(self.button_bar, text='Cancel', command=None, width=75)
        self.cancel_button.grid(row=0, column=1, padx=2, pady=3)
        self.delete_button = CTkButton(self.button_bar, text='Delete', command=None, width=75, fg_color='red3', hover_color='red4')
        self.delete_button.grid(row=0, column=2, padx=65, pady=3, sticky='e')

        # insert output summary
        self.output_summary = OutputSummaryFrame(self)
        self.output_summary.grid(row=1, column=2, rowspan=7, padx=20, sticky='nsew')


class OpenTestFrame(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._fg_color = 'blue'

class SettingsFrame(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._fg_color = 'yellow'

class OutputSummaryFrame(CTkFrame):
    def __init__(self, parent,):
        super().__init__(parent, fg_color='gray14', width=300, border_color='gray36', border_width=2)

        self.columnconfigure(0, weight=1)

        self.summary_header = CTkLabel(self, text='Output Summary', font=CTkFont(size=18, weight="bold"))
        self.summary_header.grid(row=0, column=0, sticky='nsew', pady=5, padx=5)

if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()