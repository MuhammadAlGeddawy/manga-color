import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import shutil
import os
import zipfile
import subprocess
import threading

def check_and_activate_conda_env():
    try:
        # Check if the 'manga' environment is active
        env_name = subprocess.run('echo %CONDA_DEFAULT_ENV%', shell=True, capture_output=True, text=True)
        
        if 'manga' not in env_name.stdout.strip():
            # If not active, activate the environment
            subprocess.run('conda activate manga', shell=True, check=True, executable="/bin/bash")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to activate the Conda environment 'manga'.")
        root.quit()

def upload_images():
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    
    if not file_paths:
        return

    # Show progress bar
    progress_bar.pack(pady=10)  # Show the progress bar
    status_label.config(text="Processing images...")
    
    threading.Thread(target=process_images, args=(file_paths,)).start()

def upload_cbz():
    cbz_file_path = filedialog.askopenfilename(filetypes=[("CBZ files", "*.cbz")])
    
    if not cbz_file_path:
        return
    
    # Destination directory
    demo_dir = os.path.join(os.getcwd(), 'demo')
    if not os.path.exists(demo_dir):
        os.makedirs(demo_dir)

    # Copy CBZ file to destination directory
    cbz_file_name = os.path.basename(cbz_file_path)
    cbz_dest_path = os.path.join(demo_dir, cbz_file_name)
    
    shutil.copy(cbz_file_path, cbz_dest_path)

    # Extract images from the CBZ file
    with zipfile.ZipFile(cbz_dest_path, 'r') as zip_ref:
        image_files = [os.path.join(demo_dir, file) for file in zip_ref.namelist() if file.endswith(('.png', '.jpg', '.jpeg'))]
        zip_ref.extractall(demo_dir)
    
    num_images = len(image_files)
    
    # Update status with the number of images found
    status_label.config(text=f"CBZ file contains {num_images} images. Processing...")
    
    # Show progress bar
    progress_bar.pack(pady=10)  # Show the progress bar
    threading.Thread(target=process_images, args=(image_files,)).start()

def process_images(file_paths):
    demo_dir = os.path.join(os.getcwd(), 'demo')
    image_names = []
    demo_image_paths = []
    
    for file_path in file_paths:
        image_name = os.path.basename(file_path)
        demo_image_path = os.path.join(demo_dir, image_name)
        
        # Check if the file already exists in the destination directory
        if os.path.abspath(file_path) != os.path.abspath(demo_image_path):
            try:
                shutil.copy(file_path, demo_image_path)
            except shutil.SameFileError:
                pass
        
        image_names.append(image_name)
        demo_image_paths.append(demo_image_path)
    
    # Initialize the processing
    status_label.config(text=f"Starting colorization of {len(demo_image_paths)} images...")
    run_inference_for_all(demo_image_paths, image_names)

def run_inference_for_all(image_paths, image_names):
    total_images = len(image_paths)
    for index, (image_path, image_name) in enumerate(zip(image_paths, image_names), start=1):
        # Display the current input image before running inference
        root.after(0, lambda path=image_path: open_image(path))
        run_inference(image_path, image_name)
        
        # Update status label and progress bar
        root.after(0, lambda index=index, total=total_images: update_status(index, total))
    
    # Finish processing
    root.after(0, lambda: finish_processing())

def run_inference(image_path, image_name):
    try:
        subprocess.run(['python', 'inference.py', '-p', image_path], check=True)
        
        # Generate the output image path
        demo_dir = os.path.join(os.getcwd(), 'demo')
        output_image_path = os.path.join(demo_dir, f"{os.path.splitext(image_name)[0]}_colorized.png")
        
        # Display the output image
        root.after(0, lambda path=output_image_path: open_image(path))
    except subprocess.CalledProcessError:
        root.after(0, lambda: messagebox.showerror("Error", f"Failed to run the colorization script for {image_name}."))
        root.after(0, lambda: status_label.config(text=f"Error processing {image_name}."))

def open_image(image_path):
    try:
        img = Image.open(image_path)
        img.show()  # Opens the image in the default image viewer
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open image: {e}")

def update_status(index, total):
    status_label.config(text=f"Processed {index}/{total} images...")
    progress_bar['value'] = (index / total) * 100

def finish_processing():
    status_label.config(text="Colorization process completed.")
    progress_bar.pack_forget()  # Hide the progress bar

# Set up the main Tkinter window
root = tk.Tk()
root.title("Manga Colorization")
root.geometry("600x400")  # Window size

# Create a frame to hold the status label and progress bar
info_frame = ttk.Frame(root)
info_frame.pack(pady=10, fill=tk.X)

# Create a label for status updates
status_label = ttk.Label(info_frame, text="", font=("Arial", 12))
status_label.pack(pady=5)

# Create a progress bar
progress_bar = ttk.Progressbar(info_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.pack_forget()  # Initially hide the progress bar

# Create a frame to hold the buttons at the bottom
button_frame = ttk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X)

# Create buttons and place them in the frame
upload_images_btn = ttk.Button(button_frame, text="Upload Images", command=upload_images)
upload_images_btn.pack(side=tk.TOP, pady=10)

upload_cbz_btn = ttk.Button(button_frame, text="Upload CBZ File", command=upload_cbz)
upload_cbz_btn.pack(side=tk.TOP, pady=10)

# Run the Tkinter event loop
if __name__ == "__main__":
    root.mainloop()
