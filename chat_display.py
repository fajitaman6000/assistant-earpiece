import tkinter as tk
from tkinter import ttk
from editable_message import EditableMessage

class EditableChatDisplay(ttk.Frame):
    def __init__(self, parent, get_context_size, on_message_edit=None):
        super().__init__(parent)
        self.on_message_edit = on_message_edit
        self.get_context_size = get_context_size  # Store the getter method
        self.messages = []
        
        self.pack_propagate(False)
        
        self.canvas = tk.Canvas(self, height=400)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.canvas.winfo_width())
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        self.bind_mouse_wheel()
        
    def _on_frame_configure(self, event=None):
        self.canvas.configure(width=self.winfo_width()-self.scrollbar.winfo_width())
        
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
        
        # Calculate if message is in context window
        # Last context_size messages should be in context
        # i.e., if we have 5 messages and context size is 3,
        # messages at indices 2,3,4 should be in context
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
        
        # Store current content and state
        saved_messages = []
        for msg in self.messages:
            saved_messages.append({
                'content': msg.get_content(),
                'role': msg.role
            })
            
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Rebuild messages with updated context status
        self.messages = []
        for i in range(len(saved_messages)):
            saved_msg = saved_messages[i]
            # Last context_size messages should be in context
            in_context = i >= (total_messages - context_size)
            
            msg_widget = EditableMessage(
                self.scrollable_frame,
                saved_msg['content'],
                saved_msg['role'],
                in_context=in_context,
                on_edit=lambda content, idx=i: self._handle_edit(idx, content)
            )
            msg_widget.pack(fill=tk.X, padx=5, pady=2)
            self.messages.append(msg_widget)
        
    def _handle_edit(self, index, new_content):
        if self.on_message_edit:
            self.on_message_edit(index, new_content)
            
    def clear(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.messages = []
        self.canvas.yview_moveto(0.0)