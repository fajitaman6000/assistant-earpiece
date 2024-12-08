################################################################
# COMPLETELY REPLACE EVERYTHING IN chat_display.py WITH THIS CODE #
# DELETE ALL CURRENT CONTENTS OF chat_display.py                 #
# PASTE EVERYTHING BETWEEN THESE COMMENT BLOCKS                  #
################################################################

import tkinter as tk
from tkinter import ttk
from editable_message import EditableMessage

class ContextScrollCanvas(tk.Canvas):
    def __init__(self, parent, messages, get_context_size, width=12):
        super().__init__(parent, width=width, highlightthickness=0)
        self.messages = messages
        self.get_context_size = get_context_size
        self._width = width
        # Softer colors for better visual comfort
        self.thumb_color = 'gray75'
        self.out_of_context_color = '#ffcdd2'  # Lighter, more pastel red
        self.in_context_color = 'gray85'
        self.bind('<Configure>', self._on_configure)
        
    def set(self, start, end):
        """Draw the scrollbar with context indicators"""
        self.delete('all')  # Clear canvas
        
        # Draw background (trough)
        self.create_rectangle(0, 0, self._width, self.winfo_height(), 
                            fill='lightgray', width=0)
        
        if not self.messages:
            return
            
        height = self.winfo_height()
        total_messages = len(self.messages)
        context_size = self.get_context_size()
        
        # Adjust context visualization to match visible area more accurately
        # We offset the context boundary by approximately one visible page
        visible_portion = float(end) - float(start)
        context_start = max(0, total_messages - context_size)
        
        # Calculate the visual offset to align context boundary with content
        offset_factor = visible_portion * 0.8  # Adjust this factor to fine-tune alignment
        
        # Draw context indicators with adjusted positioning
        msg_height = height / total_messages if total_messages > 0 else height
        for i in range(total_messages):
            y1 = i * msg_height
            y2 = (i + 1) * msg_height
            
            # Adjust the visual boundary by shifting it up slightly
            adjusted_i = i + (context_size * offset_factor)
            color = self.out_of_context_color if adjusted_i < context_start else self.in_context_color
            self.create_rectangle(0, y1, self._width, y2, fill=color, width=0)
            
        # Draw scrollbar thumb
        thumb_height = max(20, height * visible_portion)
        thumb_top = height * float(start)
        self.create_rectangle(0, thumb_top, self._width, thumb_top + thumb_height,
                            fill=self.thumb_color, width=0)
                            
    def _on_configure(self, event):
        self._width = event.width

################################################################
# NOTE: THE REST OF THE FILE REMAINS EXACTLY THE SAME AS BEFORE  #
# CONTINUING WITH EditableChatDisplay CLASS...                   #
################################################################

class EditableChatDisplay(ttk.Frame):
    def __init__(self, parent, get_context_size, on_message_edit=None):
        super().__init__(parent)
        self.on_message_edit = on_message_edit
        self.get_context_size = get_context_size
        self.messages = []
        
        # Create scrollable area
        self.canvas = tk.Canvas(self)
        self.scrollbar_canvas = ContextScrollCanvas(self, self.messages, self.get_context_size)
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
        self.canvas.configure(yscrollcommand=self._on_scroll)
        
        # Bind scrollbar canvas events
        self.scrollbar_canvas.bind('<Button-1>', self._on_scrollbar_click)
        self.scrollbar_canvas.bind('<B1-Motion>', self._on_scrollbar_drag)
        
        # Pack elements
        self.scrollbar_canvas.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind events
        self.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind_mouse_wheel()
        
    def _on_scroll(self, *args):
        """Handle scroll events"""
        self.canvas.yview(*('moveto', args[0]))
        self.scrollbar_canvas.set(*args)
        
    def _on_scrollbar_click(self, event):
        """Handle clicking on the scrollbar"""
        height = self.scrollbar_canvas.winfo_height()
        thumb_height = max(20, height * 0.1)  # Minimum thumb size
        click_pos = event.y / height
        
        # Move view to clicked position
        self.canvas.yview_moveto(max(0, min(1, click_pos - thumb_height/height/2)))
        
    def _on_scrollbar_drag(self, event):
        """Handle dragging the scrollbar"""
        height = self.scrollbar_canvas.winfo_height()
        click_pos = max(0, min(1, event.y / height))
        self.canvas.yview_moveto(click_pos)
        
    def _on_frame_configure(self, event=None):
        width = self.winfo_width() - self.scrollbar_canvas.winfo_width()
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
        self.scrollbar_canvas.set(*self.canvas.yview())
        
    def refresh_context_indicators(self):
        """Refresh which messages show context indicators"""
        total_messages = len(self.messages)
        context_size = self.get_context_size()
        
        for i, msg_widget in enumerate(self.messages):
            in_context = i >= (total_messages - context_size)
            if msg_widget.in_context != in_context:
                msg_widget.update_context_status(in_context)
                
        # Update scrollbar indicators
        self.scrollbar_canvas.set(*self.canvas.yview())
                
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
        self.scrollbar_canvas.set(0, 1)

################################################################
# END OF COMPLETE REPLACEMENT FOR chat_display.py                #
# MAKE SURE EVERYTHING ABOVE IS COPIED                          #
################################################################