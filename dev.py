import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from tkinter import *
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

def proses_satu_pasien(data_pasien): 
    pecah = data_pasien.split('-')
    if len(pecah) < 8:
        print(f"Format salah untuk data: {data_pasien}")
        return 
        
    nama_ruang   = pecah[0].strip()
    sistole      = pecah[1].strip()
    diastole     = pecah[2].strip()
    nadi         = pecah[3].strip()
    spo2         = pecah[4].strip()
    status_oks   = int(pecah[5].strip())
    suhu         = pecah[6].strip()
    respirasi    = pecah[7].strip() 
    
    chrome_options = Options()   
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    url1 = 'http://20.20.20.6/app.mersi-hospital/live/login'
    url2 = "http://20.20.20.6/app.mersi-hospital/live/ri/entry/transaksi_mrs_aktif" 

    try: 
        # 1. Login ke aplikasi rumah sakit
        driver.get(url1)   
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys("20224015") 
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("2024") 
        password_field.send_keys(Keys.RETURN) 
        time.sleep(2) 
 
        # 2. Navigasi ke daftar pasien aktif & buka RME
        driver.get(url2)  
        row_target = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, f"//tr[contains(., '{nama_ruang}')]"))
        )
        row_target.click()  
        time.sleep(1)  
        
        btn_rme = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btn-rme"))
        )
        btn_rme.click()  
        
        # Pindah ke tab/window baru RME pasien
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[-1]) 
        time.sleep(2)  
        
        current_url = driver.current_url
        if "asperawat_ranap" in current_url:
            new_url = current_url.replace("asperawat_ranap", "pemeriksaan_ttv")  
            driver.get(new_url) 
            
            # 3. Buka Form Tulis Data (Collapse button)
            collapse_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//h3/a[@data-card-widget='collapse' and contains(text(), 'Tulis Data')]"))
            )
            collapse_btn.click()
            time.sleep(0.5)  

            # 4. Input awal untuk memicu kalkulasi Total Skor oleh sistem web
            driver.find_element(By.ID, "txtresp").clear()
            driver.find_element(By.ID, "txtresp").send_keys(respirasi) 
            driver.find_element(By.ID, "txtspo2").clear()
            driver.find_element(By.ID, "txtspo2").send_keys(spo2) 
            
            if status_oks == 0:
                radio_tidak = driver.find_element(By.XPATH, "//input[@id='txtinso2' and @value='0']")
                if not radio_tidak.is_selected():
                    radio_tidak.click()
            else:
                radio_ya = driver.find_element(By.XPATH, "//input[@id='txtinso2' and @value='2']")
                if not radio_ya.is_selected():
                    radio_ya.click() 
                    
            driver.find_element(By.ID, "txttemp").clear()
            driver.find_element(By.ID, "txttemp").send_keys(suhu) 
            driver.find_element(By.ID, "txtbp").clear()
            driver.find_element(By.ID, "txtbp").send_keys(sistole) 
            driver.find_element(By.ID, "txtbp1").clear()
            driver.find_element(By.ID, "txtbp1").send_keys(diastole) 
            driver.find_element(By.ID, "txthr").clear()
            driver.find_element(By.ID, "txthr").send_keys(nadi) 
            
            time.sleep(0.5) # Jeda agar JavaScript menghitung total skor di halaman

            # 5. Ambil Total Skor yang dihasilkan sistem
            try:
                skor_elem = driver.find_element(By.ID, "txttotalskor")
                total_skor = int(skor_elem.get_attribute("value") or 0)
            except:
                total_skor = 0 

            print(f"Pasien {nama_ruang} - Total Skor: {total_skor}")

            # 6. Tentukan rentang waktu shift & interval pengisian berdasarkan skor
            now = datetime.now()
            jam = now.hour

            if 7 <= jam < 14:
                start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
                end_time = now.replace(hour=14, minute=0, second=0, microsecond=0)
            elif 14 <= jam < 21:
                start_time = now.replace(hour=14, minute=0, second=0, microsecond=0)
                end_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
            else:
                if jam >= 21:
                    start_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
                    end_time = (now + timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
                else:
                    start_time = (now - timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
                    end_time = now.replace(hour=7, minute=0, second=0, microsecond=0)

            waktu_input_list = []
            current_loop_time = start_time
            
            while current_loop_time <= end_time:
                waktu_input_list.append(current_loop_time)
                if total_skor <= 1:
                    break 
                elif 2 <= total_skor <= 4:
                    current_loop_time += timedelta(hours=2) 
                elif 5 <= total_skor <= 6:
                    current_loop_time += timedelta(hours=1) 
                else: 
                    current_loop_time += timedelta(minutes=15) 

            if not waktu_input_list:
                waktu_input_list.append(now)

            # ==========================================================
            # 7. TARUH KODE PERBAIKANNYA DI SINI (Gantikan looping for lama)
            # ==========================================================
            for i, waktu_target in enumerate(waktu_input_list):
                formatted_time = waktu_target.strftime("%Y-%m-%d %H:%M:%S")
                print(f"Sedang menginput untuk waktu: {formatted_time}")
                
                # A. Pastikan form dalam keadaan terbuka (karena setelah save, halaman reload & tertutup)
                form_terbuka = False
                for attempt in range(3): 
                    try:
                        resp_elem = driver.find_element(By.ID, "txtresp")
                        if resp_elem.is_displayed():
                            form_terbuka = True
                            break
                    except:
                        pass
                    
                    try:
                        collapse_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//h3/a[@data-card-widget='collapse' and contains(text(), 'Tulis Data')]"))
                        )
                        collapse_btn.click()
                        time.sleep(0.5) 
                    except Exception as e:
                        print(f"Percobaan {attempt+1}: Gagal klik tombol collapse: {e}")
                        time.sleep(1)

                if not form_terbuka:
                    print(f"Gagal membuka form TTV untuk waktu {formatted_time}, melewati iterasi ini.")
                    continue 

                # B. Isi ulang data TTV
                resp_elem = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "txtresp"))
                )
                resp_elem.clear()
                resp_elem.send_keys(respirasi) 
                
                driver.find_element(By.ID, "txtspo2").clear()
                driver.find_element(By.ID, "txtspo2").send_keys(spo2) 
                
                if status_oks == 0:
                    radio_tidak = driver.find_element(By.XPATH, "//input[@id='txtinso2' and @value='0']")
                    if not radio_tidak.is_selected():
                        radio_tidak.click()
                else:
                    radio_ya = driver.find_element(By.XPATH, "//input[@id='txtinso2' and @value='2']")
                    if not radio_ya.is_selected():
                        radio_ya.click() 
                        
                driver.find_element(By.ID, "txttemp").clear()
                driver.find_element(By.ID, "txttemp").send_keys(suhu) 
                
                driver.find_element(By.ID, "txtbp").clear()
                driver.find_element(By.ID, "txtbp").send_keys(sistole) 
                
                driver.find_element(By.ID, "txtbp1").clear()
                driver.find_element(By.ID, "txtbp1").send_keys(diastole) 
                
                driver.find_element(By.ID, "txthr").clear()
                driver.find_element(By.ID, "txthr").send_keys(nadi) 

                # C. Masukkan tanggal dan waktu sesuai jadwal interval (jam 8, jam 10, jam 12, dst.)
                tgl_input = driver.find_element(By.ID, "txttgl")
                tgl_input.clear()
                tgl_input.send_keys(formatted_time)
                
                time.sleep(0.5)
 
                btn_save = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "save"))
                )
                
                # Simpan referensi tombol save sebelum diklik
                old_btn_save = btn_save 
                btn_save.click()
                 
                try:
                    WebDriverWait(driver, 15).until(
                        EC.staleness_of(old_btn_save)
                    )
                except Exception as e:
                    print(f"Peringatan: Timeout menunggu halaman reload: {e}")
                 

    except Exception as e:
        print(f"Error pada ruang {nama_ruang}: {e}")
    finally:
        pass

def jalankan_semua_automasi(data_teks):
    baris_data = [b.strip() for b in data_teks.strip().split('\n') if b.strip()]
    if not baris_data:
        messagebox.showerror("Error", "Data pasien masih kosong!")
        return
 
    maxWindow = min(len(baris_data), 10) 
    with ThreadPoolExecutor(max_workers=maxWindow) as executor:
        executor.map(proses_satu_pasien, baris_data) 

def tombol_mulai_klik(): 
    data_teks = text_input.get("1.0", END)
    t = threading.Thread(target=jalankan_semua_automasi, args=(data_teks,))
    t.start()
 
# Konfigurasi Tampilan GUI Tkinter
root = Tk()
root.title("Auto Input TTV & CPPT Pasien - Mersi Hospital (Simultan)")
root.geometry("650x480")

label_info = Label(root, text="Masukkan data TTV (Bisa banyak baris, 1 baris 1 pasien):\nFormat: namaRuang-sistole-diastole-nadi-spo2-statusOksigen-suhu-respirasi", justify=LEFT)
label_info.pack(padx=10, pady=10, anchor="w") 

text_input = Text(root, height=8, width=75)
text_input.pack(padx=10, pady=5) 

contoh_data = (
    "310 Bed D-190-100-80-98-3-36.2-20\n"
    "310 Bed C-200-80-75-99-1-36.5-18" 
)
text_input.insert(END, contoh_data) 

btn_mulai = Button(root, text="Mulai Automasi Simultan", bg="green", fg="white", font=("Arial", 10, "bold"), command=tombol_mulai_klik)
btn_mulai.pack(padx=10, pady=15) 

root.mainloop()