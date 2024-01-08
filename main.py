
# windows xp style interface
from tkinter import *

# create the main window

root = Tk()
root.title("Instagram Bot")
root.geometry("400x400")
root.resizable(False, False)
root.configure(bg="black")

# create the frame
frame = Frame(root, bg="black")
frame.pack(expand=True)

# create the label
label = Label(frame, text="Instagram Bot", font=(
    "Arial", 30), bg="black", fg="white")
label.pack(pady=20)

# create the button
button = Button(frame, text="Start", font=(
    "Arial", 20), bg="black", fg="white")
button.pack(pady=20)

# create the entry
entry = Entry(frame, font=("Arial", 20), bg="black", fg="white")
entry.pack(pady=20)
