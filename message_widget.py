import tkinter as tk
from tkinter import ttk, Text

class EditableMessage(ttk.Frame):
    def __init__(self, parent, message, role, on_edit=None):
        super().__init__(parent)
        self.message = message
        self.role = role
        self.on_edit = on_edit
        self.is_editing = False
        
        self.role_colors = {
            "user": ("#0056b3", "#e6f3ff"),
            "assistant": ("#2e7d32", "#f1f8e9"),
            "system": ("#d32f2f", "#ffebee")
        }
        
        self.setup_widgets()
        
    def setup_widgets(self):
        role_display = "You" if self.role == "user" else "Claude" if self.role == "assistant" else "System"
        header = ttk.Label(
            self,
            text=role_display,
            foreground=self.role_colors[self.role][0]
        )
        header.pack(anchor='w', padx=5, pady=(5,0))
        
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.X, padx=5, pady=5)
        self.content_frame.configure(style='message.TFrame')
        
        style = ttk.Style()
        style.configure(
            'message.TFrame',
            background=self.role_colors[self.role][1]
        )
        
        self.message_label = ttk.Label(
            self.content_frame,
            text=self.message,
            wraplength=700,
            justify='left',
            background=self.role_colors[self.role][1]
        )
        self.message_label.pack(fill=tk.X, padx=5, pady=5)
        
        self.text_widget = Text(
            self.content_frame,
            wrap=tk.WORD,
            height=4,
            width=80,
            background=self.role_colors[self.role][1]
        )
        
        self.scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)
        
        self.message_label.bind('<Button-1>', self.start_editing)
        self.text_widget.bind('<FocusOut>', self.stop_editing)
        self.text_widget.bind('<Return>', lambda e: self.stop_editing(e) if not e.state & 0x1 else None)
        
    def start_editing(self, event=None):
        if not self.is_editing:
            self.is_editing = True
            self.message_label.pack_forget()
            self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
            self.text_widget.delete('1.0', tk.END)
            self.text_widget.insert('1.0', self.message_label.cget('text'))
            self.text_widget.focus_set()
            self.adjust_text_height()
            
    def stop_editing(self, event=None):
        if self.is_editing:
            self.is_editing = False
            new_content = self.text_widget.get('1.0', 'end-1c').rstrip()
            self.message_label.configure(text=new_content)
            self.text_widget.pack_forget()
            self.scrollbar.pack_forget()
            self.message_label.pack(fill=tk.X, padx=5, pady=5)
            if self.on_edit:
                self.on_edit(new_content)
                
    def adjust_text_height(self):
        num_lines = int(self.text_widget.index('end-1c').split('.')[0])
        self.text_widget.configure(height=max(4, min(num_lines, 20)))
            
    def get_content(self):
        if self.is_editing:
            return self.text_widget.get('1.0', 'end-1c')
        return self.message_label.cget('text')