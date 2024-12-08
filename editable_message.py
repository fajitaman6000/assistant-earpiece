import tkinter as tk
from tkinter import ttk, Text

class EditableMessage(ttk.Frame):
    def __init__(self, parent, content, role, in_context=True, on_edit=None):
        super().__init__(parent)
        self.content = content  # Store original content
        self.role = role
        self.on_edit = on_edit
        self.is_editing = False
        self.in_context = in_context
        
        self.role_colors = {
            "user": ("#0056b3", "#e6f3ff"),      # Blue: text color, background
            "assistant": ("#cc7000", "#fff5e6"),  # Orange: text color, background
            "system": ("#d32f2f", "#ffebee")      # Red: text color, background
        }
        
        self.setup_widgets()
        
    def setup_widgets(self):
        # Header frame for role and context indicator
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(fill=tk.X, padx=5, pady=(5,0))
        
        # Role label (You/Claude/System)
        role_display = "You" if self.role == "user" else "Claude" if self.role == "assistant" else "System"
        self.role_label = ttk.Label(
            self.header_frame,
            text=role_display,
            foreground=self.role_colors[self.role][0]
        )
        self.role_label.pack(side=tk.LEFT)
        
        # Context indicator (if out of context)
        if not self.in_context:
            self.context_label = ttk.Label(
                self.header_frame,
                text="OUT OF CONTEXT WINDOW",
                foreground="#d32f2f",
                font=("TkDefaultFont", 9, "bold")
            )
            self.context_label.pack(side=tk.RIGHT)
        
        # Message content frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Style for background color
        style_name = f'message.{self.role}.TFrame'
        style = ttk.Style()
        style.configure(style_name, background=self.role_colors[self.role][1])
        self.content_frame.configure(style=style_name)
        
        # Message content label
        self.message_label = ttk.Label(
            self.content_frame,
            text=self.content,
            wraplength=700,
            justify='left',
            background=self.role_colors[self.role][1]
        )
        self.message_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Edit text widget (hidden initially)
        self.text_widget = Text(
            self.content_frame,
            wrap=tk.WORD,
            height=4,
            width=80,
            background=self.role_colors[self.role][1]
        )
        
        # Scrollbar for text widget
        self.scrollbar = ttk.Scrollbar(
            self.content_frame, 
            orient="vertical", 
            command=self.text_widget.yview
        )
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)
        
        # Bindings
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
            self.text_widget.insert('1.0', self.content)
            self.text_widget.focus_set()
            self.adjust_text_height()
            
    def stop_editing(self, event=None):
        if self.is_editing:
            self.is_editing = False
            new_content = self.text_widget.get('1.0', 'end-1c').rstrip()
            self.content = new_content  # Update stored content
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
        """Get current message content"""
        return self.content