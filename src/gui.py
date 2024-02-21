
import os
#import sounddevice
import device_controller
import database_manager as db
import customtkinter
import logging
import datetime

from database_manager import TestEntry
from typing import Callable, Tuple
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
    CTkProgressBar,
    CTkToplevel
)

# App sizing
MAIN_WINDOW_HEIGHT = 580
MAIN_WINDOW_WIDTH = 1100

# App coloring
WARNING_COLOR = 'red3'
WARNING_COLOR_HIGHLIGHTED = 'red4'
CONFIRM_COLOR = 'green3'
CONFIRM_COLOR_HIGHLIGHTED = 'green4'
CONTAINER_COLOR = 'gray14'
CONTAINER_BORDER_COLOR = 'gray20'
BACKGROUND_COLOR = 'gray17'
BACKGROUND_COLOR_HIGHLIGHTED = 'gray14'
ITEM_COLOR = 'gray20'
ITEM_COLOR_HIGHLIGHTED = 'gray27'
ITEM_BORDER_COLOR = 'gray20'
ITEM_BORDER_COLOR_SELECTED = 'grey40'

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

db_manager = db.DatabaseManager()

class MainWindow(CTk):
    """The primary window object for the application GUI."""

    def __init__(self):
        super().__init__()

        self.title("UAS Damage Assessment")
        self.geometry("{}x{}".format(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT))
        self.resizable(False,False)

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar menu frame
        self.sidebar = CTkFrame(self, width=140, corner_radius=0,
                                fg_color=CONTAINER_COLOR)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        # sidebar header
        self.sidebar_title = CTkLabel(self.sidebar,
                                      text="Menu",
                                      font=CTkFont(size=20, weight="bold"))
        self.sidebar_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # sidebar menu buttons
        self.new_test_button = CTkButton(self.sidebar,
                                         text="New Test",
                                         command=self.new_test_button_handler)
        self.new_test_button.grid(row=1, column=0, padx=20, pady=10)

        self.open_test_button = CTkButton(self.sidebar,
                                          text="Open Test",
                                          command=self.open_test_button_handler)
        self.open_test_button.grid(row=2, column=0, padx=20, pady=10)

        self.settings_button = CTkButton(self.sidebar,
                                         text="Settings",
                                         command=self.settings_button_handler)
        self.settings_button.grid(row=3, column=0, padx=20, pady=10)

        # context container
        self.context_pane = CTkFrame(self, corner_radius=0,
                                     fg_color=BACKGROUND_COLOR)
        self.context_pane.grid(row=0, column=1, rowspan=4, columnspan=4, sticky="nsew")
        self.context_pane.grid_rowconfigure(0, weight=1)
        self.context_pane.grid_columnconfigure(0, weight=1)

        # context frames
        self.context_frames = {}
        for frame_class in (LandingContextFrame,
                            EditTestContextFrame,
                            OpenTestContextFrame,
                            SettingsContextFrame):

            frame_instance = frame_class(self.context_pane, self)
            
            self.context_frames[frame_class] = frame_instance

            frame_instance.grid(row=0, column=0, sticky='nsew')
            frame_instance._corner_radius = 0

        self.show_frame(LandingContextFrame)

    def show_frame(self, frame_class):
        frame_instance = self.context_frames[frame_class]
        frame_instance.tkraise()

    def new_test_button_handler(self):
        # load a blank test entry and show the edit context frame

        def submit(test_name: str):
            nonlocal self
            new_test = db_manager.create_new_test(test_name)
            self.context_frames[EditTestContextFrame].load_test_entry(new_test)
            self.show_frame(EditTestContextFrame)
        
        def cancel(text: str):
            return
        
        try:
            TextEntryPrompt(self,
                            max_characters=12,
                            prompt_text='Enter a name for test:',
                            confirm_command=submit,
                            cancel_command=cancel)
            
        except SpawnPromptError:
            pass # prevent multiple prompts from spawning
    
    def open_test_button_handler(self):
        self.context_frames[OpenTestContextFrame].update()
        self.show_frame(OpenTestContextFrame)
        return

    def settings_button_handler(self):
        self.show_frame(SettingsContextFrame)
        return 


class LandingContextFrame(CTkFrame):
    """The first screen the user sees upon opening the application.
    
    TODO: Display a quickstart guide and useful information to the user.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)

        # header label
        self.header_label = CTkLabel(self,
                                     text="UAS Damage Assessment Tool",
                                     font=CTkFont(size=20, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=20, pady=20, sticky='nsw')


class EditTestContextFrame(CTkFrame):
    """This context panel allows the user to edit, save, and/or delete a test entry."""

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.parent = parent
        self.controller = controller
        self.active_test_data = None

        self.columnconfigure((0,1), weight=0)
        self.columnconfigure(2, weight=1)
        self.rowconfigure((0,1,2,3,4,5,6,7), weight=1)

        # header label
        self.header_label = CTkLabel(self,
                                     text="Edit Untitled Test",
                                     font=CTkFont(size=20, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=20, pady=20, sticky='nsw')

        # test notes frame
        notes_container = CTkFrame(self, fg_color=BACKGROUND_COLOR)
        notes_container.grid(row=1, column=0, sticky='nsew')
        notes_container.grid_columnconfigure(0, weight=1)
        notes_container.grid_rowconfigure(0, weight=1)
        self.test_notes_label = CTkLabel(notes_container, text='Notes:', font=CTkFont(size=14))
        self.test_notes_label.grid(row=0, column=0, sticky='nsw', padx=20)
        self.test_notes_box = CTkTextbox(notes_container, height=100, width=250, border_width=2,
                                         border_color=CONTAINER_BORDER_COLOR,
                                         fg_color=CONTAINER_COLOR)
        self.test_notes_box.grid(row=1, column=0, padx=20, sticky='nsew')

        # audio/signal sample recording panel
        sample_recording_frame = SampleRecordingFrame(self)
        sample_recording_frame.grid(row=2, column=0, padx=20, pady=20, sticky='nsew')

        # process sample panel
        process_panel = CTkFrame(self, fg_color=BACKGROUND_COLOR)
        process_panel.grid(row=3, column=0, sticky='nsew')
        process_panel.grid_columnconfigure(0, weight=1)
        process_panel.grid_rowconfigure((0,1), weight=1)
        self.process_button = CTkButton(process_panel, text='Process Sample', width=250,
                                        command=None,
                                        font=CTkFont(size=14),
                                        fg_color=CONFIRM_COLOR,
                                        hover_color=CONFIRM_COLOR_HIGHLIGHTED)
        self.process_button.grid(row=0, column=0)
        self.progress_bar = CTkProgressBar(process_panel, width=250)
        self.progress_bar.grid(row=1, column=0, pady=10)

        # insert tag select frame
        self.tag_select_frame = TagContainer(self)
        self.tag_select_frame.grid(row=1, column=1, rowspan=4, sticky='nsew')
        
        # new tag button
        self.new_tag_button = CTkButton(self,  width=60,
                                        text='+ New Tag',
                                        fg_color=BACKGROUND_COLOR,
                                        hover_color=BACKGROUND_COLOR_HIGHLIGHTED,
                                        command=self.new_tag_button_handler)
        self.new_tag_button.grid(row=5, column=1, sticky='nw', pady=10)

        # save, cancel, delete buttons
        self.button_bar = CTkFrame(self, width=250, height=30,
                                   fg_color=BACKGROUND_COLOR)
        self.button_bar.grid(row=8, column=0, columnspan=2, sticky='nsew', pady=20, padx=20)
        self.button_bar.grid_columnconfigure((0,1), weight=0)
        self.button_bar.grid_columnconfigure(2, weight=1)
        self.save_button = CTkButton(self.button_bar, width=75,
                                     text='Save',
                                     command=self.save_button_handler,
                                     fg_color=CONFIRM_COLOR,
                                     hover_color=CONFIRM_COLOR_HIGHLIGHTED)
        self.save_button.grid(row=0, column=0, padx=2, pady=3, sticky='w')
        self.cancel_button = CTkButton(self.button_bar, width=75,
                                       text='Cancel',
                                       command=self.cancel_button_handler)
        self.cancel_button.grid(row=0, column=1, padx=2, pady=3)
        self.delete_button = CTkButton(self.button_bar, width=75,
                                       text='Delete',
                                       command=self.delete_button_handler,
                                       fg_color=WARNING_COLOR,
                                       hover_color=WARNING_COLOR_HIGHLIGHTED)
        self.delete_button.grid(row=0, column=2, padx=65, pady=3, sticky='e')

        # insert output summary
        self.output_summary = OutputSummaryFrame(self)
        self.output_summary.grid(row=1, column=2, rowspan=7, padx=20, sticky='nsew')

    def load_test_entry(self, test_data: TestEntry):
        '''Load the data of a preexisting test entry or present a fresh entry
        template for a new test.
        '''

        # copy test name to field if exists
        self.header_label.configure(text=('Editing: ' + test_data.name))

        # copy notes to field if exists
        self.test_notes_box.delete('1.0', 'end-1c')
        if test_data.notes: self.test_notes_box.insert('1.0', test_data.notes)

        # load and update recording time stamps if a recording sample exists

        # indicate linked tags via checkboxes
        self.tag_select_frame.sync_tags(test_data.tags)

        pass

    def new_tag_button_handler(self):

        def submit_text(text: str):
            nonlocal self
            
            self.tag_select_frame.add_tag_item(db_manager.create_new_tag(text))
        
        def cancel_text(text: str):
            return
        
        try:
            TextEntryPrompt(self,
                            max_characters=12,
                            prompt_text='Enter tag name:',
                            confirm_command=submit_text,
                            cancel_command=cancel_text)
            
        except SpawnPromptError:
            pass # prevent multiple prompts from spawning

    def delete_button_handler(self):

        def confirm_delete():
            db_manager.delete_active_test_entry()
            self.controller.show_frame(LandingContextFrame)
        
        def cancel_delete():
            return
    
        try:
            ConfirmSelectionPrompt(self,
                                   prompt_text='Are you sure you want to\ndelete this test entry?',
                                   confirm_command=confirm_delete,
                                   cancel_command=cancel_delete)
            
        except SpawnPromptError:
            pass # prevents multiple prompts from spawning

    def save_button_handler(self):
        # update active test data entry with data present in the edit form

        # notes
        db_manager._active_test.notes = self.test_notes_box.get("1.0",'end-1c')

        # active tags
        db_manager._active_test.tags = self.tag_select_frame.get_selected_tag_values()

        # data files

        # save data entry to database
        db_manager.save_active_test_data()

        # test jank
        print(self.tag_select_frame.get_selected_tag_values())
        pass

    def cancel_button_handler(self):

        def confirm_cancel():
            self.controller.show_frame(LandingContextFrame)
            db_manager.discard_active_entry()
            return
        
        def cancel_cancel():
            return
        
        try:
            ConfirmSelectionPrompt(self,
                                   prompt_text='Cancel test and discard data?',
                                   confirm_command=confirm_cancel,
                                   cancel_command=cancel_cancel)
            
        except SpawnPromptError:
            pass # prevents multiple prompts from spawning


class SampleRecordingFrame(CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, width=250,
                         fg_color=CONTAINER_COLOR)
        
        self.grid_columnconfigure((0,1,2), weight=1)
        self.grid_rowconfigure((0,1,2), weight=0)
        self.header = CTkLabel(self,
                                                      text='Sample Recording',
                                                      font=CTkFont(size=14))
        self.header.grid(row=0, column=0, columnspan=3)
        self.sample_cursor_time = CTkLabel(self,
                                           text='00:00 / 00:00')
        self.sample_cursor_time.grid(row=1, column=0, columnspan=3)
        self.record_button = CTkButton(self, width=75,
                                       text='Record',
                                       command=None)
        self.record_button.grid(row=2, column=0, padx=2, pady=3, sticky='nsew')
        self.play_button = CTkButton(self,  width=75,
                                     text='Play',
                                     command=None,)
        self.play_button.grid(row=2, column=1, padx=2, pady=3, sticky='nsew')
        self.stop_button = CTkButton(self,  width=75,
                                     text='Stop',
                                     command=None,
                                     fg_color=WARNING_COLOR,
                                     hover_color=WARNING_COLOR_HIGHLIGHTED)
        self.stop_button.grid(row=2, column=2, padx=2, pady=3, sticky='nsew')


class OutputSummaryFrame(CTkFrame):
    """Frame which displays the results of running the processor on the
    recorded sample.
    """

    def __init__(self, parent):
        super().__init__(parent,  width=300, border_width=2,
                         fg_color=CONTAINER_COLOR,
                         border_color=CONTAINER_BORDER_COLOR)

        self.columnconfigure(0, weight=1)

        self.summary_header = CTkLabel(self,
                                       text='Output Summary',
                                       font=CTkFont(size=18, weight="bold"))
        self.summary_header.grid(row=0, column=0, sticky='nsew', pady=5, padx=5)


class TagItem(CTkFrame):
    """A GUI object representing a tag with an activation checkbox and delete button."""

    def __init__(self,
                 parent=None,
                 controller=None,
                 tag_value: str='tag',
                 enable_delete: bool=True):
        """Constructs a GUI representation of a tag
        
        Parameters
        ----------
        parent: Any, optional
        tag_name: str, optional
            The text displayed on the tag
        """
        
        super().__init__(parent, fg_color=ITEM_COLOR)

        self.controller = controller
        self.tag_value = tag_value
        
        self.grid(sticky='new')
        self.grid_columnconfigure((0,1,2), weight=1)

        self.check_box_variable = customtkinter.BooleanVar()
        self.check_box = CTkCheckBox(self, width=15, border_width=2,
                                            text='',
                                            variable=self.check_box_variable)
        self.check_box.grid(row=0, column=0, sticky='w', padx=5, pady=5)

        self.tag_value_text = CTkLabel(self, text=tag_value, width=120)
        self.tag_value_text.grid(row=0, column=1)

        if enable_delete:
            self.delete_button = CTkButton(self,
                                            text='X',
                                            width=15,
                                            border_width=0,
                                            fg_color='red3',
                                            hover_color='red4',
                                            command=self.delete_button_handler)
            self.delete_button.grid(row=0, column=2, sticky='e', padx=5)

    def delete_button_handler(self):
        """Executed when the 'X' button is clicked."""

        def action_confirmed():
            nonlocal self
            db_manager.delete_tag_by_value(self.tag_value)
            self.controller.delete_tag_item(self)

        try:
            ConfirmSelectionPrompt(self, 
                                   prompt_text='Are you sure you want to\ndelete this tag?',
                                   confirm_command=action_confirmed)
        except SpawnPromptError:
            pass # prevent multiple prompts from spawning

    def get_status(self):
        return self.check_box_variable.get()


class TagContainer(CTkFrame):
    """Frame for displaying tag objects in.
    
    Parameters
    ----------
    parent: Any, 
    """

    def __init__(self, 
                 parent,
                 enable_delete=True,
                 header_text='Tags'):
        super().__init__(parent,
                         fg_color=CONTAINER_COLOR)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.tag_items: list[TagItem] = [] 
        self.num_tags = 0
        self.enable_delete = enable_delete

        # frame header
        self.header = CTkLabel(self,
                               text=header_text,
                               font=CTkFont(size=14))
        self.header.grid(row=0, column=0, sticky='n', pady=5)

        # tag scroll window
        self.tag_scroll_frame = CTkScrollableFrame(self,
                                                   fg_color=CONTAINER_COLOR)
        self.tag_scroll_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        self.tag_scroll_frame.grid_columnconfigure(0, weight=1)

        # load existing tags
        existing_tags = db_manager.list_existing_tags()
        self.load_tags(existing_tags)

    def add_tag_item(self, text: str):

        if text == None: return

        self.num_tags += 1
        new_tag = TagItem(self.tag_scroll_frame,
                          controller=self,
                          tag_value=text,
                          enable_delete=self.enable_delete)
        new_tag.grid(row=(self.num_tags - 1), column=0, pady=2, sticky='new')
        self.tag_items.append(new_tag)

    def load_tags(self, tags: list):

        self.clear()
        if tags:
            for tag in tags:
                self.add_tag_item(tag)

    def clear(self):
        for tag_item in self.tag_items:
            tag_item.destroy()
        
        self.num_tags = 0
        self.tag_items = []

    def get_selected_tag_values(self):
        selected_tag_values = []

        for tag in self.tag_items:
            if tag.get_status() == True:
                selected_tag_values.append(tag.tag_value)

        if selected_tag_values == []: return None
        return selected_tag_values
    
    def delete_tag_item(self, item: TagItem):
        self.tag_items.remove(item)
        item.destroy()

    def sync_tags(self, tags: list[str]):

        for item in self.tag_items:
            item.check_box.deselect()

        if tags:
            for tag in tags:
                for item in self.tag_items:
                    if item.tag_value == tag:
                        item.check_box.select()


class OpenTestContextFrame(CTkFrame):
    """Context pane for opening a specific saved test entry."""

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.parent = parent
        self.controller = controller

        self.grid_columnconfigure((0), weight=4)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure((1,3), weight=1)
        self.grid_rowconfigure(2, weight=3)
        self.grid_rowconfigure((0,1,3,4), weight=0)

        # header label
        self.header_label = CTkLabel(self,
                                     text="Open Test",
                                     font=CTkFont(size=20, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=20, pady=20, sticky='nsw')

        # search field
        self.search_field = SearchField(self, command=self.search)
        self.search_field.grid(row=1, column=0, padx=20, sticky='nw')

        # insert search table
        self.search_table = SearchTable(self)
        self.search_table.grid(row=2, column=0,
                               rowspan=2, padx=20, pady=20, sticky='nsew')

        # insert tag container
        self.tag_container = TagContainer(self,
                                          enable_delete=False,
                                          header_text='Filter by tag')
        self.tag_container.grid(row=2, column=2, pady=20, sticky='ns')

        # refresh button
        self.reload_button = CTkButton(self, text='\u27F3',
                                       fg_color=BACKGROUND_COLOR,
                                       hover_color=BACKGROUND_COLOR_HIGHLIGHTED,
                                       command=self.refresh,
                                       width=20,
                                       font=CTkFont(size=20, weight="bold"))
        self.reload_button.grid(row=3, column=2, pady=20, sticky='nw')


        # open, cancel, and delete button
        button_container = CTkFrame(self, fg_color=BACKGROUND_COLOR)
        button_container.grid(row=4, column=0, padx=20, pady=20, sticky='we')
        button_container.grid_columnconfigure((0,1), weight=0)
        button_container.grid_columnconfigure(2, weight=1)
        self.open_button = CTkButton(button_container, width=75,
                                     text='Open',
                                     command=self.open_button_handler)
        self.open_button.grid(row=0, column=0)
        self.cancel_button = CTkButton(button_container, width=75,
                                       text='Cancel',
                                       command=self.cancel_button_handler)
        self.cancel_button.grid(row=0, column=1, padx=3)
        self.delete_button = CTkButton(button_container, width=75,
                                       text='Delete',
                                       fg_color=WARNING_COLOR,
                                       hover_color=WARNING_COLOR_HIGHLIGHTED,
                                       command=self.delete_button_handler)
        self.delete_button.grid(row=0, column=3, sticky='e')

    def delete_button_handler(self):

        def confirm_delete():
            self.search_table.delete_entry(self.search_table.selected_entry)
        
        if self.search_table.selected_entry:
            try:
                ConfirmSelectionPrompt(self,
                                    prompt_text='Delete test entry?',
                                    confirm_command=confirm_delete)
            except SpawnPromptError:
                pass # prevent multiple prompts from spawning
        
    def open_button_handler(self):
        selected_test = self.search_table.selected_entry
        if selected_test:
            test_name = selected_test.test_entry.name
            entry = db_manager.load_existing_test_by_name(test_name)
            self.controller.context_frames[EditTestContextFrame].load_test_entry(entry)
            self.controller.show_frame(EditTestContextFrame)
    
    def cancel_button_handler(self):
        self.controller.show_frame(LandingContextFrame)
    
    def update(self):
        self.tag_container.load_tags(db_manager.list_existing_tags())

    def refresh(self):

        # get selected tags
        selected_tags = self.tag_container.get_selected_tag_values()

        # load tests matching tags if tags are selected
        if selected_tags:
            self.search_table.populate(db_manager.list_tests_by_tags(selected_tags))

        # otherwise load all tests 
        else:
            test_ids = db_manager.list_test_ids()
            if test_ids: 
                test_entries = []
                for id in test_ids:
                    test_entries.append(db_manager._load_test_by_id(id))

                self.search_table.populate(test_entries)

    def search(self, test_name):

        # populate with searched test or nothing if none found
        if test_name != '':
            searched_entry = [db_manager._load_test_by_name(test_name)]
            self.search_table.populate(searched_entry)

        # if search invoked with no search string, behave like refresh
        else:
            self.refresh()


class SearchField(CTkFrame):
    def __init__(self,
                 parent = None,
                 command: Callable[[str], None] = None):
        super().__init__(parent,
                         fg_color=BACKGROUND_COLOR)
        
        self.command = command

        self.grid_columnconfigure((0,1), weight=1)
        self.search_entry = CTkEntry(self, width=250,
                                placeholder_text='search by name',
                                fg_color=CONTAINER_COLOR,
                                border_color=CONTAINER_BORDER_COLOR)
        self.search_entry.grid(row=0, column=0, sticky='w')
        self.search_entry.bind("<Return>", self.search_button_handler)
        self.search_entry.bind("<Button-1>", self.search_entry_click)

        self.search_button = CTkButton(self, width=75,
                                  text='Search',
                                  command=self.search_button_handler)
        self.search_button.grid(row=0, column=1, padx=10)

    def search_button_handler(self, event=None):
        search_text = self.search_entry.get().strip()
        if self.command: self.command(search_text)

    def search_entry_click(self, event):
        self.search_entry.icursor(0)
        self.search_entry.select_range(0, 'end')


class SearchTestEntry(CTkFrame):
    def __init__(self, parent, controller, test_entry: TestEntry):
        super().__init__(parent, fg_color=ITEM_COLOR, border_width=1, border_color=ITEM_BORDER_COLOR)

        self.grid(row=0, column=0, padx=2, pady=2, sticky='ew')
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=0)
        self.grid_columnconfigure(4, weight=2)

        self.test_entry = test_entry
        self.controller = controller
        self.bind("<Button-1>", self.on_clicked)

        name = self.test_entry.name

        formatted_date = self.test_entry.creation_date.strftime("%m/%d/%Y")
        formatted_tags = ''

        num_tags = 0
        tags = self.test_entry.tags
        if tags:
            for tag in tags:

                num_tags += 1
                formatted_tags += str(tag)

                if num_tags < len(tags):
                    
                    # max shown tags is 3, use ... to indicate there are more than shown
                    if num_tags == 3:
                        formatted_tags += ', ...'
                        break

                    # separate displayed tags with comma
                    else:
                        formatted_tags += ', '

        entry_labels = [
            # text, padx, pady, sticky
            (name, 3, 3, None),
            ('|', 0, 3, None),
            (formatted_date, 3, 3, None),
            ('|', 0, 3, None),
            (formatted_tags, 3, 3, None)
        ]
        column=0
        for label in entry_labels:
            entry_label = CTkLabel(self,
                                    text=label[0],
                                    font=CTkFont(size=14, weight="bold"))
            entry_label.bind("<Button-1>", self.on_clicked)
            entry_label.grid(row=0,
                              column=column,
                              padx=label[1],
                              pady=label[2],
                              sticky=label[3])
            column += 1

    def on_clicked(self, event):
        self.controller.select(self)

    def select(self):
        self.configure(fg_color=ITEM_COLOR_HIGHLIGHTED)
        self.configure(border_color=ITEM_BORDER_COLOR_SELECTED)

    def deselect(self):
        self.configure(fg_color=ITEM_COLOR)
        self.configure(border_color=ITEM_BORDER_COLOR)


class SearchTable(CTkFrame):
    """Table containing the relevant test entries according to search criteria"""
    def __init__(self, parent):
        super().__init__(parent,
                         fg_color=CONTAINER_COLOR,
                         border_color=CONTAINER_BORDER_COLOR,
                         border_width=2,
                         height=370)
        
        self.num_entries = 0
        self.selected_entry = None
        self.entries = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        column_headers = CTkFrame(self, corner_radius=0)
        column_headers.grid(row=0, column=0, padx=2, pady=2, sticky='ew')
        column_headers.grid_rowconfigure(0, weight=0)
        column_headers.grid_columnconfigure(0, weight=1)
        column_headers.grid_columnconfigure(1, weight=0)
        column_headers.grid_columnconfigure(2, weight=1)
        column_headers.grid_columnconfigure(3, weight=0)
        column_headers.grid_columnconfigure(4, weight=2)

        #[name] [date] [tags]

        header_labels = [
            # text, padx, pady, sticky
            ('Name', 3, 3, None),
            ('|', 0, 3, None),
            ('Date', 3, 3, None),
            ('|', 0, 3, None),
            ('Tags', 3, 3, None)
        ]
        column=0
        for label in header_labels:
            header_label = CTkLabel(column_headers,
                                    text=label[0],
                                    font=CTkFont(size=14, weight="bold"))
            header_label.grid(row=0,
                              column=column,
                              padx=label[1],
                              pady=label[2],
                              sticky=label[3])
            column += 1

        self.scroll_container = CTkScrollableFrame(self,
                                                   fg_color='transparent')
        self.scroll_container.grid(row=1, column=0, padx=3, pady=3, sticky='nsew')
        self.scroll_container.grid_columnconfigure(0, weight=1)

        existing_test_ids = db_manager.list_test_ids()
        existing_test_entries = []

        if existing_test_ids:
            for id in existing_test_ids:
                test_entry = db_manager._load_test_by_id(id)
                existing_test_entries.append(test_entry)

        self.populate(existing_test_entries)

    def populate(self, test_entries: list[TestEntry]):

        # clear the table
        self.num_entries = 0
        
        for entry in self.entries:
            self.remove_entry(entry)

        self.entries = []

        if test_entries:
            for entry in test_entries:
                self.add_entry(entry)

    
    def select(self, entry: SearchTestEntry):

        if self.selected_entry == None:
            entry.select()
            self.selected_entry = entry
        else:
            if entry == self.selected_entry:
                self.selected_entry.deselect()
                self.selected_entry = None
            else:
                self.selected_entry.deselect()
                self.selected_entry = entry
                self.selected_entry.select()
    
    def add_entry(self, entry: TestEntry):
        
        entry_item = None

        if entry:
            entry_item = SearchTestEntry(self.scroll_container, self, entry)
            entry_item.grid(row=self.num_entries, column=0, sticky='new')
            self.entries.append(entry_item)
            self.num_entries += 1

    def remove_entry(self, entry: SearchTestEntry):

        if entry == self.selected_entry: self.selected_entry = None
        entry.destroy()

    def delete_entry(self, entry: SearchTestEntry):

        if entry:
            if entry == self.selected_entry: self.selected_entry = None
            db_manager.delete_test_entry_by_name(entry.test_entry.name)
            self.entries.remove(entry)
            entry.destroy()


class SettingsContextFrame(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # header label
        self.header_label = CTkLabel(self,
                                     text="Settings",
                                     font=CTkFont(size=20, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=20, pady=20, sticky='nsw')


class SpawnPromptError(Exception):
    """ Custom exception to indicate an attempt to spawn a prompt window when
        there is already one active. """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)        


class TextEntryPrompt(CTkToplevel):
    """A pop up window which prompts the user to enter a text string.
    
    Attributes
    ----------
    _PROMPT_ACTIVE : bool, private
        Indicates whether a prompt is currently active or not
    """

    _PROMPT_ACTIVE = False

    def __init__(self,
                 parent = None,
                 max_characters: int = 99,
                 prompt_text: str = 'Enter Text',
                 confirm_command: Callable[[str], None] = None,
                 cancel_command: Callable[[str], None] = None
                 ):
        """Constructs a pop-up window which prompts the user to enter a text string

        Parameters
        ----------
        parent : Any, optional
        max_characters: int, optional
            Limits the number of characters that may be submitted
        prompt_text : str, optional 
            The text displayed to the user on the prompt.
        confirm_command : callable, required 
            Executes when the user presses 'confirm'
            Must have this signature::

                callback(out_text: str) -> None

        cancel_command : callable, optional
            Executes when the user presses 'cancel'
        """

        super().__init__(parent)

        if TextEntryPrompt._PROMPT_ACTIVE:
            self.destroy()
            raise SpawnPromptError('A prompt is already active')
        else:
            TextEntryPrompt._PROMPT_ACTIVE = True

        self.parent = parent
        self.max_characters = max_characters
        self.confirm_command = confirm_command
        self.cancel_command = cancel_command

        self.title('Enter Text')
        self.geometry('300x120')
        self.resizable(False,False)
        self.attributes("-topmost", True)
        self.protocol('WM_DELETE_WINDOW', self.exit)
        self.focus_force()
        self.grid_columnconfigure((0,1), weight=1)
        self.grid_rowconfigure((0,1,3), weight=1)

        # prompt text
        self.prompt_text_label = CTkLabel(self,
                                          text=prompt_text,
                                          font=CTkFont(size=16))
        self.prompt_text_label.grid(row=0, column=0, columnspan=2, pady=15, sticky='nsew')

        # entry field
        self.text_entry = CTkEntry(self)
        self.text_entry.grid(row=1, column=0, columnspan=2, pady=10, padx=40, sticky='nsew')

        # buttons
        self.confirm_button = CTkButton(self,
                                        text='Confirm',
                                        command=self.confirm_button_handler,
                                        fg_color=CONFIRM_COLOR,
                                        hover_color=CONFIRM_COLOR_HIGHLIGHTED)
        self.confirm_button.grid(row=3, column=0, padx=10, pady=10, sticky='s')
        self.cancel_button = CTkButton(self,
                                       text='Cancel',
                                       command=self.cancel_button_handler,
                                       fg_color=WARNING_COLOR,
                                       hover_color=WARNING_COLOR_HIGHLIGHTED)
        self.cancel_button.grid(row=3, column=1, padx=10, pady=10, sticky='s')

        center_window(self)
        self.text_entry.focus_set()
        self.text_entry.bind('<Return>', self.confirm_button_handler)

    def confirm_button_handler(self, event=None):
        """Executed when the 'confirm' button is clicked.
        
        If the user attempts to enter too many characters, a warning label
        is displayed beneath the text entry to inform the user.

        Parameters
        ----------
        event: tkinter.event, optional
            Consumes a tkinter event if this function is bound to a widget
        """

        out_text = self.text_entry.get()

        if out_text.__len__() <= self.max_characters:
            # execute confirm command and exit
            try:
                self.confirm_command(out_text)
            except TypeError:
                logging.exception('No confirm_command provided')
            self.exit()

        else:
            # insert warning label beneath text_entry and persist pop-up
            warning_text = CTkLabel(self,
                                    text='Input can be no longer than\n{} characters'.format(self.max_characters),
                                    font=CTkFont(size=12),
                                    text_color=WARNING_COLOR)
            warning_text.grid(row=2, column=0, columnspan=2)

    def cancel_button_handler(self):
        """Executed when the 'cancel' button is clicked."""

        if self.cancel_command: self.cancel_command(self.text_entry.get())
        self.exit()

    def exit(self):
        """Called to close the current instance of ConfirmSelectionPrompt"""
        TextEntryPrompt._PROMPT_ACTIVE = False
        self.destroy()


class ConfirmSelectionPrompt(CTkToplevel):
    """ A pop up window which prompts the user to confirm or deny an action.
    
    Attributes
    ----------
    _PROMPT_ACTIVE : bool, private
        Indicates whether a prompt is currently active or not
    """

    _PROMPT_ACTIVE = False

    def __init__(self,
                 parent,
                 prompt_text: str='Confirm Selection?',
                 confirm_command: Callable[[], None]=None,
                 cancel_command: Callable[[], None]=None
                 ):
        """ Constructs a pop-up window which prompts a user to confirm or deny an action.

        Parameters
        ----------
        parent : Any, optional
        prompt_text : str, optional 
            The text displayed to the user on the prompt.
        confirm_command : callable, required 
            Executes when the user presses 'confirm'
        cancel_command : callable, optional
            Executes when the user presses 'cancel'
        """

        super().__init__(parent)

        # ensure there are no other instances of 'ConfirmSelectionPrompt'
        # currently existing
        if ConfirmSelectionPrompt._PROMPT_ACTIVE:
            self.destroy()
            raise SpawnPromptError('A prompt is already active')
        else:
            ConfirmSelectionPrompt._PROMPT_ACTIVE = True

        self.parent = parent
        self.confirm_command = confirm_command
        self.cancel_command = cancel_command

        self.title('Confirm Selection')
        self.geometry('300x120')
        self.resizable(False,False)
        self.attributes("-topmost", True)
        self.protocol('WM_DELETE_WINDOW', self.exit)
        self.grid_columnconfigure((0,1), weight=1)
        self.grid_rowconfigure((0,1), weight=1)

        # prompt text
        self.prompt_text_label = CTkLabel(self,
                                          text=prompt_text,
                                          font=CTkFont(size=16))
        self.prompt_text_label.grid(row=0, column=0, columnspan=2, pady=25, sticky='nsew')

        # buttons
        self.confirm_button = CTkButton(self, 
                                        text='Confirm',
                                        command=self.confirm_button_handler,
                                        fg_color=CONFIRM_COLOR,
                                        hover_color=CONFIRM_COLOR_HIGHLIGHTED)
        self.confirm_button.grid(row=1, column=0, padx=10, pady=10, sticky='s')

        self.cancel_button = CTkButton(self,
                                       text='Cancel',
                                       command=self.cancel_button_handler,
                                       fg_color=WARNING_COLOR,
                                       hover_color=WARNING_COLOR_HIGHLIGHTED)
        self.cancel_button.grid(row=1, column=1, padx=10, pady=10, sticky='s')

        center_window(self)

    def confirm_button_handler(self):
        """Executed when the 'confirm' button is clicked."""

        try:
            self.confirm_command()
        except TypeError:
            logging.exception('No confirm_command provided')
        self.exit()

    def cancel_button_handler(self):
        """Executed when the 'cancel' button is clicked."""

        if self.cancel_command: self.cancel_command()
        self.exit()

    def exit(self):
        """Called to close the current instance of ConfirmSelectionPrompt"""

        ConfirmSelectionPrompt._PROMPT_ACTIVE = False 
        self.destroy()


def center_window(toplevel: CTkToplevel):
    """ Position the window provided in the center of the screen """

    screen_width = toplevel.winfo_screenwidth()
    screen_height = toplevel.winfo_screenheight()

    window_width = toplevel.winfo_width()
    window_height = toplevel.winfo_height()

    x = int((screen_width/2) - (window_width/2))
    y = int((screen_height/2) - (window_height/2))

    toplevel.geometry("{}x{}+{}+{}".format(window_width, window_height, x, y))


if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()