import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil
import os
import subprocess
import threading

# Set up the relative path for the destination directory
destination_dir = os.path.join(os.getcwd(), "test_datasets", "gray_test")

def update_status(message):
    status_label.config(text=message)

def run_inference():
    input_image_path = filedialog.askopenfilename(title="Select Input Image for Colorization")
    if not input_image_path:
        return
    
    input_image_name = os.path.basename(input_image_path)
    input_image_dest = os.path.join(destination_dir, input_image_name)
    
    if os.path.abspath(input_image_path) != os.path.abspath(input_image_dest):
        shutil.copy(input_image_path, input_image_dest)
    
    update_status("Input image selected.")
    
    reference_image_path = filedialog.askopenfilename(title="Select Reference Image for Colorization")
    if not reference_image_path:
        return
    
    reference_image_name = os.path.basename(reference_image_path)
    reference_image_dest = os.path.join(destination_dir, reference_image_name)
    
    if os.path.abspath(reference_image_path) != os.path.abspath(reference_image_dest):
        shutil.copy(reference_image_path, reference_image_dest)
    
    update_status("Reference image selected.")
    
    # Show progress bar
    progress_bar.pack(pady=10)
    progress_bar['value'] = 0
    
    # Start colorization process
    threading.Thread(target=run_colorization, args=(input_image_name, reference_image_name)).start()

def run_colorization(input_image_name, reference_image_name):
    try:
        cmd = 'python inference2.py -ne'
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True, shell=True)
        process.communicate(input=f"{input_image_name}\n{reference_image_name}\n")
        
        update_status("Colorization process completed.")
        progress_bar['value'] = 100
    except subprocess.CalledProcessError:
        update_status("Failed to run the colorization script.")
        messagebox.showerror("Error", "Failed to run the colorization script.")
    finally:
        progress_bar.pack_forget()  # Hide progress bar when done

# GUI setup
root = tk.Tk()
root.title("Example-Based Manga Colorization and Grayscale Conversion")
root.geometry("600x400")  # Maintain the same size as the previous GUI

# Create a frame to hold the buttons and status bar
info_frame = ttk.Frame(root)
info_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X)

# Status label
status_label = ttk.Label(info_frame, text="", font=("Courier", 14))
status_label.pack(pady=10)

# Progress bar
progress_bar = ttk.Progressbar(info_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)
progress_bar.pack_forget()  # Initially hide the progress bar

# Colorization button
colorization_btn = ttk.Button(info_frame, text="Start Colorization", command=run_inference)
colorization_btn.pack(pady=10)

# Run the Tkinter event loop
if __name__ == "__main__":
    root.mainloop()
