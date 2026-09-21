import time
import tkinter as tk
from tkinter import messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MersiAutomationApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Automasi RME Mersi Hospital")
    self.root.geometry("700x600")

    # Label Petunjuk
    self.label = tk.Label(
        root,
        text=(
            "Masukkan data TTV pasien (Format:\n"
            "namaRuang-sistole-diastole-nadi-spo2-statusOksigen-suhu-respirasi)"
        ),
        justify=tk.LEFT,
    )
    self.label.pack(padx=10, pady=10, anchor="w")

    # Text Area untuk Input Data Pasien
    self.text_area = scrolledtext.ScrolledText(root, width=80, height=20)
    self.text_area.pack(padx=10, pady=5)

    # Contoh Data Bawaan
    default_data = (
        "301 Bed A-110-81-71-97-0-36.1-21\n301 Bed B-120-82-72-98-1-36.2-22"
    )
    self.text_area.insert(tk.END, default_data)

    # Tombol Mulai Automasi
    self.btn_start = tk.Button(
        root,
        text="Mulai Automasi",
        bg="green",
        fg="white",
        font=("Arial", 11, "bold"),
        command=self.run_automation,
    )
    self.btn_start.pack(padx=10, pady=15)

  def run_automation(self):
    raw_data = self.text_area.get("1.0", tk.END).strip()
    if not raw_data:
      messagebox.showerror("Error", "Data pasien masih kosong!")
      return

    lines = raw_data.split("\n")
    patients_data = []

    try:
      for line in lines:
        if not line.strip():
          continue
        parts = line.split("-")
        if len(parts) != 8:
          raise ValueError(f"Format salah pada baris: {line}")

        patient = {
            "namaRuang": parts[0].strip(),
            "sistole": parts[1].strip(),
            "diastole": parts[2].strip(),
            "nadi": parts[3].strip(),
            "spo2": parts[4].strip(),
            "statusOksigen": int(parts[5].strip()),
            "suhu": parts[6].strip(),
            "respirasi": parts[7].strip(),
        }
        patients_data.append(patient)
    except Exception as e:
      messagebox.showerror(
          "Format Error",
          f"Terjadi kesalahan format data:\n{e}\nPastikan pemisah menggunakan '-'",
      )
      return

    # Jalankan Selenium di Background / Thread terpisah (atau langsung jika ingin simpel)
    self.execute_selenium(patients_data)

  def execute_selenium(self, patients_data):
    driver = webdriver.Chrome()  # Pastikan chromedriver tersedia di PATH
    wait = WebDriverWait(driver, 10)

    try:
      # 1. Login
      driver.get("http://20.20.20.6/app.mersi-hospital/live/login")
      time.sleep(2)

      username_input = wait.until(
          EC.presence_of_element_located((By.ID, "username"))
      )
      password_input = driver.find_element(By.ID, "password")

      username_input.send_keys("20224015")
      password_input.send_keys("2024")
      password_input.send_keys(Keys.RETURN)

      # Jeda 2 detik lalu arahkan ke halaman aktif
      time.sleep(2)
      driver.get(
          "http://20.20.20.6/app.mersi-hospital/live/ri/entry/transaksi_mrs_aktif"
      )
      time.sleep(5)

      # 2. Iterasi setiap pasien
      for p in patients_data:
        try:
              # Mencari baris tr berdasarkan nama ruang dan memastikan elemennya bisa diklik
          row_target = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
              (By.XPATH, f"//tr[contains(., '{p['namaRuang']}')]")
            )
          )
          time.sleep(2)    
              # Klik baris tersebut (atau langsung klik tombol btn-rme di dalamnya)
          row_target.click()

              # Cari tombol #btn-rme di dalam baris yang sudah ditemukan
          btn_rme = row_target.find_element(By.ID, "btn-rme")
          btn_rme.click()

          # Membuka tab baru (Selenium otomatis handle tab baru atau pindah fokus)
          time.sleep(2)
          window_handles = driver.window_handles
          driver.switch_to.window(window_handles[-1])



          # 3. Modifikasi URL Pemeriksaan TTV
          current_url = driver.current_url
          # Contoh: http://20.20.20.6/app.mersi-hospital/live.rme/rawatinap/asperawat_ranap?idx=...&idp=...
          new_url = current_url.replace(
              "asperawat_ranap", "pemeriksaan_ttv"
          ) or current_url.replace("index.php", "")  # Sesuaikan modifikasi
          # Sesuai request prompt persis: ganti asperawat_ranap jadi pemeriksaan_ttv
          if "asperawat_ranap" in current_url:
            new_url = current_url.replace("asperawat_ranap", "pemeriksaan_ttv")
          else:
            new_url = current_url + (
                "/pemeriksaan_ttv"
                if not current_url.endswith("/")
                else "pemeriksaan_ttv"
            )  # fallback aman

          driver.get(new_url)
          time.sleep(3)  # tunggu halaman selesai dimuat

          # 4. Klik "Tulis Data"
          tulis_data_btn = wait.until(
              EC.element_to_be_clickable(
                  (
                      By.XPATH,
                      "//h3/a[@data-card-widget='collapse' and"
                      " text()='Tulis Data']",
                  )
              )
          )
          # Karena strukturnya <h3><a ...>Tulis Data</a></h3>, kita cari elemen <a> yang berisi teks Tulis Data
          tulis_data_btn = wait.until(
              EC.element_to_be_clickable(
                  (
                      By.XPATH,
                      "//h3/a[@data-card-widget='collapse'][contains(.,'Tulis"
                      " Data')]",
                  )
              )
          )
          tulis_data_btn.click()
          time.sleep(1)

          # 5. Isi Form TTV
          driver.find_element(By.ID, "txtresp").send_keys(p["respirasi"])
          driver.find_element(By.ID, "txtspo2").send_keys(p["spo2"])

          # Radio button statusOksigen (0 = Tidak, >0 = Ya)
          if p["statusOksigen"] == 0:
            # Pilih "Tidak" (value="0")
            radio_tidak = driver.find_element(
                By.XPATH, "//input[@id='txtinso2' and @value='0']"
            )
            if not radio_tidak.is_selected():
              driver.execute_script("arguments[0].click();", radio_tidak)
          else:
            # Pilih "Ya" (value="2")
            radio_ya = driver.find_element(
                By.XPATH, "//input[@id='txtinso2' and @value='2']"
            )
            if not radio_ya.is_selected():
              driver.execute_script("arguments[0].click();", radio_ya)

          driver.find_element(By.ID, "txttemp").send_keys(p["suhu"])
          driver.find_element(By.ID, "txtbp").send_keys(p["sistole"])
          driver.find_element(By.ID, "txtbp1").send_keys(p["diastole"])
          driver.find_element(By.ID, "txthr").send_keys(p["nadi"])

          time.sleep(1)

          # 6. Klik tombol Save
          save_btn = driver.find_element(By.ID, "save")
          save_btn.click()

          # Proses save mereload halaman, beri jeda 5 detik
          time.sleep(5)

          # 7. Modifikasi URL ke CPPT
          current_url_after_save = driver.current_url
          cppt_url = current_url_after_save.replace(
              "pemeriksaan_ttv", "cppt"
          )
          driver.get(cppt_url)
          time.sleep(3)

          # Tutup tab pasien ini, lalu kembali ke tab utama list pasien
          driver.close()
          driver.switch_to.window(window_handles[0])
          time.sleep(1)

        except Exception as inner_e:
          print(f"Gagal memproses pasien {p['namaRuang']}: {inner_e}")
          # Jika error di satu pasien, coba kembali ke window utama agar iterasi berikutnya aman
          if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
          continue

      messagebox.setItem = messagebox.showinfo(
          "Sukses", "Automasi pengisian RME selesai!"
      )

    except Exception as e:
      messagebox.showerror("Error Automasi", f"Terjadi kesalahan sistem: {e}")
    finally:
      # driver.quit() # Uncomment jika ingin browser otomatis tertutup setelah selesai
      pass


if __name__ == "__main__":
  root = tk.Tk()
  app = MersiAutomationApp(root)
  root.mainloop()