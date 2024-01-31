import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import shutil
import threading
import json

CONFIG_FILE = "config.json"

def are_files_equal(file1, file2):
    # Open both files in binary mode
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        # Read the content of both files
        content1 = f1.read()
        content2 = f2.read()
    
    # Compare the contents of the files
    if content1 == content2:
        return True
    else:
        return False

def read_configuration():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {"source": "", "destination": ""}

def save_configuration(source, destination):
    with open(CONFIG_FILE, "w") as file:
        json.dump({"source": source, "destination": destination}, file)

def choose_directory(title, entry):
    directory = filedialog.askdirectory(title=title)
    if directory:
        entry.delete(0, tk.END)
        entry.insert(0, directory)

def copy_new_files_with_progress(source, destination, progress_text):
    total_files = 0
    total_copied = 0

    # First, count the total number of files to be copied
    for current_folder, _, files in os.walk(source):
        destination_current_folder = os.path.join(destination, os.path.relpath(current_folder, source))
        destination_files = set(os.listdir(destination_current_folder)) if os.path.exists(destination_current_folder) else set()
        c=[]

        for dest_file in destination_files:
            if "." in dest_file:
                dest = destination_current_folder + "/" + dest_file
                if dest_file in files:
                    if destination_current_folder[-1] == ".":
                        destination_current_folder = destination_current_folder[:-1]

                    if not are_files_equal(dest, current_folder + "/" + dest_file):
                        os.remove(destination_current_folder + "/" + dest_file)
                        progress_text.insert(tk.END, f"Apagando: {dest_file} to {dest} \n")
                        c.append(dest_file)
                        
                else:
                    os.remove(dest)
                    progress_text.insert(tk.END, f"Apagando: {dest_file} to {dest} \n")

        for i in c:
            destination_files.remove(i)
        total_files += len([file for file in files if file not in destination_files])

    if total_files == 0:
        progress_text.insert(tk.END, "Sem novos arquivos para copiar.\n")
        return

    for current_folder, _, files in os.walk(source):
        destination_current_folder = os.path.join(destination, os.path.relpath(current_folder, source))
        if not os.path.exists(destination_current_folder):
            os.makedirs(destination_current_folder)

        destination_files = set(os.listdir(destination_current_folder))

        for file in files:
            if file not in destination_files:
                source_full_path = os.path.join(current_folder, file)
                destination_full_path = os.path.join(destination_current_folder, file)

                try:
                    if os.path.isfile(source_full_path):
                        shutil.copy(source_full_path, destination_full_path)
                        total_copied += 1
                        percentage = (total_copied / total_files) * 100
                        progress_text.insert(tk.END, f"Copiando: {file} para {destination_current_folder} ({percentage:.2f}% completo)\n")
                except Exception as e:
                    progress_text.insert(tk.END, f"Erro ao copiar {file}: {e}\n")

    if total_copied == 0:
        progress_text.insert(tk.END, "Sem novos arquivos para copiar.\n")
    else:
        progress_text.insert(tk.END, "Completo tudo foi copiado.\n")

def start_copying(source_entry, destination_entry, progress):
    source = source_entry.get()
    destination = destination_entry.get()
    save_configuration(source, destination)
    if not source or not destination:
        messagebox.showerror("Error", "Please select both folders.")
        return

    threading.Thread(target=copy_new_files_with_progress, args=(source, destination, progress)).start()

# GUI functions
def create_label_frame(parent, title, row, column, padx, pady):
    frame = ttk.LabelFrame(parent, text=title)
    frame.grid(row=row, column=column, padx=padx, pady=pady, sticky="ew")
    return frame

def create_entry_with_button(frame, label_text, button_text, button_command):
    label = ttk.Label(frame, text=label_text)
    label.pack(side=tk.LEFT, padx=(0, 5))
    
    entry = ttk.Entry(frame, width=50)
    entry.pack(side=tk.LEFT, padx=(0, 5))

    button = ttk.Button(frame, text=button_text, command=lambda: button_command(entry))
    button.pack(side=tk.LEFT)
    
    return entry

def create_interface():
    # Initial window settings
    root = tk.Tk()
    root.title("File Copier")
    style = ttk.Style()
    style.configure('TButton', font=('Arial', 10))

    # Load saved configurations
    config = read_configuration()

    # Source and Destination frames
    source_frame = create_label_frame(root, "Source", 0, 0, 10, 5)
    destination_frame = create_label_frame(root, "Destination", 1, 0, 10, 5)

    source_entry = create_entry_with_button(source_frame, "Source Folder:", "Choose", lambda e: choose_directory("Choose the source folder", e))
    destination_entry = create_entry_with_button(destination_frame, "Destination Folder:", "Choose", lambda e: choose_directory("Choose the destination folder", e))

    source_entry.insert(0, config["source"])
    destination_entry.insert(0, config["destination"])

    # Progress area
    progress = scrolledtext.ScrolledText(root, height=10)
    progress.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="nsew")  

    # Start button
    start_btn = ttk.Button(root, text="Start Copy", command=lambda: start_copying(source_entry, destination_entry, progress))
    start_btn.grid(row=3, column=0, padx=10, pady=(0, 10))

    # Configure grid row and column expansion
    root.grid_rowconfigure(2, weight=1)  
    root.grid_columnconfigure(0, weight=1)  

    # Start the main window
    root.mainloop()

create_interface()
