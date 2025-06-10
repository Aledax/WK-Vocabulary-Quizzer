import tkinter, sys
from tkinter import messagebox
from tkinter import filedialog
import win32gui
tkinter.Tk().wm_withdraw()

# These helper functions provide functionality that occurs outside of the main PyGame
# window using Tkinter (as PyGame does not support it.)

WINDOW_NAME = "SAS Instrument Dashboard"

def window_enumeration_handler(hwnd, windows):
    windows.append((hwnd, win32gui.GetWindowText(hwnd)))

def return_to_parent_window(parent_window_name: str = None):
    if not parent_window_name: parent_window_name = WINDOW_NAME
    windows = []
    win32gui.EnumWindows(window_enumeration_handler, windows)
    for i in windows:
        if i[1] == parent_window_name:
            win32gui.ShowWindow(i[0], 5)
            win32gui.SetForegroundWindow(i[0])
            break

def information(message, parent_window_name: str = None):
    messagebox.showinfo(title = "INFORMATION", message = message)
    return_to_parent_window(parent_window_name)

def confirmation(message, parent_window_name: str = None):
    result = messagebox.askyesno(title = "CONFIRMATION", message = message)
    return_to_parent_window(parent_window_name)
    return result

def choosefile(parent_window_name: str = None):
    result = filedialog.askopenfilename()
    return_to_parent_window(parent_window_name)
    return result

def choosedirectory(parent_window_name: str = None):
    result = filedialog.askdirectory()
    return_to_parent_window(parent_window_name)
    return result