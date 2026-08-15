import base64
import json
import os
import sys
import urllib.request

# Konfigurasi Repository
USERNAME = "basprogr"
REPO = "python-emr"
FILE_PATH = "emr.py"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_remote():
    # Gunakan GitHub API agar tidak bergantung pada nama branch (main/master)
    api_url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{FILE_PATH}"
    req = urllib.request.Request(
        api_url, headers={"User-Agent": "Python-Launcher"}
    )

    print(f"Mengambil {FILE_PATH} dari GitHub ({USERNAME}/{REPO})...")
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            # Decode isi file dari Base64
            code = base64.b64decode(data["content"]).decode("utf-8")

        # Set working directory ke folder launcher
        # Agar file history .txt dibuat dan dibaca dari lokasi ini
        os.chdir(BASE_DIR)

        print("Menjalankan program dari RAM...\n" + "=" * 40)
        exec(
            code,
            {
                "__name__": "__main__",
                "__file__": os.path.join(BASE_DIR, FILE_PATH),
            },
        )

    except urllib.error.HTTPError as e:
        print(f"[HTTP Error {e.code}]: Gagal mengambil file.")
        if e.code == 404:
            print(
                f"Pastikan file '{FILE_PATH}' berada di root folder repositori."
            )
    except Exception as e:
        print(f"Terjadi kesalahan saat menjalankan script: {e}")


if __name__ == "__main__":
    run_remote()