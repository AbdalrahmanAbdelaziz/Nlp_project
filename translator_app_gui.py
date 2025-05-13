import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from transformers import MarianMTModel, MarianTokenizer
import torch
import os
import threading

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Translingo")
        self.root.geometry("1000x700")
        self.root.minsize(900, 650)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Load models
        self.load_models()
        
        # Create UI
        self.create_widgets()
        
        # Dark mode toggle
        self.dark_mode = False
        
    def configure_styles(self):
        """Configure custom styles for widgets"""
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10), padding=6)
        self.style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))
        self.style.configure('Status.TLabel', font=('Helvetica', 9), foreground='#666666')
        self.style.map('TButton',
                      foreground=[('pressed', 'white'), ('active', 'white')],
                      background=[('pressed', '#0052cc'), ('active', '#0066ff')])
        
    def load_models(self):
        """Load translation models in a separate thread"""
        self.models_loaded = False
        self.loading_thread = threading.Thread(target=self._load_models_thread, daemon=True)
        self.loading_thread.start()
        
    def _load_models_thread(self):
        """Thread function for loading models"""
        try:
            # Arabic to English model (your fine-tuned model)
            self.model_ar_en = MarianMTModel.from_pretrained("./marian-ar-en-finetuned")
            self.tokenizer_ar_en = MarianTokenizer.from_pretrained("./marian-ar-en-finetuned")
            
            # English to Arabic model (pretrained)
            self.model_en_ar = MarianMTModel.from_pretrained("./opus-mt-en-ar")
            self.tokenizer_en_ar = MarianTokenizer.from_pretrained("./opus-mt-en-ar")
            
            self.models_loaded = True
            self.update_status("Models loaded successfully", success=True)
        except Exception as e:
            self.update_status(f"Model loading failed: {str(e)}", error=True)
            messagebox.showerror("Error", f"Failed to load models: {str(e)}")
            
    def create_widgets(self):
        """Create all UI widgets"""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.title_label = ttk.Label(
            self.header_frame, 
            text="Translingo", 
            style='Header.TLabel'
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Theme toggle button
        self.theme_btn = ttk.Button(
            self.header_frame,
            text="☀️",
            command=self.toggle_theme,
            width=3
        )
        self.theme_btn.pack(side=tk.RIGHT, padx=5)
        
        
        # Translation direction
        self.direction_frame = ttk.Frame(self.main_frame)
        self.direction_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.direction_var = tk.StringVar(value="Arabic to English")
        
        self.ar_to_en_btn = ttk.Radiobutton(
            self.direction_frame,
            text="Arabic → English",
            variable=self.direction_var,
            value="Arabic to English",
            style='Toolbutton'
        )
        self.ar_to_en_btn.pack(side=tk.LEFT, padx=5)
        
        self.en_to_ar_btn = ttk.Radiobutton(
            self.direction_frame,
            text="English → Arabic",
            variable=self.direction_var,
            value="English to Arabic",
            style='Toolbutton'
        )
        self.en_to_ar_btn.pack(side=tk.LEFT, padx=5)
        
        # Swap button
        self.swap_btn = ttk.Button(
            self.direction_frame,
            text="⇄ Swap",
            command=self.swap_direction,
            style='TButton'
        )
        self.swap_btn.pack(side=tk.RIGHT, padx=5)
        
        # Text areas
        self.text_frame = ttk.Frame(self.main_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input text
        self.input_frame = ttk.Frame(self.text_frame)
        self.input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.input_label = ttk.Label(self.input_frame, text="Input Text:")
        self.input_label.pack(anchor=tk.W)
        
        self.input_text = tk.Text(
            self.input_frame,
            height=20,
            wrap=tk.WORD,
            font=('Helvetica', 12),
            padx=10,
            pady=10,
            undo=True
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Input buttons
        self.input_btn_frame = ttk.Frame(self.input_frame)
        self.input_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.clear_input_btn = ttk.Button(
            self.input_btn_frame,
            text="Clear",
            command=lambda: self.input_text.delete("1.0", tk.END)
        )
        self.clear_input_btn.pack(side=tk.LEFT, padx=2)
        
        self.paste_btn = ttk.Button(
            self.input_btn_frame,
            text="Paste",
            command=self.paste_text
        )
        self.paste_btn.pack(side=tk.LEFT, padx=2)
        
        
        # Output text
        self.output_frame = ttk.Frame(self.text_frame)
        self.output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.output_label = ttk.Label(self.output_frame, text="Translation:")
        self.output_label.pack(anchor=tk.W)
        
        self.output_text = tk.Text(
            self.output_frame,
            height=20,
            wrap=tk.WORD,
            font=('Helvetica', 12),
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Output buttons
        self.output_btn_frame = ttk.Frame(self.output_frame)
        self.output_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.copy_btn = ttk.Button(
            self.output_btn_frame,
            text="Copy",
            command=self.copy_translation
        )
        self.copy_btn.pack(side=tk.LEFT, padx=2)
        
        
        # Action buttons
        self.action_frame = ttk.Frame(self.main_frame)
        self.action_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.translate_btn = ttk.Button(
            self.action_frame,
            text="Translate",
            command=self.start_translation,
            style='Accent.TButton'
        )
        self.translate_btn.pack(pady=5, ipadx=20, ipady=5)
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame, height=25)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_var,
            style='Status.TLabel',
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X)
        
        # Configure text tags for RTL support
        self.input_text.tag_configure('rtl', justify='right')
        self.output_text.tag_configure('rtl', justify='right')
        
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            # Dark theme colors
            bg_color = '#2d2d2d'
            fg_color = '#ffffff'
            text_bg = '#3d3d3d'
            text_fg = '#ffffff'
            self.theme_btn.config(text="🌙")
        else:
            # Light theme colors
            bg_color = '#f0f0f0'
            fg_color = '#000000'
            text_bg = '#ffffff'
            text_fg = '#000000'
            self.theme_btn.config(text="☀️")
        
        # Update all widgets
        self.style.configure('.', background=bg_color, foreground=fg_color)
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color)
        self.style.configure('TButton', background=bg_color)
        self.style.configure('Status.TLabel', foreground='#aaaaaa')
        
        # Update text widgets
        self.input_text.config(
            bg=text_bg,
            fg=text_fg,
            insertbackground=fg_color
        )
        self.output_text.config(
            bg=text_bg,
            fg=text_fg,
            insertbackground=fg_color
        )
        
    def swap_direction(self):
        """Swap translation direction"""
        current = self.direction_var.get()
        if current == "Arabic to English":
            self.direction_var.set("English to Arabic")
        else:
            self.direction_var.set("Arabic to English")
            
    def start_translation(self):
        """Start translation in a separate thread"""
        if not self.models_loaded:
            messagebox.showwarning("Warning", "Models are still loading. Please wait.")
            return
            
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text to translate")
            return
            
        self.update_status("Translating...")
        self.translate_btn.config(state=tk.DISABLED)
        
        # Start translation in a separate thread
        translation_thread = threading.Thread(
            target=self.translate_text,
            args=(text,),
            daemon=True
        )
        translation_thread.start()
        
    def translate_text(self, text):
        """Perform the actual translation"""
        try:
            direction = self.direction_var.get()
            
            if direction == "Arabic to English":
                inputs = self.tokenizer_ar_en(
                    text,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=128
                )
                with torch.no_grad():
                    translated = self.model_ar_en.generate(**inputs)
                result = self.tokenizer_ar_en.decode(translated[0], skip_special_tokens=True)
            else:
                inputs = self.tokenizer_en_ar(
                    text,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=128
                )
                with torch.no_grad():
                    translated = self.model_en_ar.generate(**inputs)
                result = self.tokenizer_en_ar.decode(translated[0], skip_special_tokens=True)
            
            # Update UI in main thread
            self.root.after(0, self.display_translation, result)
            self.root.after(0, self.update_status, "Translation completed", success=True)
            
        except Exception as e:
            self.root.after(0, self.update_status, f"Translation failed: {str(e)}", error=True)
            self.root.after(0, messagebox.showerror, "Error", f"Translation failed: {str(e)}")
            
        finally:
            self.root.after(0, lambda: self.translate_btn.config(state=tk.NORMAL))
            
    def display_translation(self, text):
        """Display translated text in the output box"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)
        
        # Set text direction based on language
        if self.direction_var.get() == "Arabic to English":
            self.output_text.tag_add('ltr', '1.0', tk.END)
        else:
            self.output_text.tag_add('rtl', '1.0', tk.END)
            
        self.output_text.config(state=tk.DISABLED)
        
    def update_status(self, message, success=False, error=False):
        """Update status bar with message"""
        self.status_var.set(message)
        if success:
            self.status_label.config(foreground='green')
        elif error:
            self.status_label.config(foreground='red')
        else:
            self.status_label.config(foreground='#666666')
            
    def paste_text(self):
        """Paste text from clipboard"""
        try:
            text = self.root.clipboard_get()
            self.input_text.insert(tk.END, text)
        except tk.TclError:
            messagebox.showwarning("Warning", "No text in clipboard")
            
    def copy_translation(self):
        """Copy translation to clipboard"""
        text = self.output_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.update_status("Translation copied to clipboard", success=True)
        
    def save_translation(self):
        """Save translation to file"""
        text = self.output_text.get("1.0", tk.END)
        if not text.strip():
            messagebox.showwarning("Warning", "No translation to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.update_status(f"Translation saved to {file_path}", success=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
                self.update_status("Save failed", error=True)
                
    def load_from_file(self):
        """Load text from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", text)
                self.update_status(f"Loaded text from {file_path}", success=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                self.update_status("Load failed", error=True)

if __name__ == "__main__":
    root = tk.Tk()
        
    app = TranslatorApp(root)
    root.mainloop()