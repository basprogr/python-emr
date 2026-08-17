import base64
import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  
DEPENDENCIES = {
    "pdfplumber": "pdfplumber",
    "pyautogui": "pyautogui",
    "pyperclip": "pyperclip",
    "qrcode": "qrcode",
    "tkinter": "tk", 
    "PIL": "pillow" 
}
 
def check_and_install_dependencies(root, label):
    for module_name, pip_name in DEPENDENCIES.items():
        try:
            __import__(module_name)
        except ImportError:
            label.config(text=f"Installing {pip_name}...")
            root.update()
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pip_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
 
def load_and_run(root, label, progress):
    api_url = (
        "https://api.github.com/repos/basprogr/python-emr/contents/emr.py"
    )
    req = urllib.request.Request(
        api_url, headers={"User-Agent": "Python-Launcher"}
    )

    try:
        # 1. Cek Dependensi
        if DEPENDENCIES:
            check_and_install_dependencies(root, label)

        # 2. Download source file dari GitHub API
        label.config(text="Downloading source file...")
        root.update()

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            code = base64.b64decode(data["content"]).decode("utf-8")

        os.chdir(BASE_DIR)

        # Hentikan animasi progress bar terlebih dahulu agar tidak error saat destroy
        progress.stop()
        root.destroy()

        # 3. Eksekusi emr.py dari RAM
        exec(
            code,
            {
                "__name__": "__main__",
                "__file__": os.path.join(BASE_DIR, "emr.py"),
            },
        )

    except Exception as e:
        progress.stop()  # Hentikan animasi jika ada error
        label.config(text=f"Error: {e}", foreground="red")


def main():
    root = tk.Tk()
    root.title("EMR Launcher")
    root.geometry("300x100")
    root.eval("tk::PlaceWindow . center")

    label = ttk.Label(root, text="Starting launcher...", font=("Arial", 10))
    label.pack(expand=True)

    progress = ttk.Progressbar(root, mode="indeterminate")
    progress.pack(fill="x", padx=20, pady=(0, 20))
    progress.start(10)

    # Kirimkan variabel progress ke dalam load_and_run
    root.after(100, lambda: load_and_run(root, label, progress))
    root.mainloop()


if __name__ == "__main__":
    main()