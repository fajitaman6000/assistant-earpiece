import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import anthropic # type: ignore
import json
import os
from chat_display import EditableChatDisplay
from multiline_input import MultilineInput
import base64

class ClaudeChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Claude Chat Interface")
        self.root.geometry("750x800")
        
        api_key = self.load_api_key()
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None
        
        self.context_size = 10
        self.api_context = []
        self.full_history = []
        
        self.create_widgets()
        self.create_pdf_frame()  # Add this line after create_widgets()

    def create_pdf_frame(self):
        """Create frame for PDF selection controls with centered filename"""
        # Create main frame
        pdf_frame = ttk.LabelFrame(self.root, text="PDF Document")
        pdf_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # Left side - Include PDF button
        self.pdf_button = ttk.Button(pdf_frame, text="Include PDF", command=self.select_pdf)
        self.pdf_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Right side - Clear button
        self.clear_pdf_button = ttk.Button(pdf_frame, text="Clear Current File", command=self.clear_pdf)
        self.clear_pdf_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Center - Filename label (pack after buttons to fill remaining space)
        self.pdf_label = ttk.Label(pdf_frame, text="Current File: None", anchor="center")
        self.pdf_label.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Initialize PDF tracking variables
        self.current_pdf_path = None
        self.current_pdf_data = None


    def select_pdf(self):
        """Handle PDF file selection"""
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    pdf_data = f.read()
                    self.current_pdf_path = file_path
                    self.current_pdf_data = base64.b64encode(pdf_data).decode('utf-8')
                    filename = os.path.basename(file_path)
                    self.pdf_label.configure(text=f"Current File: {filename}")
            except Exception as e:
                self.full_history.append({
                    "role": "system", 
                    "content": f"Error loading PDF: {str(e)}"
                })
                self.refresh_display()
                self.current_pdf_path = None
                self.current_pdf_data = None
                self.pdf_label.configure(text="Current: None")

    def clear_pdf(self):
        """Clear the current PDF selection"""
        self.current_pdf_path = None
        self.current_pdf_data = None
        self.pdf_label.configure(text="Current: None")

    def get_context_size(self):
        """Helper method to safely get current context size"""
        try:
            return max(0, int(self.context_size_var.get()))
        except (ValueError, AttributeError):
            return 10  # default value

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
        
        # Chat display area
        # Create a container frame for fixed height
        self.chat_container = ttk.Frame(self.root, height=400)
        self.chat_container.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.chat_container.pack_propagate(False)  # Prevent size changes
        
        # Create the chat display inside the container
        self.chat_display = EditableChatDisplay(
            self.chat_container,
            get_context_size=self.get_context_size,
            on_message_edit=self.handle_message_edit
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        self.input_frame = ttk.Frame(self.root)
        self.input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # Using MultilineInput with submit callback
        self.message_input = MultilineInput(
            self.input_frame, 
            on_submit=self.send_message,
            min_height=30, 
            max_height=150
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # System message area
        system_frame = ttk.LabelFrame(self.root, text="Persistent Context/Instructions")
        system_frame.pack(padx=10, pady=3, fill=tk.X)
        
        self.system_input = scrolledtext.ScrolledText(system_frame, wrap=tk.WORD, height=5)
        self.system_input.pack(padx=5, pady=10, fill=tk.X)

    def save_conversation(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            current_history = []
            for i, msg in enumerate(self.full_history):
                if i < len(self.chat_display.messages):
                    current_content = self.chat_display.messages[i].get_content()
                    current_history.append({
                        "role": msg["role"],
                        "content": current_content
                    })
                else:
                    current_history.append(msg)
            
            save_data = {
                "history": current_history,
                "system_message": self.system_input.get("1.0", tk.END).strip(),
                "settings": {
                    "temperature": self.temperature_var.get(),
                    "max_tokens": self.tokens_var.get(),
                    "context_size": self.context_size_var.get()
                },
                "pdf": {
                    "path": self.current_pdf_path,
                    "data": self.current_pdf_data
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
                    
                    if "system_message" in data:
                        self.system_input.delete("1.0", tk.END)
                        self.system_input.insert("1.0", data["system_message"])
                    
                    if "settings" in data:
                        settings = data["settings"]
                        self.temperature_var.set(settings.get("temperature", "0.7"))
                        self.tokens_var.set(settings.get("max_tokens", "1024"))
                        self.context_size_var.set(settings.get("context_size", "10"))
                        self.update_context_size()
                    
                    # Load PDF data if present
                    if "pdf" in data and isinstance(data["pdf"], dict):
                        pdf_path = data["pdf"].get("path")
                        pdf_data = data["pdf"].get("data")
                        
                        if pdf_path and pdf_data:
                            if os.path.exists(pdf_path):
                                self.current_pdf_path = pdf_path
                                self.current_pdf_data = pdf_data
                                filename = os.path.basename(pdf_path)
                                self.pdf_label.configure(text=f"Current: {filename}")
                            else:
                                self.current_pdf_path = None
                                self.current_pdf_data = None
                                self.pdf_label.configure(text="Current: None")
                                
                file_name = os.path.basename(file_path)
                self.root.title(f"Claude - Loaded: {file_name}")
                    
                self.refresh_display()
            except Exception as e:
                self.full_history.append({"role": "system", "content": f"Error loading file: {str(e)}"})
                self.refresh_display()
    
    def update_context_size(self):
        try:
            self.context_size = max(0, int(self.context_size_var.get()))
            # Add this line to refresh context indicators when context size changes
            self.chat_display.refresh_context_indicators()
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
        """Handle sending a message to Claude API with proper PDF handling"""
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
            
        self.message_input.delete()
        
        try:
            temperature = float(self.temperature_var.get())
            max_tokens = int(self.tokens_var.get())
            system_message = self.system_input.get("1.0", tk.END).strip()
            
            # Get context messages first
            context_messages = self.get_context_messages()
            
            # Prepare the new user message with PDF if present
            if self.current_pdf_data:
                new_message = {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": self.current_pdf_data
                            },
                            "cache_control": {"type": "ephemeral"}
                        },
                        {
                            "type": "text",
                            "text": user_msg_content
                        }
                    ]
                }
            else:
                new_message = {
                    "role": "user",
                    "content": user_msg_content
                }
            
            # Add the new message to context or use it alone if no context
            messages_for_api = context_messages if context_messages else []
            messages_for_api.append(new_message)
            
            # Store simplified version in history for display
            self.full_history.append({
                "role": "user",
                "content": user_msg_content
            })
            
            # Make API call
            api_params = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages_for_api
            }
            
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
        """Refresh the chat display with current messages and context indicators"""
        # If this is the first refresh, populate the display
        if len(self.chat_display.messages) == 0:
            total_messages = len(self.full_history)
            context_size = self.context_size  # Get current context size
            
            for i, msg in enumerate(self.full_history):
                # Calculate if message should be in context
                # Last context_size messages should be in context
                in_context = i >= (total_messages - context_size)
                self.chat_display.add_message(msg, msg["role"])
                
            # Force a refresh of context indicators
            self.chat_display.refresh_context_indicators()
            
        # Otherwise, just add any new messages
        elif len(self.full_history) > len(self.chat_display.messages):
            # Get the new messages
            new_messages = self.full_history[len(self.chat_display.messages):]
            for msg in new_messages:
                self.chat_display.add_message(msg, msg["role"])
            
            # Refresh context indicators to ensure proper display
            self.chat_display.refresh_context_indicators()

    def reset_new_chat_button(self):
        """Reset the new chat button to its default state"""
        self.new_chat_button.configure(text="New Chat", style="TButton")
        self.confirm_new_chat = False

    def new_chat(self):
        if not hasattr(self, 'confirm_new_chat'):
            self.confirm_new_chat = False
            
        if not self.confirm_new_chat:
            self.confirm_new_chat = True
            style = ttk.Style()
            style.configure('Red.TButton', background='red')
            self.new_chat_button.configure(text="Confirm", style="Red.TButton")
            self.root.after(2000, self.reset_new_chat_button)
            
        else:
            self.confirm_new_chat = False
            self.full_history = []
            self.api_context = []
            self.root.title("Claude Chat Interface")
            self.system_input.delete("1.0", tk.END)
            self.temperature_var.set("1.0")
            self.tokens_var.set("1024")
            self.context_size_var.set("10")
            self.context_size = 10
            # Reset PDF selection
            self.current_pdf_path = None
            self.current_pdf_data = None
            self.pdf_label.configure(text="Current: None")
            self.chat_display.clear()
            self.reset_new_chat_button()
            self.refresh_display()