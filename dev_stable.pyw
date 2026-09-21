import time
import threading
from tkinter import *
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def jalankan_automasi(data_pasien_str):
    """Fungsi yang menjalankan Selenium untuk memproses data pasien dan mengisi form TTV."""
    baris_data = data_pasien_str.strip().split('\n')
    if not baris_data or baris_data[0] == "":
        messagebox.showerror("Error", "Data pasien masih kosong!")
        return

    # Konfigurasi Chrome Options
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    url1 = 'http://20.20.20.6/app.mersi-hospital/live/login'
    url2 = "http://20.20.20.6/app.mersi-hospital/live/ri/entry/transaksi_mrs_aktif" 

    try: 
        driver.get(url1)   
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys("20224015") 
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("2024") 
        password_field.send_keys(Keys.RETURN) 
        time.sleep(2) 
        
        # Looping untuk setiap pasien di Tkinter Text
        for item in baris_data:
            item = item.strip()
            if not item:
                continue
            
            # Parsing data berdasarkan pemisah '-'
            # Format: namaRuang-sistole-diastole-nadi-spo2-statusOksigen-suhu-respirasi
            pecah = item.split('-')
            if len(pecah) < 8:
                print(f"Format salah untuk baris: {item}")
                continue
                
            nama_ruang   = pecah[0].strip() # Contoh: "310 Bed D"
            sistole      = pecah[1].strip()
            diastole     = pecah[2].strip()
            nadi         = pecah[3].strip()
            spo2         = pecah[4].strip()
            status_oks   = int(pecah[5].strip()) # Diubah ke integer untuk pengecekan kondisi
            suhu         = pecah[6].strip()
            respirasi    = pecah[7].strip()

            # Navigasi ke halaman transaksi MRS aktif
            driver.get(url2) 
            
            # Cari baris berdasarkan nama ruang/bed pasien
            row_target = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, f"//tr[contains(., '{nama_ruang}')]"))
            )
            row_target.click()  
            time.sleep(1) 
            
            # Klik tombol RME (Membuka tab baru)
            btn_rme = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btn-rme"))
            )
            btn_rme.click() 
            
            # Pindah fokus ke tab baru
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[-1])
            
            # Tunggu dan ubah URL ke halaman pemeriksaan_ttv
            time.sleep(2) 
            current_url = driver.current_url
            
            if "asperawat_ranap" in current_url:
                new_url = current_url.replace("asperawat_ranap", "pemeriksaan_ttv")  
                driver.get(new_url)
                
                # --- AUTOMASI DI HALAMAN PEMERIKSAAN TTV --- 
                # 1. Tunggu hingga halaman selesai dimuat, lalu klik elemen collapse "Tulis Data"
                collapse_btn = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//h3/a[@data-card-widget='collapse' and contains(text(), 'Tulis Data')]"))
                )
                collapse_btn.click()
                time.sleep(1) # Jeda 1 detik sesuai instruksi
                
                # 2. Isi form TTV
                # Respirasi
                driver.find_element(By.ID, "txtresp").clear()
                driver.find_element(By.ID, "txtresp").send_keys(respirasi)
                
                # SpO2
                driver.find_element(By.ID, "txtspo2").clear()
                driver.find_element(By.ID, "txtspo2").send_keys(spo2)
                
                # Status Oksigen (Radio button: 0 = Tidak, > 0 = Ya)
                if status_oks == 0:
                    radio_tidak = driver.find_element(By.XPATH, "//input[@id='txtinso2' and @value='0']")
                    if not radio_tidak.is_selected():
                        radio_tidak.click()
                else:
                    radio_ya = driver.find_element(By.XPATH, "//input[@id='txtinso2' and @value='2']")
                    if not radio_ya.is_selected():
                        radio_ya.click()
                
                # Suhu / Temperature
                driver.find_element(By.ID, "txttemp").clear()
                driver.find_element(By.ID, "txttemp").send_keys(suhu)
                
                # Sistole (Tekanan Darah Sistolik)
                driver.find_element(By.ID, "txtbp").clear()
                driver.find_element(By.ID, "txtbp").send_keys(sistole)
                
                # Diastole (Tekanan Darah Diastolik)
                driver.find_element(By.ID, "txtbp1").clear()
                driver.find_element(By.ID, "txtbp1").send_keys(diastole)
                
                # Nadi / Heart Rate
                driver.find_element(By.ID, "txthr").clear()
                driver.find_element(By.ID, "txthr").send_keys(nadi)
                
                # 3. Jeda waktu 1 detik lalu klik tombol save
                time.sleep(1)
                btn_save = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "save"))
                )
                btn_save.click()
                
                # 4. Menunggu halaman selesai mereload setelah save
                print("Menyimpan data TTV, menunggu halaman selesai mereload...")
                WebDriverWait(driver, 15).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(1.5)
                print(f"Berhasil menyimpan data TTV untuk pasien: {nama_ruang}")

                # --- AUTOMASI DI HALAMAN CPPT ---
                current_url_cppt = driver.current_url
                if "pemeriksaan_ttv" in current_url_cppt:
                    cppt_url = current_url_cppt.replace("pemeriksaan_ttv", "cppt")
                    driver.get(cppt_url)
                    
                    print(f"Berpindah ke halaman CPPT: {cppt_url}")
                    WebDriverWait(driver, 15).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                    time.sleep(1)
                    
                    try:
                        btn_copy_perawat = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "(//tr[./td[2][contains(text(), 'Perawat')]])[1]//button[@name='btncopy']"))
                        )
                        btn_copy_perawat.click()
                        print("Berhasil mengklik tombol 'Salin Ke Form' milik Perawat pertama di CPPT.")
                        time.sleep(2)
                    except Exception as e_cppt:
                        print(f"Gagal menemukan atau mengklik tombol copy perawat di CPPT: {e_cppt}")
                else:
                    print("URL tidak mengandung 'pemeriksaan_ttv', gagal melakukan redirect ke CPPT.")
            # Tutup tab pasien saat ini dan kembali ke tab utama untuk iterasi berikutnya
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)

        messagebox.showinfo("Sukses", "Semua data TTV pasien berhasil diproses dan disimpan!")

    except Exception as e:
        messagebox.showerror("Terjadi Error", f"Error: {e}")

def tombol_mulai_klik():
    """Fungsi pemicu saat tombol di Tkinter diklik."""
    data_teks = text_input.get("1.0", END)
    t = threading.Thread(target=jalankan_automasi, args=(data_teks,))
    t.start()

# --- PEMBUATAN GUI TKINTER ---
root = Tk()
root.title("Auto Input TTV Pasien - Mersi Hospital")
root.geometry("650x480")

label_info = Label(root, text="Masukkan data TTV pasien (Format: namaRuang-sistole-diastole-nadi-spo2-statusOksigen-suhu-respirasi):\n(Satu baris untuk satu pasien)", justify=LEFT)
label_info.pack(padx=10, pady=10, anchor="w")

# Text Area untuk input banyak baris
text_input = Text(root, height=15, width=75)
text_input.pack(padx=10, pady=5)

# Contoh teks default bantu
contoh_data = "310 Bed D-120-80-80-98-0-36.5-20\n310 Bed C-110-81-71-97-2-36.1-21"
text_input.insert(END, contoh_data)

# Tombol Mulai
btn_mulai = Button(root, text="Mulai Automasi", bg="green", fg="white", font=("Arial", 10, "bold"), command=tombol_mulai_klik)
btn_mulai.pack(padx=10, pady=15)

root.mainloop()