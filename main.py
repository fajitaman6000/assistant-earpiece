# ============================================================
# === REPLACE THE ENTIRE CONTENTS OF main.py WITH THIS CODE ===
# === MAKE SURE TO PUT THIS IN main.py, NOT ANY OTHER FILE ====
# ============================================================

import tkinter as tk
from chat_app import ClaudeChatApp
import os
from PIL import Image, ImageTk  # Make sure to pip install pillow
import sys
import ctypes

def create_ico_from_png(png_path, ico_path):
    """Convert PNG to ICO if needed"""
    if not os.path.exists(ico_path) and os.path.exists(png_path):
        img = Image.open(png_path)
        # Convert RGBA to RGB if needed
        if img.mode == 'RGBA':
            bg = Image.new('RGB', img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        # Save as ICO
        img.save(ico_path, format='ICO', sizes=[(32, 32)])

def set_windows_taskbar_icon(window, icon_path):
    """Set the Windows taskbar icon explicitly"""
    if sys.platform == 'win32':
        try:
            # Get the window handle
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            # Load the icon
            icon_handle = ctypes.windll.user32.LoadImageW(
                None,
                icon_path,
                1,  # IMAGE_ICON
                0,
                0,
                0x00000010 | 0x00000040  # LR_LOADFROMFILE | LR_DEFAULTSIZE
            )
            # Set the icon for both the window and the taskbar
            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, icon_handle)  # WM_SETICON
            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, icon_handle)  # WM_SETICON
        except Exception as e:
            print(f"Could not set Windows taskbar icon: {e}")

def main():
    root = tk.Tk()
    
    # Set up icon paths
    icon_png = "claude_icon.png"  # Your PNG icon
    icon_ico = "claude_icon.ico"  # Windows ICO version
    
    # Try to convert PNG to ICO if needed (for Windows)
    create_ico_from_png(icon_png, icon_ico)
    
    # Set window icon - try different formats based on OS
    try:
        # For Windows: use ICO file and set taskbar icon
        if sys.platform == 'win32' and os.path.exists(icon_ico):
            root.iconbitmap(icon_ico)
            # Wait for window to be created before setting taskbar icon
            root.after(10, lambda: set_windows_taskbar_icon(root, icon_ico))
        # For Linux/Mac: use PNG file
        elif os.path.exists(icon_png):
            icon = tk.PhotoImage(file=icon_png)
            root.iconphoto(True, icon)
    except Exception as e:
        print(f"Could not set icon: {e}")
    
    app = ClaudeChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()