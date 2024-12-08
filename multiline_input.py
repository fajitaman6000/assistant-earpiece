# ================================================================
# === DELETE EVERYTHING IN multiline_input.py =====================
# === PASTE EVERYTHING BETWEEN THESE COMMENT BLOCKS ==============
# === THIS IS THE COMPLETE NEW FILE CONTENTS ====================
# === FILE: multiline_input.py (ENTIRE FILE) ====================
# ================================================================

import tkinter as tk
from tkinter import ttk

class MultilineInput(ttk.Frame):
    def __init__(self, parent, on_submit=None, min_height=50, max_height=150, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Store the submit callback
        self.on_submit = on_submit
        
        # Create text widget
        self.text = tk.Text(
            self,
            wrap=tk.WORD,
            width=1,
            height=2,
            undo=True,
            padx=5,
            pady=5,
            background='white',
            relief=tk.FLAT,
            exportselection=1,
            spacing1=2,
            spacing2=2,
            spacing3=2
        )
        
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # Remove ALL default key bindings
        for sequence in ["<Return>", "<Shift-Return>", "<KP_Enter>", "<Shift-KP_Enter>"]:
            self.text.unbind(sequence)
            self.text.unbind_class("Text", sequence)
        
        # Add our own key bindings
        self.text.bind("<Return>", self._handle_return)
        self.text.bind("<Shift-Return>", self._handle_shift_return)
        self.text.bind("<KeyRelease>", self._handle_key_release)
        
        # Initialize state
        self.last_content = ""
        
    def _handle_return(self, event):
        """Handle regular Return key - submits the message"""
        if self.on_submit and self.get().strip():
            self.on_submit()
        return "break"
    
    def _handle_shift_return(self, event):
        """Handle Shift+Return - inserts a newline"""
        self.text.insert(tk.INSERT, '\n')
        return "break"
    
    def _handle_key_release(self, event):
        """Handle updating the height on any key release"""
        self._adjust_height()
    
    def _adjust_height(self):
        """Adjust the height of the text widget based on content"""
        content = self.text.get("1.0", "end-1c")
        
        if content != self.last_content:
            self.last_content = content
            
            # Count actual lines
            lines = content.split('\n')
            line_count = len(lines)
            
            # Add lines for text wrapping
            for line in lines:
                wrap_count = (len(line) // 50)
                line_count += wrap_count
            
            # Set height between 2 and 12 lines
            new_height = min(max(2, line_count), 12)
            self.text.configure(height=new_height)
    
    def get(self):
        """Get the current content"""
        return self.text.get("1.0", "end-1c")
    
    def delete(self, *args):
        """Clear the text widget"""
        self.text.delete("1.0", "end")
        self.last_content = ""
        self.text.configure(height=2)
    
    def focus_set(self):
        """Set focus to the text widget"""
        self.text.focus_set()
    
    def bind(self, sequence=None, func=None, add=None):
        """Override bind to prevent external key bindings"""
        if sequence in ["<Return>", "<Shift-Return>", "<KP_Enter>", "<Shift-KP_Enter>"]:
            return
        self.text.bind(sequence, func, add)

# ================================================================
# === END OF multiline_input.py =================================
# === NO OTHER CODE SHOULD BE IN THIS FILE =====================
# ================================================================