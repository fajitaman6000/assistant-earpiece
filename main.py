import tkinter as tk
from chat_app import ClaudeChatApp

def main():
    root = tk.Tk()
    app = ClaudeChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()