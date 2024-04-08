from typing import Callable
from customtkinter import (
    CTkToplevel,
    CTkFrame,
    CTkButton,
    CTkLabel,
    CTkFont,
    CTkEntry
)
import logging

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


class ConfirmationPrompt(CTkToplevel):
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
        if ConfirmationPrompt._PROMPT_ACTIVE:
            self.destroy()
            raise SpawnPromptError('A prompt is already active')
        else:
            ConfirmationPrompt._PROMPT_ACTIVE = True

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

        ConfirmationPrompt._PROMPT_ACTIVE = False 
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
