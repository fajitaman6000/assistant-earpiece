import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import anthropic # type: ignore
import json
import os
from chat_display import EditableChatDisplay

class ClaudeChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Claude Chat Interface")
        self.root.geometry("750x600")
        
        api_key = self.load_api_key()
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None
        
        self.context_size = 10
        self.api_context = []
        self.full_history = []
        
        self.create_widgets()
        
    def load_api_key(self):
        """Load API key from file or create the file if it doesn't exist."""
        try:
            # Try to read the API key
            with open('api_key.txt', 'r') as f:
                api_key = f.read().strip()
                
            # Check if the file is empty
            if not api_key:
                raise FileNotFoundError()
                
            return api_key
            
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open('api_key.txt', 'w') as f:
                pass  # Create empty file
                
            # Add a system message to the history about needing an API key
            if not hasattr(self, 'full_history'):
                self.full_history = []
            self.full_history.append({
                "role": "system",
                "content": "Anthropic API key needed! Paste your key into api_key.txt in the same directory as this program, or generate one first at https://console.anthropic.com/dashboard"
            })
            
            return None

    def handle_message_edit(self, index, new_content):
        # Update the content in full_history
        if 0 <= index < len(self.full_history):
            self.full_history[index]["content"] = new_content
        
    def setup_tags(self):
        self.chat_display.tag_configure("active_context", background="#e6f3ff")
        self.chat_display.tag_configure("user", foreground="#0056b3")
        self.chat_display.tag_configure("assistant", foreground="#2e7d32")
        self.chat_display.tag_configure("system", foreground="#d32f2f")
        
    def create_widgets(self):
        # Top settings frame
        settings_frame = ttk.LabelFrame(self.root, text="Settings")
        settings_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # Temperature control
        ttk.Label(settings_frame, text="Temperature:").pack(side=tk.LEFT, padx=5)
        self.temperature_var = tk.StringVar(value="1.0")
        self.temperature_spinbox = ttk.Spinbox(
            settings_frame,
            from_=0.0,
            to=1.0,
            increment=0.1,
            width=5,
            textvariable=self.temperature_var
        )
        self.temperature_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Token length control
        ttk.Label(settings_frame, text="Max Tokens:").pack(side=tk.LEFT, padx=5)
        self.tokens_var = tk.StringVar(value="1024")
        self.tokens_spinbox = ttk.Spinbox(
            settings_frame,
            from_=1,
            to=4096,
            increment=100,
            width=6,
            textvariable=self.tokens_var
        )
        self.tokens_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Context size control
        ttk.Label(settings_frame, text="Context Size:").pack(side=tk.LEFT, padx=5)
        self.context_size_var = tk.StringVar(value="10")
        self.context_size_spinbox = ttk.Spinbox(
            settings_frame,
            from_=0,
            to=999999,
            increment=2,
            width=6,
            textvariable=self.context_size_var,
            command=self.update_context_size
        )
        self.context_size_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Save/Load buttons
        self.save_button = ttk.Button(settings_frame, text="Save Chat", command=self.save_conversation)
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        self.load_button = ttk.Button(settings_frame, text="Load Chat", command=self.load_conversation)
        self.load_button.pack(side=tk.RIGHT, padx=5)

        self.new_chat_button = ttk.Button(settings_frame, text="New Chat", command=self.new_chat)
        self.new_chat_button.pack(side=tk.RIGHT, padx=5)
        
        # Chat display area - using new EditableChatDisplay
        self.chat_display = EditableChatDisplay(self.root, on_message_edit=self.handle_message_edit)
        self.chat_display.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Input area
        self.input_frame = ttk.Frame(self.root)
        self.input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.message_input = ttk.Entry(self.input_frame)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # System message area
        system_frame = ttk.LabelFrame(self.root, text="Persistent Context/Instructions")
        system_frame.pack(padx=10, pady=3, fill=tk.X)
        
        self.system_input = scrolledtext.ScrolledText(system_frame, wrap=tk.WORD, height=5)
        self.system_input.pack(padx=5, pady=10, fill=tk.X)
        
        self.message_input.bind('<Return>', lambda e: self.send_message())

    def save_conversation(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            # Create a copy of history with current edited content
            current_history = []
            for i, msg in enumerate(self.full_history):
                if i < len(self.chat_display.messages):
                    # Get current edited content for displayed messages
                    current_content = self.chat_display.messages[i].get_content()
                    current_history.append({
                        "role": msg["role"],
                        "content": current_content
                    })
                else:
                    # Use original content for any messages not yet displayed
                    current_history.append(msg)
            
            save_data = {
                "history": current_history,  # Use the updated history with edits
                "system_message": self.system_input.get("1.0", tk.END).strip(),
                "settings": {
                    "temperature": self.temperature_var.get(),
                    "max_tokens": self.tokens_var.get(),
                    "context_size": self.context_size_var.get()
                }
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f)
    
    def load_conversation(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.new_chat()

                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.full_history = data["history"]
                    
                    # Load system message if present
                    if "system_message" in data:
                        self.system_input.delete("1.0", tk.END)
                        self.system_input.insert("1.0", data["system_message"])
                    
                    # Load settings if present
                    if "settings" in data:
                        settings = data["settings"]
                        self.temperature_var.set(settings.get("temperature", "0.7"))
                        self.tokens_var.set(settings.get("max_tokens", "1024"))
                        self.context_size_var.set(settings.get("context_size", "10"))
                        self.update_context_size()
                    
                # Update window title with loaded file name
                file_name = os.path.basename(file_path)
                self.root.title(f"Claude - Loaded: {file_name}")
                    
                self.refresh_display()
            except Exception as e:
                self.full_history.append({"role": "system", "content": f"Error loading file: {str(e)}"})
                self.refresh_display()
    
    def update_context_size(self):
        try:
            self.context_size = max(0, int(self.context_size_var.get()))
            self.refresh_display()
        except ValueError:
            self.full_history.append({"role": "system", "content": "Error: Invalid context size value"})
            self.refresh_display()
    
    def get_context_messages(self):
        if self.context_size == 0:
            return []
        
        # Get the last context_size messages from full_history
        context_slice = self.full_history[-self.context_size:]
        
        # Create a list of messages with current edited content
        context_messages = []
        start_idx = len(self.full_history) - len(context_slice)
        
        for i, msg in enumerate(context_slice):
            display_idx = start_idx + i
            if display_idx < len(self.chat_display.messages):
                # Use the current edited content from the display
                edited_content = self.chat_display.messages[display_idx].get_content()
                context_messages.append({
                    "role": msg["role"],
                    "content": edited_content
                })
            else:
                # Use the original content for any new messages
                context_messages.append(msg)
        
        return context_messages
    
    def send_message(self):
        # Check if we have a valid client
        if not self.client:
            self.full_history.append({
                "role": "system",
                "content": "Cannot send message: No valid API key found. Please add your API key to api_key.txt"
            })
            self.refresh_display()
            return
            
        user_msg_content = self.message_input.get().strip()
        if not user_msg_content:
            return
            
        self.message_input.delete(0, tk.END)
        
        user_msg = {"role": "user", "content": user_msg_content}
        self.full_history.append(user_msg)
        
        try:
            temperature = float(self.temperature_var.get())
            max_tokens = int(self.tokens_var.get())
            system_message = self.system_input.get("1.0", tk.END).strip()
            
            # Get messages for API call, including any edited content
            context_messages = self.get_context_messages()
            if len(context_messages) == 0:
                context_messages = [user_msg]
            
            # Make API call with system parameter as a string
            api_params = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": context_messages
            }
            
            # Only add system parameter if there's a system message
            if system_message:
                api_params["system"] = system_message
            
            response = self.client.messages.create(**api_params)
            
            claude_message = self.format_claude_response(response.content)
            assistant_msg = {"role": "assistant", "content": claude_message}
            self.full_history.append(assistant_msg)
            
        except Exception as e:
            error_msg = {"role": "system", "content": f"Error: {str(e)}"}
            self.full_history.append(error_msg)
        
        self.refresh_display()
    
    def format_claude_response(self, response):
        if isinstance(response, str):
            return response
        if isinstance(response, dict) and 'text' in response:
            return response['text']
        if hasattr(response, 'text'):
            return response.text
        try:
            if isinstance(response, (list, tuple)):
                return ' '.join(str(block.text) if hasattr(block, 'text') else str(block) for block in response)
        except:
            pass
        return str(response)
    
    def refresh_display(self):
        # If this is the first refresh, populate the display
        if len(self.chat_display.messages) == 0:
            for msg in self.full_history:
                self.chat_display.add_message(msg, msg["role"])
        # Otherwise, just add the new message
        elif len(self.full_history) > len(self.chat_display.messages):
            # Get the new messages
            new_messages = self.full_history[len(self.chat_display.messages):]
            for msg in new_messages:
                self.chat_display.add_message(msg, msg["role"])

    def reset_new_chat_button(self):
        """Reset the new chat button to its default state"""
        self.new_chat_button.configure(text="New Chat", style="TButton")
        self.confirm_new_chat = False

    def new_chat(self):
        if not hasattr(self, 'confirm_new_chat'):
            self.confirm_new_chat = False
            
        if not self.confirm_new_chat:
            # First click - show confirmation state
            self.confirm_new_chat = True
            
            # Create a custom style for the red button
            style = ttk.Style()
            style.configure('Red.TButton', background='red')
            
            # Change button appearance
            self.new_chat_button.configure(text="Confirm", style="Red.TButton")
            
            # Schedule reset after 2 seconds
            self.root.after(2000, self.reset_new_chat_button)
            
        else:
            # Second click - perform new chat operations
            self.confirm_new_chat = False
            
            # Clear chat history
            self.full_history = []
            # Clear API context
            self.api_context = []
            # Reset window title
            self.root.title("Claude Chat Interface")
            # Clear system message
            self.system_input.delete("1.0", tk.END)
            # Reset settings to defaults
            self.temperature_var.set("1.0")
            self.tokens_var.set("1024")
            self.context_size_var.set("10")
            self.context_size = 10
            # Clear the chat display
            self.chat_display.clear()
            # Reset button appearance
            self.reset_new_chat_button()
            # Refresh display to ensure everything is clean
            self.refresh_display()