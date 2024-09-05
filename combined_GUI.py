import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import shutil
import os
import subprocess
import threading
import zipfile

# Set up the relative path for the destination directory
destination_dir = os.path.join(os.getcwd(), "test_datasets", "gray_test")

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def check_and_activate_conda_env():
    try:
        env_name = subprocess.run('echo %CONDA_DEFAULT_ENV%', shell=True, capture_output=True, text=True)
        if 'manga' not in env_name.stdout.strip():
            subprocess.run('conda activate manga', shell=True, check=True, executable="/bin/bash")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to activate the Conda environment 'manga'.")
        root.quit()

def show_frame(frame):
    frame.tkraise()

def create_subfolder(option_name):
    demo_dir = os.path.join(os.getcwd(), 'demo', option_name)
    ensure_directory_exists(demo_dir)
    return demo_dir

def upload_images_predefined():
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_paths:
        process_files(file_paths, 'predefined', process_images_predefined)

def upload_cbz_predefined():
    cbz_file_path = filedialog.askopenfilename(filetypes=[("CBZ files", "*.cbz")])
    if cbz_file_path:
        demo_dir = create_subfolder('predefined')
        cbz_file_name = os.path.basename(cbz_file_path)
        cbz_dest_path = os.path.join(demo_dir, cbz_file_name)
        shutil.copy(cbz_file_path, cbz_dest_path)
        with zipfile.ZipFile(cbz_dest_path, 'r') as zip_ref:
            zip_ref.extractall(demo_dir)
        image_files = [os.path.join(demo_dir, file) for file in zip_ref.namelist() if file.endswith(('.png', '.jpg', '.jpeg'))]
        process_files(image_files, 'predefined', process_images_predefined)

def process_files(file_paths, option_name, process_function):
    demo_dir = create_subfolder(option_name)
    status_label.config(text="Processing...")
    show_progress_bar(indeterminate=True)
    threading.Thread(target=process_function, args=(file_paths, demo_dir)).start()

def process_images_predefined(file_paths, demo_dir):
    image_names = []
    demo_image_paths = []
    for file_path in file_paths:
        image_name = os.path.basename(file_path)
        demo_image_path = os.path.join(demo_dir, image_name)
        if os.path.abspath(file_path) != os.path.abspath(demo_image_path):
            try:
                shutil.copy(file_path, demo_image_path)
            except shutil.SameFileError:
                pass
        image_names.append(image_name)
        demo_image_paths.append(demo_image_path)
    status_label.config(text=f"Starting colorization of {len(demo_image_paths)} images...")
    run_inference_for_all(demo_image_paths, image_names, demo_dir)

def run_inference_for_all(image_paths, image_names, demo_dir):
    total_images = len(image_paths)
    for index, (image_path, image_name) in enumerate(zip(image_paths, image_names), start=1):
        root.after(0, lambda path=image_path: open_image(path))
        run_inference(image_path, image_name, demo_dir)
        root.after(0, lambda idx=index, total=total_images: update_status(idx, total))
    root.after(0, finish_processing)

def run_inference(image_path, image_name, demo_dir):
    try:
        subprocess.run(['python', 'inference.py', '-p', image_path], check=True)
        output_image_path = os.path.join(demo_dir, f"{os.path.splitext(os.path.basename(image_path))[0]}_colorized.png")
        root.after(0, lambda path=output_image_path: open_image(path))
    except subprocess.CalledProcessError:
        root.after(0, lambda: messagebox.showerror("Error", f"Failed to run the colorization script for {image_name}."))
        root.after(0, lambda: status_label.config(text=f"Error processing {image_name}."))

def open_image(image_path):
    try:
        img = Image.open(image_path)
        img.show()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open image: {e}")

def show_progress_bar(indeterminate=False):
    # Show the progress bar with grid
    progress_bar.grid(row=5, column=1, pady=10, sticky="ew")
    if indeterminate:
        progress_bar.start()
    else:
        progress_bar.stop()

def finish_processing():
    status_label.config(text="Colorization process completed.")
    # Hide the progress bar when done
    progress_bar.grid_remove()

def update_status(index=None, total=None):
    if index is not None and total is not None:
        status_label.config(text=f"Processed {index}/{total} images...")
    else:
        status_label.config(text="Processing...")

def run_inference_example_based():
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
   
    demo_dir = create_subfolder('example_based')
    update_status("Reference image selected.")

    if os.path.abspath(input_image_path) != os.path.abspath(input_image_dest):
        shutil.copy(input_image_path, demo_dir)

    if os.path.abspath(reference_image_path) != os.path.abspath(reference_image_dest):
        shutil.copy(reference_image_path, demo_dir)

    update_status("Input image selected and copied.")
    show_progress_bar(indeterminate=True)  # Show indeterminate progress bar
    threading.Thread(target=run_colorization_example_based, args=(input_image_name, reference_image_name, demo_dir)).start()

def run_colorization_example_based(input_image_name, reference_image_name, demo_dir):
    try:
        cmd = 'python inference2.py -ne'
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True, shell=True)
        process.communicate(input=f"{input_image_name}\n{reference_image_name}\n")
        
        output_image_name = f"{os.path.splitext(input_image_name)[0]}_color.png"
        output_image_path = os.path.join('test_datasets', 'gray_test', 'color', output_image_name)
        if os.path.exists(output_image_path):
            shutil.copy(output_image_path, os.path.join(demo_dir, output_image_name))
            root.after(0, lambda path=os.path.join(demo_dir, output_image_name): open_image(path))
        
        update_status("Colorization process completed.")
        progress_bar['value'] = 100
    except subprocess.CalledProcessError:
        update_status("Failed to run the colorization script.")
        messagebox.showerror("Error", "Failed to run the colorization script.")
    finally:
        show_progress_bar(indeterminate=False)  # Hide progress bar and reset
        finish_processing()

def run_grayscale_conversion():
    input_image_path = filedialog.askopenfilename(title="Select Input Image for Grayscale Conversion")
    if input_image_path:
        demo_dir = create_subfolder('grayscale')
        process_files([input_image_path], 'grayscale', convert_to_grayscale)

def convert_to_grayscale(file_paths, demo_dir):
    input_image_path = file_paths[0]
    try:
        img = Image.open(input_image_path).convert("L")
        output_image_path = os.path.join(demo_dir, f"{os.path.splitext(os.path.basename(input_image_path))[0]}_gray.png")
        img.save(output_image_path)
        update_status(100, 100)
        root.after(0, lambda path=output_image_path: open_image(path))
    except Exception as e:
        update_status("Failed to convert to grayscale.")
        messagebox.showerror("Error", f"Failed to convert to grayscale: {e}")
    finally:
        progress_bar.pack_forget()

# Main GUI Setup
root = tk.Tk()
root.title("Manga Colorization Tool")
root.geometry("600x500")

# Define frames
frames = {
    'main_menu': tk.Frame(root),
    'predefined': tk.Frame(root),
    'example_based': tk.Frame(root),
    'grayscale': tk.Frame(root)
}

for frame in frames.values():
    frame.grid(row=0, column=0, sticky='nsew')

# Configure grid rows and columns to make widgets responsive
for frame in frames.values():
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_rowconfigure(2, weight=1)
    frame.grid_rowconfigure(3, weight=1)
    frame.grid_rowconfigure(4, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_columnconfigure(2, weight=1)

# Main Menu
tk.Label(frames['main_menu'], text="Choose an option", font=("Arial", 18)).grid(row=0, column=1, pady=20)
tk.Button(frames['main_menu'], text="Predefined Colorization", font=("Arial", 14), command=lambda: show_frame(frames['predefined'])).grid(row=1, column=1, pady=10, sticky="ew")
tk.Button(frames['main_menu'], text="Example-Based Colorization", font=("Arial", 14), command=lambda: show_frame(frames['example_based'])).grid(row=2, column=1, pady=10, sticky="ew")
tk.Button(frames['main_menu'], text="Grayscale Conversion", font=("Arial", 14), command=lambda: show_frame(frames['grayscale'])).grid(row=3, column=1, pady=10, sticky="ew")
tk.Button(frames['main_menu'], text="Exit", font=("Arial", 14), command=root.quit).grid(row=4, column=1, pady=10, sticky="ew")

# Predefined Colorization Frame
tk.Label(frames['predefined'], text="Predefined Colorization", font=("Arial", 18)).grid(row=0, column=1, pady=20)
tk.Button(frames['predefined'], text="Upload Images", font=("Arial", 14), command=upload_images_predefined).grid(row=1, column=1, pady=10, sticky="ew")
tk.Button(frames['predefined'], text="Upload CBZ File", font=("Arial", 14), command=upload_cbz_predefined).grid(row=2, column=1, pady=10, sticky="ew")
tk.Button(frames['predefined'], text="Back", font=("Arial", 14), command=lambda: show_frame(frames['main_menu'])).grid(row=3, column=1, pady=10, sticky="ew")
status_label = tk.Label(frames['predefined'], text="", font=("Arial", 12))
status_label.grid(row=4, column=1, pady=10, sticky="ew")
progress_bar = ttk.Progressbar(frames['predefined'], orient="horizontal", mode="determinate")
progress_bar.grid(row=5, column=1, pady=10, sticky="ew")

# Example-Based Colorization Frame
tk.Label(frames['example_based'], text="Example-Based Colorization", font=("Arial", 18)).grid(row=0, column=1, pady=20)
tk.Button(frames['example_based'], text="Upload Input Image", font=("Arial", 14), command=run_inference_example_based).grid(row=1, column=1, pady=10, sticky="ew")
tk.Button(frames['example_based'], text="Back", font=("Arial", 14), command=lambda: show_frame(frames['main_menu'])).grid(row=2, column=1, pady=10, sticky="ew")
progress_bar = ttk.Progressbar(frames['example_based'], orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=4, column=1, pady=10, sticky="ew")
progress_bar.grid_remove()  # Hide initially

status_label = tk.Label(frames['example_based'], text="", font=("Arial", 12))
status_label.grid(row=3, column=1, pady=10, sticky="ew")

# Grayscale Conversion Frame
tk.Label(frames['grayscale'], text="Grayscale Conversion", font=("Arial", 18)).grid(row=0, column=1, pady=20)
tk.Button(frames['grayscale'], text="Upload Image", font=("Arial", 14), command=run_grayscale_conversion).grid(row=1, column=1, pady=10, sticky="ew")
tk.Button(frames['grayscale'], text="Back", font=("Arial", 14), command=lambda: show_frame(frames['main_menu'])).grid(row=2, column=1, pady=10, sticky="ew")

# Display the main menu on startup
show_frame(frames['main_menu'])

# Allow the window to be resized
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# Run the main loop
root.mainloop()
