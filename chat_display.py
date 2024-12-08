import tkinter as tk
from tkinter import ttk
from editable_message import EditableMessage

class EditableChatDisplay(ttk.Frame):
    def __init__(self, parent, get_context_size, on_message_edit=None):
        super().__init__(parent)
        self.on_message_edit = on_message_edit
        self.get_context_size = get_context_size
        self.messages = []
        
        # Create scrollable area
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling behavior
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_frame = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack elements - NOTE: Order is important!
        self.scrollbar.pack(side="right", fill="y")  # Pack scrollbar first
        self.canvas.pack(side="left", fill="both", expand=True)  # Then canvas
        
        # Bind events
        self.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind_mouse_wheel()
        
    def _on_frame_configure(self, event=None):
        width = self.winfo_width() - self.scrollbar.winfo_width()
        self.canvas.configure(width=width)
        
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
        
    def bind_mouse_wheel(self):
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def add_message(self, message, role):
        """Add a new message to the display"""
        total_messages = len(self.messages)
        context_size = self.get_context_size()
        in_context = total_messages >= (len(self.messages) - context_size)
        
        msg_widget = EditableMessage(
            self.scrollable_frame,
            message["content"],
            role,
            in_context=in_context,
            on_edit=lambda content: self._handle_edit(len(self.messages), content)
        )
        msg_widget.pack(fill=tk.X, padx=5, pady=2)
        self.messages.append(msg_widget)
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
        
    def refresh_context_indicators(self):
        """Refresh which messages show context indicators"""
        total_messages = len(self.messages)
        context_size = self.get_context_size()
        
        for i, msg_widget in enumerate(self.messages):
            in_context = i >= (total_messages - context_size)
            if msg_widget.in_context != in_context:
                msg_widget.update_context_status(in_context)
                
    def _handle_edit(self, index, new_content):
        """Handle message editing"""
        if self.on_message_edit:
            self.on_message_edit(index, new_content)
            
    def clear(self):
        """Clear all messages"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.messages = []
        self.canvas.yview_moveto(0.0)