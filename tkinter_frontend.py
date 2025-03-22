import os
import json
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import requests
import threading
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("frontend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CalibrationAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calibration Analyzer Client")
        self.root.geometry("1200x800")
        
        # API URL
        self.api_url = "http://localhost:8000"  # Default API server URL
        
        # Setup UI components
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # File selection
        ttk.Label(control_frame, text="Certificate PDF:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.file_path_var, width=50).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Browse...", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)
        
        # API URL input
        ttk.Label(control_frame, text="API URL:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.api_url_var = tk.StringVar(value=self.api_url)
        ttk.Entry(control_frame, textvariable=self.api_url_var, width=50).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Custom instructions input
        ttk.Label(control_frame, text="Custom Instructions:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.custom_instructions_text = scrolledtext.ScrolledText(control_frame, wrap=tk.WORD, height=4)
        self.custom_instructions_text.grid(row=2, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # Process button
        self.analyze_button = ttk.Button(control_frame, text="Analyze Certificate", command=self.analyze_certificate)
        self.analyze_button.grid(row=3, column=2, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.RIGHT, padx=5)
        
        # Results notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Full response tab
        response_frame = ttk.Frame(notebook)
        notebook.add(response_frame, text="Full Response")
        
        self.response_text = scrolledtext.ScrolledText(response_frame, wrap=tk.WORD)
        self.response_text.pack(fill=tk.BOTH, expand=True)
        
        # Verdict tab
        verdict_frame = ttk.Frame(notebook)
        notebook.add(verdict_frame, text="Verdict")
        
        verdict_inner_frame = ttk.Frame(verdict_frame, padding="20")
        verdict_inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Verdict information - large and prominent
        ttk.Label(verdict_inner_frame, text="Verdict:", font=("Arial", 16, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.verdict_var = tk.StringVar(value="N/A")
        ttk.Label(verdict_inner_frame, textvariable=self.verdict_var, font=("Arial", 16, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(verdict_inner_frame, text="Confidence:", font=("Arial", 14)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.confidence_var = tk.StringVar(value="N/A")
        ttk.Label(verdict_inner_frame, textvariable=self.confidence_var, font=("Arial", 14)).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(verdict_inner_frame, text="Summary:", font=("Arial", 14)).grid(row=2, column=0, sticky=tk.NW, padx=5, pady=5)
        self.summary_text = scrolledtext.ScrolledText(verdict_inner_frame, wrap=tk.WORD, height=5, font=("Arial", 12))
        self.summary_text.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Specifications tab
        spec_frame = ttk.Frame(notebook)
        notebook.add(spec_frame, text="Specifications")
        
        # Split the specifications tab into sections
        spec_frame_top = ttk.Frame(spec_frame)
        spec_frame_top.pack(fill=tk.X, padx=5, pady=5)
        
        # Add a section for specification sources
        ttk.Label(spec_frame_top, text="Specifications Source:", font=("Arial", 12, "bold")).pack(anchor=tk.W, padx=5, pady=5)
        self.spec_source_var = tk.StringVar(value="No source information available")
        ttk.Label(spec_frame_top, textvariable=self.spec_source_var, font=("Arial", 11)).pack(anchor=tk.W, padx=15, pady=5)
        
        ttk.Separator(spec_frame, orient='horizontal').pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Label(spec_frame_top, text="Specification Details:", font=("Arial", 12, "bold")).pack(anchor=tk.W, padx=5, pady=5)
        
        self.spec_text = scrolledtext.ScrolledText(spec_frame, wrap=tk.WORD)
        self.spec_text.pack(fill=tk.BOTH, expand=True)
        
        # Calculations tab
        calc_frame = ttk.Frame(notebook)
        notebook.add(calc_frame, text="Calculations")
        
        self.calculations_text = scrolledtext.ScrolledText(calc_frame, wrap=tk.WORD)
        self.calculations_text.pack(fill=tk.BOTH, expand=True)
        
        # Discrepancies tab
        disc_frame = ttk.Frame(notebook)
        notebook.add(disc_frame, text="Discrepancies")
        
        self.discrepancies_text = scrolledtext.ScrolledText(disc_frame, wrap=tk.WORD)
        self.discrepancies_text.pack(fill=tk.BOTH, expand=True)
        
        # Debug log tab
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Debug Log")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid expansion
        control_frame.columnconfigure(1, weight=1)
        verdict_inner_frame.columnconfigure(1, weight=1)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Certificate PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.log_message(f"Selected file: {file_path}")
    
    def analyze_certificate(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a PDF file first")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            return
        
        # Get API URL
        self.api_url = self.api_url_var.get()
        if not self.api_url:
            messagebox.showerror("Error", "Please enter API URL")
            return
        
        # Get custom instructions
        custom_instructions = self.custom_instructions_text.get("1.0", tk.END).strip()
        
        # Clear previous results
        self.response_text.delete(1.0, tk.END)
        self.calculations_text.delete(1.0, tk.END)
        self.discrepancies_text.delete(1.0, tk.END)
        self.summary_text.delete(1.0, tk.END)
        self.verdict_var.set("N/A")
        self.confidence_var.set("N/A")
        
        # Start analysis in a separate thread
        self.update_status("Analysis started...")
        self.progress.start()
        self.analyze_button.config(state=tk.DISABLED)
        threading.Thread(target=self._analysis_thread, args=(file_path, custom_instructions), daemon=True).start()
    
    def _analysis_thread(self, file_path, custom_instructions):
        try:
            # Prepare the API request
            with open(file_path, 'rb') as f:
                files = {'certificate_file': (os.path.basename(file_path), f, 'application/pdf')}
                
                data = {}
                if custom_instructions:
                    data['custom_instructions'] = custom_instructions
                
                # Log the request
                self.log_message(f"Sending request to API: {self.api_url}/analyze")
                self.log_message(f"File: {os.path.basename(file_path)}")
                if custom_instructions:
                    self.log_message(f"Custom instructions: {custom_instructions}")
                
                # Send the request to the API
                response = requests.post(
                    f"{self.api_url}/analyze",
                    files=files,
                    data=data
                )
                
                # Log the response status
                self.log_message(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    # Parse the JSON response
                    result = response.json()
                    
                    # Display the full response
                    self.root.after(0, lambda: self.response_text.insert(tk.END, json.dumps(result, indent=2)))
                    
                    # Update the verdict display
                    if "verdict" in result:
                        self.root.after(0, lambda: self.verdict_var.set(result["verdict"]))
                    
                    if "confidence" in result:
                        self.root.after(0, lambda: self.confidence_var.set(result["confidence"]))
                    
                    if "summary" in result:
                        self.root.after(0, lambda: self.summary_text.insert(tk.END, result["summary"]))
                    
                    # Extract and display specification sources
                    if "spec_source" in result:
                        self.root.after(0, lambda: self.spec_source_var.set(result["spec_source"]))
                    
                    # Update specifications tab with formatted specification information
                    if "specifications" in result:
                        specs_formatted = self._format_specifications(result["specifications"])
                        self.root.after(0, lambda: self.spec_text.insert(tk.END, specs_formatted))
                    
                    # Update calculations tab
                    if "calculations" in result and result["calculations"]:
                        calc_text = self._format_calculations(result["calculations"])
                        self.root.after(0, lambda: self.calculations_text.insert(tk.END, calc_text))
                    
                    # Update discrepancies tab
                    if "discrepancies" in result and result["discrepancies"]:
                        disc_text = self._format_discrepancies(result["discrepancies"])
                        self.root.after(0, lambda: self.discrepancies_text.insert(tk.END, disc_text))
                    
                    self.update_status("Analysis completed successfully")
                else:
                    # Display the error
                    error_message = f"API Error: {response.status_code} - {response.text}"
                    self.log_message(error_message, level=logging.ERROR)
                    self.root.after(0, lambda: self.response_text.insert(tk.END, error_message))
                    self.update_status(f"Error: {response.status_code}")
            
        except Exception as e:
            self.log_message(f"Error during analysis: {str(e)}", level=logging.ERROR)
            self.update_status(f"Error: {str(e)}")
            self.root.after(0, lambda: self.response_text.insert(tk.END, f"Error: {str(e)}"))
            
            import traceback
            self.log_message(traceback.format_exc(), level=logging.ERROR)
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.analyze_button.config(state=tk.NORMAL))
    
    def _format_calculations(self, calculations):
        """Format calculations list for display"""
        text = "CALCULATIONS:\n\n"
        for i, calc in enumerate(calculations):
            text += f"Calculation {i+1}:\n"
            text += f"  Parameter: {calc.get('parameter', 'N/A')}\n"
            text += f"  Nominal: {calc.get('nominal', 'N/A')}\n"
            text += f"  Spec Tolerance: {calc.get('spec_tolerance', 'N/A')}\n"
            text += f"  Applied Tolerance: {calc.get('applied_tolerance', 'N/A')}\n"
            text += f"  Equivalent: {calc.get('equivalent', 'N/A')}\n"
            text += f"  Explanation: {calc.get('explanation', 'N/A')}\n\n"
        return text
    
    def _format_discrepancies(self, discrepancies):
        """Format discrepancies list for display"""
        text = "DISCREPANCIES:\n\n"
        for i, disc in enumerate(discrepancies):
            text += f"Discrepancy {i+1}:\n"
            text += f"  Parameter: {disc.get('parameter', 'N/A')}\n"
            text += f"  Nominal: {disc.get('nominal', 'N/A')}\n"
            text += f"  Spec Tolerance: {disc.get('spec_tolerance', 'N/A')}\n"
            text += f"  Applied Tolerance: {disc.get('applied_tolerance', 'N/A')}\n"
            text += f"  Issue: {disc.get('issue', 'N/A')}\n\n"
        return text
    
    def _format_specifications(self, specifications):
        """Format specifications for better display"""
        if isinstance(specifications, str):
            return specifications
        
        if isinstance(specifications, dict):
            text = "DETAILED SPECIFICATIONS:\n\n"
            for param, details in specifications.items():
                text += f"{param}:\n"
                if isinstance(details, dict):
                    for key, value in details.items():
                        text += f"  {key}: {value}\n"
                else:
                    text += f"  {details}\n"
                text += "\n"
            return text
        
        return str(specifications)
    
    def update_status(self, message, error=False):
        """Update the status message"""
        self.root.after(0, lambda: self.status_var.set(message))
        if error:
            self.log_message(message, level=logging.ERROR)
    
    def log_message(self, message, level=logging.INFO):
        """Log a message to both the log file and the UI"""
        if level == logging.ERROR:
            logger.error(message)
        elif level == logging.WARNING:
            logger.warning(message)
        else:
            logger.info(message)
        
        # Also display in the UI log
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {'ERROR: ' if level == logging.ERROR else 'WARNING: ' if level == logging.WARNING else ''}{message}\n"
        self.root.after(0, lambda: self.log_text.insert(tk.END, log_entry))
        self.root.after(0, lambda: self.log_text.see(tk.END))

def main():
    root = tk.Tk()
    app = CalibrationAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()