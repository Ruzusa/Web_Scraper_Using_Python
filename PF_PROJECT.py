import os
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime


# Directory to store extracted data
os.chdir(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = "extracted_data"  # creates file to store extracted data
HISTORY_FILE = "history.txt"  # creates file to store history

# Creates the directory if it doesn't exist, without raising an error if it already does
os.makedirs(DATA_DIR, exist_ok=True)


def validate_url(url):
    # validates that url sarts with http or https
    return url.startswith("http://") or url.startswith("https://")


def extract_data():
    # Retrieves the URL entered by the user and removes any leading/trailing whitespace
    url = url_entry.get().strip()

    if not validate_url(url):
        messagebox.showerror(
            "Invalid URL", "Please enter a valid URL (starting with http:// or https://)")
        return

    # clear previous result if any
    for widget in result_frame.winfo_children():
        widget.destroy()

    # Show progress bar and status message
    extracting_label = tk.Label(result_frame, text="Extracting data, please wait...",
                                bg="#621708", fg="white", font=("Helvetica", 10, "bold"))
    extracting_label.pack(pady=10)

    progress_bar = ttk.Progressbar(
        result_frame, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=10)

    path_label = tk.Label(result_frame, text="", bg="#bc4b51",
                          fg="white", font=("Helvetica", 9, "bold"))
    path_label.pack(pady=5)

    perform_scraping(url, progress_bar, path_label, extracting_label)


def perform_scraping(url, progress_bar, path_label, extracting_label):
    try:
        # sends HTTP get request to server with 20 sec time interval if time exceedes error will be raised
        response = requests.get(url, timeout=20)
        # if the HTTP response status code indicates an error (like 404  means if page doesnt exist or 500), it raises an exception, stops the program and jumps to except block
        response.raise_for_status()
        # response.text contains raw html code source in a plain string,Beautiful soup makes row content into structured form and html.parser tells program to use html built in parser
        soup = BeautifulSoup(response.text, 'html.parser')

        raw_text = soup.get_text()  # get text from parsed content skipping tags or scripts
        # Removes empty lines and leading/trailing spaces, then joins the cleaned lines into a single text block
        lines = [line.strip()
                 for line in raw_text.splitlines() if line.strip()]
        text_data = "\n".join(lines)

        # Generates a timestamped filename using the current date and time
        now = datetime.now()
        current_time = now.strftime("%Y%m%d_%H%M%S")
        filename = f"{DATA_DIR}/data_{current_time}.txt"

        # opening file in write mode to add extracted data into it
        with open(filename, "w", encoding='utf-8') as f:
            f.write(text_data)

        with open(HISTORY_FILE, "a", encoding='utf-8') as history:
            history.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - {url}\n")

        def simulate_progress(i=0):
            # Updates the progress bar value gradually until it reaches 100, with a short delay between updates
            if i <= 100:
                progress_bar['value'] = i
                root.update_idletasks()
                root.after(15, lambda: simulate_progress(i + 1))
            else:
                path_label.config(
                    text=f"File succesfully saved to:\n{os.path.abspath(filename)}", fg="white", bg="#7C1217")
                progress_bar.destroy()
                extracting_label.destroy()

        simulate_progress()

    # handles any network error during HTTP get request, Request exception is base class that handles all requests related error like connection error, timeout error,
    except requests.exceptions.RequestException as e:
        messagebox.showerror(
            "Request Error", f"Failed to fetch data from the URL.\n\n{str(e)}")

    except Exception as e:  # handles other unexpected error like disk error
        messagebox.showerror(
            "Error", f"An unexpected error occurred:\n\n{str(e)}")


# GUI Setup
root = tk.Tk()
root.title("Web Scraper")
root.geometry("800x550")
root.configure(bg="#621708")

# Heading
tk.Label(root, text="🌐 WEB SCRAPING",
         font=("Helvetica", 22, "bold"),
         bg="#220901", fg="#e7ecef", pady=20).pack(fill="x")

# Description
tk.Label(root, text="Web scraping is the process of automatically extracting information from websites.\n"
                    "It involves writing a script or using a tool to collect data from web pages and\n"
                    "save it in a structured format.",
         font=("Helvetica", 14, "bold"),
         bg="#621708", fg="#e7ecef", justify="left").pack(padx=10, pady=(10, 20))

# URL label
tk.Label(root, text="ENTER URL to SCRAPE:",
         bg="#621708", fg="#e7ecef", font=("Helvetica", 13, "bold")).pack(pady=5)

# Frame to hold Entry and Button side by side
url_frame = tk.Frame(root, bg="#621708")
url_frame.pack(pady=5)

# URL entry inside frame
url_entry = tk.Entry(url_frame, width=50, bg="white",
                     fg="black", font=("Helvetica", 11, "bold"))
url_entry.pack(side=tk.LEFT, padx=5, ipady=6)


# Extract button inside frame, next to entry
tk.Button(url_frame, text="EXTRACT", command=extract_data,
          bg="#7B3000", fg="white", activebackground="#9E3D00", activeforeground="white", cursor="hand2", font=("Helvetica", 14, "bold")).pack(side=tk.LEFT, padx=5)

# Frame for result and progress
result_frame = tk.Frame(root, bg="#7C1217", width=50)
result_frame.pack(pady=10)

# Developer label
tk.Label(root, text="@ Developed by RUZUSA",
         bg="black", fg="white", font=("Helvetica", 10, "bold"),
         anchor="center", pady=10).pack(side="bottom", fill="x")

# Start the GUI loop
root.mainloop()
