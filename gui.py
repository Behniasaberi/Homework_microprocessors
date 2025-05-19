import tkinter as tk
from tkinter import messagebox
import subprocess

# Define valid username and password
VALID_USERNAME = "Behnia"
VALID_PASSWORD = "87243131"

# Function to validate login credentials
def login():
    username = entry_username.get()
    password = entry_password.get()
    
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        messagebox.showinfo("Login Successful", "Launching Calculator...")
        # Launch Windows Calculator
        subprocess.Popen("calc.exe")
        window.destroy()  # Close the login window
    else:
        messagebox.showerror("Error", "Invalid username or password!")

# Create the main window
window = tk.Tk()
window.title("Login Form")
window.geometry("300x180")
window.resizable(False, False)

# Username label and entry field
tk.Label(window, text="Username:").pack(pady=(20, 0))
entry_username = tk.Entry(window)
entry_username.pack()

# Password label and entry field
tk.Label(window, text="Password:").pack(pady=(10, 0))
entry_password = tk.Entry(window, show="*")
entry_password.pack()

# Login button
tk.Button(window, text="Login", command=login).pack(pady=20)

# Start the GUI loop
window.mainloop()
