import tkinter as tk
from tkinter import scrolledtext
import time
import threading
import ctypes
import random
import win32api
import win32con
import win32gui

# Virtual key codes for special keys
VK_RETURN = 0x0D
VK_TAB = 0x09
VK_SPACE = 0x20

class AutoTyperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Typer - Bypass Paste Detection")
        self.root.geometry("450x480")
        
        # Variables
        self.typing_active = False
        self.stop_typing = False
        
        # Main frame
        main_frame = tk.Frame(root, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Auto Typer - Bypass Paste Detection", 
                             font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Text input
        input_frame = tk.LabelFrame(main_frame, text="Text to Type")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.input_text = scrolledtext.ScrolledText(input_frame, width=45, height=8)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Options frame
        options_frame = tk.LabelFrame(main_frame, text="Options")
        options_frame.pack(fill=tk.X, pady=5)
        
        # Wait time
        wait_frame = tk.Frame(options_frame)
        wait_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(wait_frame, text="Wait time:").pack(side=tk.LEFT)
        
        self.wait_var = tk.IntVar(value=5)
        wait_options = [3, 5, 10, 15]
        for i, opt in enumerate(wait_options):
            tk.Radiobutton(wait_frame, text=f"{opt}s", variable=self.wait_var, 
                          value=opt).pack(side=tk.LEFT, padx=5)
        
        # Instantaneous typing option
        self.instant_var = tk.BooleanVar(value=False)
        instant_check = tk.Checkbutton(options_frame, text="Instantaneous typing (no delay between characters)", 
                                     variable=self.instant_var, command=self.update_options_state)
        instant_check.pack(anchor="w", pady=5)
        
        # Tab handling options
        tab_frame = tk.LabelFrame(options_frame, text="Tab Handling")
        tab_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.tab_var = tk.StringVar(value="preserve")
        tk.Radiobutton(tab_frame, text="Preserve tabs", variable=self.tab_var, 
                      value="preserve").pack(anchor="w")
        tk.Radiobutton(tab_frame, text="Replace with 2 spaces", variable=self.tab_var, 
                      value="spaces2").pack(anchor="w")
        tk.Radiobutton(tab_frame, text="Replace with 4 spaces", variable=self.tab_var, 
                      value="spaces4").pack(anchor="w")
        
        # Speed control
        speed_frame = tk.Frame(options_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        
        self.speed_label = tk.Label(speed_frame, text="Typing Speed:")
        self.speed_label.pack(side=tk.LEFT)
        
        self.speed_var = tk.DoubleVar(value=0.05)
        self.speed_scale = tk.Scale(speed_frame, from_=0.01, to=0.2, resolution=0.01, 
                               variable=self.speed_var, orient=tk.HORIZONTAL, 
                               length=200)
        self.speed_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.faster_label = tk.Label(speed_frame, text="Faster")
        self.faster_label.pack(side=tk.LEFT)
        
        # Human-like typing
        self.human_var = tk.BooleanVar(value=True)
        self.human_check = tk.Checkbutton(options_frame, text="Human-like typing (variable speed)", 
                      variable=self.human_var)
        self.human_check.pack(anchor="w", pady=5)
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(button_frame, text="Start Typing", 
                                    command=self.start_typing,
                                    bg="#4CAF50", fg="white", 
                                    font=("Arial", 10, "bold"),
                                    width=15, height=1)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = tk.Button(button_frame, text="Stop", 
                                   command=self.stop_typing_command,
                                   bg="#F44336", fg="white",
                                   width=15, height=1)
        self.stop_button.pack(side=tk.LEFT)
        self.stop_button.config(state=tk.DISABLED)
        
        # Status frame
        status_frame = tk.LabelFrame(main_frame, text="Status")
        status_frame.pack(fill=tk.X, pady=5)
        
        # Countdown label
        self.countdown_var = tk.StringVar(value="")
        self.countdown_label = tk.Label(status_frame, textvariable=self.countdown_var,
                                      font=("Arial", 10, "bold"), fg="red")
        self.countdown_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, fg="blue")
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Initialize UI state
        self.update_options_state()
    
    def update_options_state(self):
        # Enable/disable options based on instantaneous mode
        is_instant = self.instant_var.get()
        state = tk.DISABLED if is_instant else tk.NORMAL
        
        self.speed_scale.config(state=state)
        self.human_check.config(state=state)
        self.speed_label.config(state=state)
        self.faster_label.config(state=state)
    
    def start_typing(self):
        # Get text from input
        text_to_type = self.input_text.get("1.0", tk.END).strip()
        
        if not text_to_type:
            self.status_var.set("Please enter text to type!")
            return
        
        if self.typing_active:
            return
        
        # Start typing process in a separate thread
        self.typing_thread = threading.Thread(target=self.typing_process, args=(text_to_type,))
        self.typing_thread.daemon = True
        self.stop_typing = False
        self.typing_thread.start()
    
    def stop_typing_command(self):
        self.stop_typing = True
        self.status_var.set("Stopping...")
    
    def send_key(self, vk_code):
        """Send a virtual key code"""
        hwnd = win32gui.GetForegroundWindow()
        # Send key down
        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
        # Send key up
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
    
    def send_char(self, char):
        """Send a character"""
        hwnd = win32gui.GetForegroundWindow()
        char_code = ord(char)
        win32api.PostMessage(hwnd, win32con.WM_CHAR, char_code, 0)
    
    def type_spaces(self, count):
        """Type a specific number of spaces"""
        hwnd = win32gui.GetForegroundWindow()
        for _ in range(count):
            win32api.PostMessage(hwnd, win32con.WM_CHAR, ord(' '), 0)
    
    def typing_process(self, text_to_type):
        # Set typing as active
        self.typing_active = True
        
        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Get wait time
        wait_time = self.wait_var.get()
        self.status_var.set(f"Get ready to position your cursor! Typing will begin in {wait_time} seconds...")
        
        # Start countdown
        self.countdown_thread = threading.Thread(target=self.countdown, args=(wait_time,))
        self.countdown_thread.daemon = True
        self.countdown_thread.start()
        
        # Wait for countdown
        time.sleep(wait_time)
        
        # Reset countdown
        self.countdown_var.set("")
        
        # Check if stopped
        if self.stop_typing:
            self.cleanup()
            return
        
        # Start typing
        self.status_var.set("Typing in progress...")
        
        try:
            # Get settings
            base_delay = self.speed_var.get()
            human_like = self.human_var.get()
            instantaneous = self.instant_var.get()
            tab_handling = self.tab_var.get()
            
            # Process tab handling
            if tab_handling == "spaces2":
                tab_replacement = "  "  # 2 spaces
            elif tab_handling == "spaces4":
                tab_replacement = "    "  # 4 spaces
            else:
                tab_replacement = None  # Preserve tabs
            
            # Type each character
            char_count = 0
            i = 0
            
            while i < len(text_to_type):
                if self.stop_typing:
                    break
                
                char = text_to_type[i]
                i += 1
                char_count += 1
                
                # Handle special characters
                if char == '\n':
                    # Send Enter key
                    self.send_key(VK_RETURN)
                elif char == '\t':
                    if tab_replacement:
                        # Replace tab with spaces
                        self.type_spaces(len(tab_replacement))
                    else:
                        # Send Tab key
                        self.send_key(VK_TAB)
                else:
                    # Regular character
                    self.send_char(char)
                
                # Calculate delay - skip delay if instantaneous mode is enabled
                if not instantaneous:
                    if human_like:
                        # Random variations for more natural typing
                        if random.random() < 0.01:  # 1% chance of pause
                            time.sleep(random.uniform(0.3, 0.7))
                        
                        delay = base_delay + random.uniform(-0.3 * base_delay, 0.3 * base_delay)
                        
                        # Pause longer after punctuation and line breaks
                        if char in ['.', ',', '!', '?', ';', ':', '\n'] and random.random() < 0.8:
                            delay += random.uniform(0.1, 0.3)
                    else:
                        delay = base_delay
                    
                    time.sleep(delay)
                else:
                    # Minimal delay to allow messages to be processed
                    time.sleep(0.001)
                
                # Update status occasionally
                if char_count % 20 == 0:
                    self.status_var.set(f"Typing in progress... ({char_count}/{len(text_to_type)} chars)")
            
            # Final status update
            if not self.stop_typing:
                self.status_var.set(f"Typing completed! ({char_count} characters)")
            else:
                self.status_var.set("Typing stopped by user")
                
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
        finally:
            self.cleanup()
    
    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            if self.stop_typing:
                break
            self.countdown_var.set(f"⏱️ Countdown: {i} seconds")
            time.sleep(1)
        self.countdown_var.set("")
    
    def cleanup(self):
        # Reset UI state
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.typing_active = False

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoTyperApp(root)
    root.mainloop()