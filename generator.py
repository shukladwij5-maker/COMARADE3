import tkinter as tk
from tkinter import messagebox, scrolledtext
import google.generativeai as genai
import os
import threading

# Configuration: Please set your API key here.
API_KEY = "AIzaSyB0saJEwa-yULzN1hUXpdZDXCfZsYvRW4s"

class CommandGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CMD/PS Generator")
        self.root.geometry("600x650")
        self.root.configure(bg="#1e1e1e")

        # UI Styling constants
        self.header_font = ("Segoe UI", 14, "bold")
        self.label_font = ("Segoe UI", 10)
        self.mono_font = ("Consolas", 11)
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.input_bg = "#2d2d2d"
        self.btn_bg = "#3c3c3c"

        self.setup_ui()

        if not API_KEY:
            messagebox.showwarning("API Key Missing", 
                "Please set the GEMINI_API_KEY environment variable for the script to function correctly.")

    def setup_ui(self):
        # Input Section
        tk.Label(self.root, text="Describe what you want to do:", 
                 font=self.label_font, bg=self.bg_color, fg=self.fg_color).pack(pady=(20, 5), padx=20, anchor="w")
        
        self.prompt_entry = tk.Entry(self.root, font=self.mono_font, bg=self.input_bg, fg=self.fg_color, 
                                     insertbackground="white", borderwidth=0)
        self.prompt_entry.pack(fill="x", padx=20, pady=5, ipady=8)
        self.prompt_entry.bind("<Return>", lambda e: self.generate())

        self.gen_btn = tk.Button(self.root, text="Generate Commands", font=self.label_font, 
                                 bg=self.btn_bg, fg=self.fg_color, command=self.generate, 
                                 borderwidth=0, activebackground="#4c4c4c", cursor="hand2")
        self.gen_btn.pack(pady=15, padx=20, fill="x")

        # PowerShell Section
        tk.Label(self.root, text="PowerShell:", font=self.label_font, bg=self.bg_color, fg="#00a1f1").pack(padx=20, anchor="w")
        self.ps_output = scrolledtext.ScrolledText(self.root, height=8, font=self.mono_font, bg=self.input_bg, 
                                                   fg=self.fg_color, borderwidth=0)
        self.ps_output.pack(fill="both", padx=20, pady=5, expand=True)

        # CMD Section
        tk.Label(self.root, text="CMD:", font=self.label_font, bg=self.bg_color, fg="#ffba08").pack(padx=20, anchor="w", pady=(10, 0))
        self.cmd_output = scrolledtext.ScrolledText(self.root, height=8, font=self.mono_font, bg=self.input_bg, 
                                                    fg=self.fg_color, borderwidth=0)
        self.cmd_output.pack(fill="both", padx=20, pady=5, expand=True)

        # Status
        self.status_label = tk.Label(self.root, text="Ready", font=("Segoe UI", 9), bg=self.bg_color, fg="#888888")
        self.status_label.pack(pady=10)

    def update_status(self, text, color="#888888"):
        self.status_label.config(text=text, fg=color)

    def generate(self):
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            return
        
        if not API_KEY:
            messagebox.showerror("Error", "Gemini API key is required.")
            return

        self.update_status("Generating...", "#00a1f1")
        self.gen_btn.config(state="disabled")
        
        # Run in thread to keep GUI responsive
        threading.Thread(target=self.call_gemini, args=(prompt,), daemon=True).start()

    def call_gemini(self, user_prompt):
        try:
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            system_instruction = (
                "You are a translator that converts natural language into Windows shell commands. "
                "Provide the most accurate and safe command for the user's intent. "
                "Return exactly this format without markdown code blocks:\n"
                "---PS---\n"
                "[PowerShell Command]\n"
                "---CMD---\n"
                "[CMD Command]"
            )
            
            response = model.generate_content(f"{system_instruction}\n\nUser Intent: {user_prompt}")
            text = response.text.strip()
            
            ps_cmd = ""
            cmd_cmd = ""
            
            if "---PS---" in text and "---CMD---" in text:
                parts = text.split("---CMD---")
                ps_cmd = parts[0].replace("---PS---", "").strip()
                cmd_cmd = parts[1].strip()
            else:
                ps_cmd = text # Fallback

            self.root.after(0, lambda: self.display_results(ps_cmd, cmd_cmd))
        except Exception as e:
            self.root.after(0, lambda: self.show_error(str(e)))

    def display_results(self, ps, cmd):
        self.ps_output.delete("1.0", tk.END)
        self.ps_output.insert(tk.END, ps)
        
        self.cmd_output.delete("1.0", tk.END)
        self.cmd_output.insert(tk.END, cmd)
        
        self.update_status("Done!", "#4caf50")
        self.gen_btn.config(state="normal")

    def show_error(self, err):
        messagebox.showerror("API Error", err)
        self.update_status("Error occurred", "#f44336")
        self.gen_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = CommandGeneratorApp(root)
    root.mainloop()
