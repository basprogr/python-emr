import re
import requests
import threading
import time 
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from tkinter import *
from tkinter import ttk, messagebox 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
  
SUPABASE_URL = "https://qjwmhtnfowkmwoflwhzy.supabase.co/rest/v1/logbook" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFqd21odG5mb3drbXdvZmx3aHp5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY5NjAwMTIsImV4cCI6MjEwMjUzNjAxMn0.ERWHxYn3GJJKHXJaJaZ2vnypcEM0DF8QE4DR_mjF-3s"
 
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}
 
DAFTAR_AKUN = { 
    "Berti": {"username": "20223027", "pass": "2829"}, 
    "Danang Kurniawan": {"username": "20120140", "pass": "b4rb"},
    "Filda Dwi Cahyani": {"username": "20223086", "pass": "1997"},
    "Fita Purnamasari": {"username": "20122032", "pass": "1226"}, 
    "Puput Citra": {"username": "20224042", "pass": "4321"}, 
    "Riska Diana": {"username": "20224055", "pass": "1357"},
    "Selvi Juliana": {"username": "20224046", "pass": "1234"},
    "Suari Arisona": {"username": "20217037", "pass": "0723"},
    "Tamela": {"username": "20115102", "pass": "1412"}, 
    "Yuni Nofita": {"username": "20210062", "pass": "1212"}
} 

def proses_satu_pasien(data_pasien, kredensial_ganjil, kredensial_genap, nama_perawat_ganjil, nama_perawat_genap):    
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
 
    try: 
        kata_pertama = nama_ruang.split()[0]
        angka_ruang = int(''.join(filter(str.isdigit, kata_pertama))) 
         
        if angka_ruang == 301:
            kredensial = kredensial_genap 
            selected_nama = nama_perawat_genap  
        elif angka_ruang == 302:
            kredensial = kredensial_ganjil 
            selected_nama = nama_perawat_ganjil 
        else: 
            if angka_ruang % 2 != 0:
                kredensial = kredensial_ganjil 
                selected_nama = nama_perawat_ganjil
            else:
                kredensial = kredensial_genap  
                selected_nama = nama_perawat_genap
    except (ValueError, IndexError): 
        kredensial = kredensial_ganjil
        selected_nama = nama_perawat_ganjil
 
    chrome_options = Options()   
    # chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
 
    url_patient_list = "http://20.20.20.6/app.mersi-hospital/live/ri/entry/transaksi_mrs_aktif"  

    try: 
        driver.get('http://20.20.20.6/app.mersi-hospital/live/login')   
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        ) 
        username_field.send_keys(kredensial["username"]) 
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(kredensial["pass"]) 
        password_field.send_keys(Keys.RETURN) 
        time.sleep(2)  
        driver.get(url_patient_list)  
        row_target = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, f"//tr[contains(., '{nama_ruang}')]"))
        )
        row_target.click()  
        time.sleep(1)  
        btn_rme = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btn-rme"))
        )
        btn_rme.click()   
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2)) 
        tab_lama = driver.window_handles[0] 
        driver.switch_to.window(driver.window_handles[-1]) 
        time.sleep(1)   
        driver.switch_to.window(tab_lama) 
        driver.close()               
        driver.switch_to.window(driver.window_handles[0]) 
        time.sleep(2)  
        
        current_url = driver.current_url 
        no_rm = "-"
        nama_pasien = "-"
        diagnosa_medis = "-"
        
        if "asperawat_ranap" in current_url: 
            handoverURL = current_url.replace("asperawat_ranap", "handover_dewasa1")  
            driver.get(handoverURL)  
            try:
                no_rm_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'No RM')]/following-sibling::div"))
                )
                no_rm = no_rm_elem.text.replace(":", "").strip()   
                nama_pasien_elem = driver.find_element(By.XPATH, "//div[contains(text(), 'Nama Pasien')]/following-sibling::div//strong") 
                nama_pasien_raw = nama_pasien_elem.text.strip()  
                parts = nama_pasien_raw.split(" ") 
                if len(parts) > 1:
                    nama_pasien = " ".join(parts[1:])
                else:
                    nama_pasien = nama_pasien_raw  
                print(f"No RM: {no_rm}, Nama: {nama_pasien}") 

                first_row = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//table[@id='datalist']/tbody/tr[1]"))
                ) 
                situation_td = first_row.find_element(By.XPATH, "./td[4]")
                situation_text = situation_td.text 
                for line in situation_text.split("\n"):
                    if "Diagnosa Medis" in line:
                        diagnosa_medis = line.split(":", 1)[1].strip()
                        break
            except Exception as e:
                print(f"[WARNING] {e}")
         
            tanggal_hari_ini = datetime.now().strftime("%Y%m%d") 
            payload = {
                "room": nama_ruang,
                "patient_name": nama_pasien,
                "no_rm": no_rm,
                "diagnosa_medis": diagnosa_medis,
                "created_at": tanggal_hari_ini
            } 
            try: 
                cek_url = f"{SUPABASE_URL}?room=eq.{nama_ruang}&created_at=eq.{tanggal_hari_ini}"
                resp_cek = requests.get(cek_url, headers=HEADERS)
                existing_data = resp_cek.json()
        
                if existing_data and len(existing_data) > 0: 
                    row_id = existing_data[0]['id']
                    patch_url = f"{SUPABASE_URL}?id=eq.{row_id}"
                    response = requests.patch(patch_url, json=payload, headers=HEADERS)
        
                    if response.status_code in [200, 204]:
                        print(f"-> [UPDATE SUKSES] Data pasien {nama_pasien} (Ruang: {nama_ruang}) diperbarui.")
                    else:
                        print(f"-> [GAGAL UPDATE] Status: {response.status_code}, Respon: {response.text}")
                else: 
                    response = requests.post(SUPABASE_URL, json=payload, headers=HEADERS)
                    if response.status_code in [200, 201]:
                        print(f"-> [INSERT SUKSES] Data pasien {nama_pasien} (Ruang: {nama_ruang}) ditambahkan.")
                    else:
                        print(f"-> [GAGAL INSERT] Status: {response.status_code}, Respon: {response.text}") 
            except Exception as req_err:
                print(f"-> [ERROR] Kesalahan koneksi Supabase: {req_err}") 

            try: 
                btn_copy_pertama = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//table[@id='datalist']/tbody/tr[1]//button[@id='btncopy']"))
                )
                btn_copy_pertama.click()  
                time.sleep(1) 
                now = datetime.now()
                hour = now.hour 
                if 7 <= hour < 14:
                    shift_val = "I" 
                    tgl_penyerahan_val = now.strftime("%d-%m-%Y") + " 14:00"
                elif 14 <= hour < 21:
                    shift_val = "II" 
                    tgl_penyerahan_val = now.strftime("%d-%m-%Y") + " 21:00"
                else:
                    shift_val = "III" 
                    if hour >= 21: 
                        besok = now + timedelta(days=1)
                        tgl_penyerahan_val = besok.strftime("%d-%m-%Y") + " 07:00"
                    else: 
                        tgl_penyerahan_val = now.strftime("%d-%m-%Y") + " 07:00" 
                select_shift_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "selshift"))
                )
                Select(select_shift_elem).select_by_value(shift_val) 
                
                input_tgl_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "txttgl_penyerahan"))
                )
                input_tgl_elem.clear()
                input_tgl_elem.send_keys(tgl_penyerahan_val)  
                perawat_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//select[@id='selperawat_1']/option[contains(text(), '{selected_nama}')]")) 
                )
                perawat_option.click() 
                time.sleep(1) 
                btn_simpan = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "save"))
                )

                btn_simpan.click() 
                WebDriverWait(driver, 10).until(EC.staleness_of(btn_simpan)) 
                
                driver.get('http://20.20.20.6/app.mersi-hospital/live/login/log_out')   
                username_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                ) 
                username_field.send_keys('20224015') 
                password_field = driver.find_element(By.ID, "password")
                password_field.send_keys('2024') 
                password_field.send_keys(Keys.RETURN)
                
                time.sleep(2) # GANTI DENGAN MENUNGGU ELEMEN MUNCUL
 
                driver.get(url_patient_list)  
                row_target = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, f"//tr[contains(., '{nama_ruang}')]"))
                )
                row_target.click()  
                time.sleep(1)  
                btn_rme = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "btn-rme"))
                )
                btn_rme.click()   
                WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2)) 
                tab_lama = driver.window_handles[0] 
                driver.switch_to.window(driver.window_handles[-1]) 
                time.sleep(2)   
                driver.switch_to.window(tab_lama) 
                driver.close()  
                driver.switch_to.window(driver.window_handles[0]) 
                time.sleep(2)   
 
                current_url = driver.current_url 
                if "asperawat_ranap" in current_url:
                    vitalSign_URL = current_url.replace("asperawat_ranap", "pemeriksaan_ttv")  
                    driver.get(vitalSign_URL)  
                    collapse_btn = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, "//h3/a[@data-card-widget='collapse' and contains(text(), 'Tulis Data')]"))
                    )
                    collapse_btn.click()
                    time.sleep(1)
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
                    time.sleep(1)
                    btn_save = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "save"))
                    )
                    btn_save.click()  
                    WebDriverWait(driver, 15).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                    time.sleep(1.5)  
                    current_url_cppt = driver.current_url
                    if "pemeriksaan_ttv" in current_url_cppt:
                        cppt_url = current_url_cppt.replace("pemeriksaan_ttv", "cppt")
                        driver.get(cppt_url) 
                        WebDriverWait(driver, 15).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                        time.sleep(1) 
                        try:
                            btn_copy_perawat = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "(//tr[./td[2][contains(text(), 'Perawat')]])[1]//button[@name='btncopy']"))
                            )
                            btn_copy_perawat.click() 
                            time.sleep(2)
                        except Exception as e_cppt:
                            print(f"Error: {e_cppt}")
                
                        now = datetime.now()
                        current_date_str = now.strftime("%Y-%m-%d")
                        tomorrow_date_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
                        jam = now.hour
                
                        if 6 < jam < 14:
                            val_txttgl = f"{current_date_str} 13:00:00"
                            val_txttgl_operan = f"{current_date_str} 14:00:00"
                            val_shift = "I"  # Pagi
                        elif 13 < jam < 21:
                            val_txttgl = f"{current_date_str} 20:00:00"
                            val_txttgl_operan = f"{current_date_str} 21:00:00"
                            val_shift = "II"  # Siang
                        else:
                            if jam >= 21:
                                val_txttgl = f"{tomorrow_date_str} 06:00:00"
                                val_txttgl_operan = f"{tomorrow_date_str} 07:00:00"
                            else:
                                val_txttgl = f"{current_date_str} 06:00:00"
                                val_txttgl_operan = f"{current_date_str} 07:00:00"
                            val_shift = "III"  # Malam
                
                        txttgl_elem = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.ID, "txttgl"))
                        ) 
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", txttgl_elem)
                        time.sleep(0.5) 
                        try:
                            txttgl_elem.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", txttgl_elem) 
                        time.sleep(0.3)
                        txttgl_elem.clear()
                        txttgl_elem.send_keys(val_txttgl)
                        time.sleep(0.5)
                        txttgl_elem.send_keys(Keys.ESCAPE)
                        time.sleep(1.0)
                
                        try:
                            time.sleep(1)
                            text_s = driver.execute_script("return CKEDITOR.instances.txtevaluasi_s.getData();") or ""
                            text_s = re.sub(r'\b(pasien|px|klien|mengeluh|mengatakan)\b\s*', '', text_s, flags=re.IGNORECASE).strip()  
                            driver.execute_script("CKEDITOR.instances.txtevaluasi_s.setData(arguments[0]);", text_s)
                            print("Berhasil memperbarui txtevaluasi_s via CKEditor API.")
                        except Exception as e_s:
                            print(f"Gagal memproses txtevaluasi_s: {e_s}")
                
                        try:
                            time.sleep(0.5)
                            text_o = driver.execute_script("return CKEDITOR.instances.txtevaluasi_o.getData();") or "" 
                            simple_pattern = r"Rr\s*:\s*.*?SpO2\s*:\s*\d+%\s*(?:dengan\s+O2(?:\s*\d+\s*(?:lpm|Lpm|L/min|L/mnt)?)?|tanpa\s+O2)?"
                            text_bersih = re.sub(simple_pattern, "", text_o, flags=re.IGNORECASE | re.DOTALL) 
                            if status_oks > 0:
                                str_oksigen = f"dengan O2 {status_oks} lpm"
                            else:
                                str_oksigen = "tanpa O2" 
                                new_vitals = f"Rr : {respirasi} x/menit\nSuhu : {suhu} °C\nNadi : {nadi} x/menit\nTD : {sistole}/{diastole} mmHg\nSpO2 : {spo2}% {str_oksigen}"
                                final_text = text_bersih.strip() + "\n" + new_vitals 
                                driver.execute_script("CKEDITOR.instances.txtevaluasi_o.setData(arguments[0]);", final_text)
                        except Exception as e_o:
                            print(f"Error: {e_o}")
                
                        try:
                            time.sleep(0.5)
                            text_a = (driver.execute_script("return CKEDITOR.instances.txtevaluasi_a.getData();") or "").lower() 
                            mapping_a = {
                                'bersihan': 'bersihan jalan napas tidak efektif',
                                'diare': 'diare',
                                'hipertermi': 'hipertermia',
                                'hipervolemi': 'hipervolemia',
                                'hipovolemi': 'hipovolemia',
                                'integritas': 'gangguan integritas kulit dan jaringan',
                                'ketidakstabilan': 'ketidakstabilan kadar glukosa darah',
                                'nausea': 'nausea',
                                'nyeri': 'nyeri akut',
                                'curah jantung': 'penurunan curah jantung',
                                'adaptif': 'penurunan kapasitas adaptif intrakranial',
                                'pola': 'pola napas tidak efektif',
                                'jatuh': 'resiko jatuh',
                                'infeksi': 'resiko infeksi'
                            } 
                            matched_keys = []
                            formatted_a_list = []
                            for key, val in mapping_a.items():
                                if key in text_a:
                                    matched_keys.append(key)
                                    formatted_a_list.append(val) 
                            if formatted_a_list: 
                                numbered_items = [f"{i+1}. {item}" for i, item in enumerate(formatted_a_list)]
                                formatted_a_html = "<br>".join(numbered_items) 
                                driver.execute_script("CKEDITOR.instances.txtevaluasi_a.setData(arguments[0]);", formatted_a_html)
                        except Exception as e_a:
                            print(f"Error on txtevaluasi_a: {e_a}")
                
                        p_dict = {
                            'bersihan': ['Frekuensi napas membaik', 'Pola napas membaik', 'wheezing/ronchi menurun'],
                            'diare': ['tidak ada tanda gejala hipovolemia', 'konsistensi feses membaik', 'kontrol pengeluaran feses meningkat', 'frekuensi defekasi membaik'],
                            'hipertermi': ['Kulit tidak kemerahan', 'Suhu tubuh membaik'],
                            'hipervolemi': ['Turgor kulit membaik', 'Keluaran urin meningkat', 'Edema menurun'],
                            'hipovolemi': ['kekuatan nadi meningkat', 'perasaan lemah menurun', 'tekanan darah membaik', 'turgor kulit membaik'],
                            'integritas': ['Perfusi perifer baik'],
                            'ketidakstabilan': ['Kadar glukosa dalam darah membaik'],
                            'nausea': ['Nafsu makan meningkat', 'keluhan mual menurun'],
                            'nyeri': ['keluhan nyeri menurun', 'grimace menurun'],
                            'curah jantung': ['status hemodinamik membaik'],
                            'adaptif': ['Refleks neurologis membaik', 'Fungsi kognitif meningkat'],
                            'pola': ['frekuensi napas membaik', 'dispneu menurun'],
                            'jatuh': ['tidak ada kejadian jatuh'],
                            'infeksi': ['tidak terjadi tanda tanda infeksi', 'kadar sel darah putih dalam batas normal']
                        } 
                        list_p = []
                        for k in matched_keys:
                            if k in p_dict:
                                list_p.extend(p_dict[k]) 
                        try:
                            if list_p:
                                numbered_items = [f"{i+1}. {item}" for i, item in enumerate(list_p)]
                                list_p_html = "<br>".join(numbered_items) 
                                driver.execute_script("CKEDITOR.instances.txtevaluasi_p.setData(arguments[0]);", list_p_html)
                        except Exception as e_p:
                            print(f"Error on txtevaluasi_p: {e_p}")
                
                        instruksi_dict = {
                            'bersihan': [
                                'Monitor pola napas',
                                'Monitor adanya bunyi napas tambahan',
                                'Monitor saturasi oksigen'
                            ],
                            'diare': [
                                'Monitor intake dan output cairan',
                                'Monitor tanda dan gejala hipovolemia',
                                'Monitor jumlah pengeluaran diare'
                            ],
                            'integritas': [ 
                                'Identifikasi penyebab gangguan integritas kulit'
                            ],
                            'hipertermi': [
                                'Monitor Suhu tubuh',
                                'Longgarkan atau lepaskan pakaian',
                                'Lakukan pendinginan eksternal'
                            ],
                            'hipervolemi': [
                                'Periksa tanda & gejala hipervolemia',
                                'Monitor Status hemodinamik',
                                'Monitor intake & output cairan',
                                'Batasi asupan cairan dan garam'
                            ],
                            'hipovolemi': [
                                'Periksa tanda dan gejala hipovolemia',
                                'Monitor intake dan output cairan',
                                'Kolaborasi pemberian cairan'
                            ],
                            'ketidakstabilan': [
                                'Identifikasi tanda dan gejala hipoglikemi',
                                'Monitor kadar glukosa darah, jika perlu'
                            ],
                            'nausea': [
                                'Monitor keseimbangan cairan dan elektrolit',
                                'Identifikasi isyarat nonverbal ketidaknyamanan',
                                'Kontrol lingkungan penyebab muntah'
                            ],
                            'nyeri': [
                                'Identifikasi lokasi, karakteristik, durasi, frekuensi, kualitas, intensitas nyeri',
                                'Identifikasi skala nyeri',
                                'Identifikasi respon nyeri non verbal',
                                'Identifikasi factor yang memperberat dan memperingan nyeri'
                            ],
                            'curah jantung': [
                                'Monitor status kardiopulmonal',
                                'Monitor ststus oksigenasi'
                            ],
                            'adaptif': [
                                'Monitor penurunan tingkat kesaadaran',
                                'Monitor status neurologis'
                            ],
                            'pola': [
                                'Monitor pola napas',
                                'Palpasi kesimetrisan ekspansi paru',
                                'Monitor saturasi oksigen'
                            ],
                            'jatuh': [
                                'Identifikasi faktor risiko jatuh',
                                'pastikan roda tempat tidur selalu dalam kondisi terkunci',
                                'pasang handrail tempat tidur'
                            ],
                            'infeksi': [
                                'Monitor tanda dan gejala infeksi local dan sistemik.'
                            ]
                        }
                
                        list_instruksi = []
                        for k in matched_keys:
                            if k in instruksi_dict:
                                list_instruksi.extend(instruksi_dict[k]) 
                        try:
                            if list_instruksi:
                                numbered_items = [f"{i+1}. {item}" for i, item in enumerate(list_instruksi)]
                                list_instruksi_html = "<br>".join(numbered_items) 
                                driver.execute_script("CKEDITOR.instances.txtinstruksi.setData(arguments[0]);", list_instruksi_html)
                        except Exception as e_instruksi:
                            print(f"Error on txtinstruksi: {e_instruksi}")
                
                        radio_seloperan = driver.find_element(By.XPATH, "//input[@id='seloperan' and @value='Ya']")
                        if not radio_seloperan.is_selected():
                            radio_seloperan.click()
                
                        txttgl_operan_elem = driver.find_element(By.ID, "txttgl_operan")
                        txttgl_operan_elem.click()
                        time.sleep(0.3)
                        txttgl_operan_elem.clear()
                        txttgl_operan_elem.send_keys(val_txttgl_operan)
                        time.sleep(0.5)
                        txttgl_operan_elem.send_keys(Keys.ESCAPE)
                        time.sleep(1.0) 
                        select_shift = Select(driver.find_element(By.ID, "selshift"))
                        select_shift.select_by_value(val_shift) 
                        time.sleep(1)  
                
                        if val_shift != 'I' :
                            try:
                                btn_save_cppt = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, "//button[@id='save' and @name='save' and @value='save']"))
                                ) 
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", btn_save_cppt)
                                time.sleep(0.5)  
                                try:
                                    btn_save_cppt.click()
                                except Exception:
                                    driver.execute_script("arguments[0].click();", btn_save_cppt) 
                                time.sleep(2)
                            except Exception as e_save:
                                print(f"Error clicking save CPPT: {e_save}")
                
                        current_url_cppt = driver.current_url
                        if "cppt" in current_url_cppt:
                            impl_url = current_url_cppt.replace("cppt", "implementasi_keperawatan")
                            driver.get(impl_url) 
                            WebDriverWait(driver, 15).until(
                                lambda d: d.execute_script("return document.readyState") == "complete"
                            )
                            time.sleep(1.5) 
                            try:
                                collapse_tulis = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.XPATH, "//div[@id='tulistransfer']//a[@data-card-widget='collapse']"))
                                )
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", collapse_tulis)
                                time.sleep(0.5)
                                try:
                                    collapse_tulis.click()
                                except Exception:
                                    driver.execute_script("arguments[0].click();", collapse_tulis)
                                time.sleep(1)
                            except Exception as e_tulis:
                                print(f"Error opening 'Tulis' card: {e_tulis}")
                
                            time.sleep(1.0) 
                            select_shift = Select(driver.find_element(By.ID, "selshift"))
                            select_shift.select_by_value(val_shift) 
                            time.sleep(1)
                
                            diagnosis_checkbox_mapping = {
                                'bersihan': '1.1',
                                'diare': '3.2',
                                'integritas': '13.1',
                                'hipertermi': '13.2',
                                'hipervolemi': '3.3',
                                'hipovolemi': '3.4',
                                'ketidakstabilan': '3.6',
                                'nausea': '8.3',
                                'nyeri': '8.4',
                                'curah jantung': '2.2',
                                'adaptif': '6.2',
                                'pola': '1.5',
                                'infeksi': '13.12',
                                'jatuh': '13.13'
                            }
                
                            for k in matched_keys:
                                if k in diagnosis_checkbox_mapping:
                                    val_checkbox = diagnosis_checkbox_mapping[k]
                                    try:
                                        checkbox_elem = WebDriverWait(driver, 5).until(
                                            EC.presence_of_element_located((By.XPATH, f"//input[@name='askep_diagnosis[]' and @value='{val_checkbox}']"))
                                        )
                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", checkbox_elem)
                                        time.sleep(0.3)
                                        if not checkbox_elem.is_selected():
                                            try:
                                                checkbox_elem.click()
                                            except Exception:
                                                driver.execute_script("arguments[0].click();", checkbox_elem)
                                            print(f"Checkbox untuk {k} (value={val_checkbox}) berhasil dicentang.")
                                    except Exception as e_cb:
                                        print(f"Gagal mencentang checkbox {k} (value={val_checkbox}): {e_cb}")
                
                            # 5. Mapping detail checkbox lanjutan berdasarkan diagnosis yang aktif (AJAX trigger)
                            detail_checkbox_mapping = {
                                'bersihan': [
                                    ("askep_penyebab[]", "1.1.2"), ("askep_penyebab[]", "1.1.8"),
                                    ("askep_gejala[]", "1.1.2.1"), ("askep_gejala[]", "1.1.2.11"),
                                    ("askep_kriteriahasil[]", "1.1.1"), ("askep_kriteriahasil[]", "1.1.11"), ("askep_kriteriahasil[]", "1.1.12"),
                                    ("askep_int_observasi[]", "1.1.1"), ("askep_int_observasi[]", "1.1.2"), ("askep_int_observasi[]", "1.1.8"),
                                    ("askep_int_kolaborasi[]", "1.1.1"),
                                    ("askep_imp_observasi[]", "1.1.1"), ("askep_imp_observasi[]", "1.1.11"), ("askep_imp_observasi[]", "1.1.2"), ("askep_imp_observasi[]", "1.1.8"),
                                    ("askep_imp_terapi[]", "1.1.1"), ("askep_int_terapi[]", "1.1.1"),
                                    ("askep_imp_kolaborasi[]", "1.1.1")
                                ],
                                'diare': [
                                    ("askep_penyebab[]", "3.2.1"), ("askep_penyebab[]", "3.2.3"),
                                    ("askep_gejala[]", "3.2.2.2"), ("askep_gejala[]", "3.2.2.4"),
                                    ("askep_kriteriahasil[]", "3.2.1"), ("askep_kriteriahasil[]", "3.2.8"), ("askep_kriteriahasil[]", "3.2.7"), ("askep_kriteriahasil[]", "3.2.9"),
                                    ("askep_int_observasi[]", "3.2.8"), ("askep_int_observasi[]", "3.2.6"), ("askep_int_observasi[]", "3.2.5"), ("askep_int_observasi[]", "3.2.4"), ("askep_int_observasi[]", "3.2.1"),
                                    ("askep_int_kolaborasi[]", "3.2.3"), ("askep_int_terapi[]", "3.2.3"),
                                    ("askep_imp_kolaborasi[]", "3.2.3"), ("askep_imp_terapi[]", "3.2.3"),
                                    ("askep_imp_observasi[]", "3.2.8"), ("askep_imp_observasi[]", "3.2.5"), ("askep_imp_observasi[]", "3.2.6"), ("askep_imp_observasi[]", "3.2.4"), ("askep_imp_observasi[]", "3.2.1")
                                ],
                                'integritas': [
                                    ("askep_imp_observasi[]", "13.1.1"), ("askep_int_observasi[]", "13.1.1"),
                                    ("askep_kriteriahasil[]", "13.1.4"), ("askep_kriteriahasil[]", "13.1.1"),
                                    ("askep_gejala[]", "13.1.1.3"), ("askep_penyebab[]", "13.1.2")
                                ],
                                'hipertermi': [
                                    ("askep_imp_kolaborasi[]", "13.2.1"), ("askep_imp_terapi[]", "13.2.6"),
                                    ("askep_imp_observasi[]", "13.2.2"), ("askep_imp_observasi[]", "13.2.1"),
                                    ("askep_int_kolaborasi[]", "13.2.1"), ("askep_int_terapi[]", "13.2.6"), ("askep_int_observasi[]", "13.2.2"),
                                    ("askep_kriteriahasil[]", "13.2.6"), ("askep_kriteriahasil[]", "13.2.1"),
                                    ("askep_gejala[]", "13.2.1.9"), ("askep_gejala[]", "13.2.1.3"),
                                    ("askep_penyebab[]", "13.2.5")
                                ],
                                'hipervolemi': [
                                    ("askep_imp_terapi[]", "3.3.2"),
                                    ("askep_imp_observasi[]", "3.3.3"), ("askep_imp_observasi[]", "3.3.4"), ("askep_imp_observasi[]", "3.3.1"),
                                    ("askep_int_terapi[]", "3.3.2"),
                                    ("askep_int_observasi[]", "3.3.4"), ("askep_int_observasi[]", "3.3.3"), ("askep_int_observasi[]", "3.3.1"),
                                    ("askep_kriteriahasil[]", "3.3.5"), ("askep_kriteriahasil[]", "3.3.2"), ("askep_kriteriahasil[]", "3.3.11"),
                                    ("askep_gejala[]", "3.3.2.2"), ("askep_penyebab[]", "3.3.1")
                                ],
                                'hipovolemi': [
                                    ("askep_imp_kolaborasi[]", "3.4.1"),
                                    ("askep_imp_observasi[]", "3.4.2"), ("askep_imp_observasi[]", "3.4.1"),
                                    ("askep_int_kolaborasi[]", "3.4.1"),
                                    ("askep_int_observasi[]", "3.4.2"), ("askep_int_observasi[]", "3.4.1"),
                                    ("askep_kriteriahasil[]", "3.4.2"), ("askep_kriteriahasil[]", "3.4.19"), ("askep_kriteriahasil[]", "3.4.1"),
                                    ("askep_gejala[]", "3.4.2.3"), ("askep_gejala[]", "3.4.1.2"),
                                    ("askep_penyebab[]", "3.4.4")
                                ],
                                'ketidakstabilan': [
                                    ("askep_imp_kolaborasi[]", "3.6.1"),
                                    ("askep_imp_observasi[]", "3.6.5"), ("askep_imp_observasi[]", "3.6.2"),
                                    ("askep_int_kolaborasi[]", "3.6.1"),
                                    ("askep_int_observasi[]", "3.6.5"), ("askep_int_observasi[]", "3.6.2"),
                                    ("askep_kriteriahasil[]", "3.6.12"),
                                    ("askep_gejala[]", "3.6.1.3"), ("askep_penyebab[]", "3.6.1")
                                ],
                                'nausea': [
                                    ("askep_imp_kolaborasi[]", "8.3.1"), ("askep_imp_terapi[]", "8.3.1"),
                                    ("askep_imp_observasi[]", "8.3.2"), ("askep_imp_observasi[]", "8.3.11"),
                                    ("askep_int_kolaborasi[]", "8.3.1"), ("askep_int_terapi[]", "8.3.1"), ("askep_int_observasi[]", "8.3.2"), ("askep_int_observasi[]", "8.3.11"),
                                    ("askep_kriteriahasil[]", "8.3.2"), ("askep_kriteriahasil[]", "8.3.1"),
                                    ("askep_gejala[]", "8.3.1.1"), ("askep_penyebab[]", "8.3.1")
                                ],
                                'nyeri': [
                                    ("askep_imp_kolaborasi[]", "8.4.1"), ("askep_imp_terapi[]", "8.4.3"),
                                    ("askep_imp_observasi[]", "8.4.3"), ("askep_imp_observasi[]", "8.4.1"),
                                    ("askep_int_kolaborasi[]", "8.4.1"), ("askep_int_terapi[]", "8.4.3"), ("askep_int_observasi[]", "8.4.3"), ("askep_int_observasi[]", "8.4.1"),
                                    ("askep_kriteriahasil[]", "8.4.2"),
                                    ("askep_gejala[]", "8.4.1.1"), ("askep_penyebab[]", "8.4.1")
                                ],
                                'curah jantung': [
                                    ("askep_imp_kolaborasi[]", "2.2.3"),
                                    ("askep_imp_observasi[]", "2.2.2"), ("askep_imp_observasi[]", "2.2.1"),
                                    ("askep_int_kolaborasi[]", "2.2.3"),
                                    ("askep_int_observasi[]", "2.2.2"), ("askep_int_observasi[]", "2.2.1"),
                                    ("askep_kriteriahasil[]", "2.2.3"), ("askep_kriteriahasil[]", "2.2.4"),
                                    ("askep_gejala[]", "2.2.1.9"), ("askep_penyebab[]", "2.2.2")
                                ],
                                'adaptif': [
                                    ("askep_imp_terapi[]", "6.2.10"), ("askep_imp_observasi[]", "6.2.2"),
                                    ("askep_int_terapi[]", "6.2.10"), ("askep_int_observasi[]", "6.2.2"),
                                    ("askep_kriteriahasil[]", "6.2.14"),
                                    ("askep_gejala[]", "6.2.2.6"), ("askep_penyebab[]", "6.2.3")
                                ],
                                'pola': [
                                    ("askep_imp_kolaborasi[]", "1.5.1"),
                                    ("askep_imp_observasi[]", "1.5.7"), ("askep_imp_observasi[]", "1.5.1"),
                                    ("askep_int_kolaborasi[]", "1.5.1"),
                                    ("askep_int_observasi[]", "1.5.8"), ("askep_int_observasi[]", "1.5.2"), ("askep_int_observasi[]", "1.5.1"),
                                    ("askep_kriteriahasil[]", "1.5.6"), ("askep_kriteriahasil[]", "1.5.11"), ("askep_kriteriahasil[]", "1.5.12"),
                                    ("askep_gejala[]", "1.5.2.3"), ("askep_gejala[]", "1.5.1.1"),
                                    ("askep_penyebab[]", "1.5.5"), ("askep_penyebab[]", "1.5.2")
                                ],
                                'infeksi': [
                                    ("askep_imp_terapi[]", "13.12.3"), ("askep_imp_observasi[]", "13.12.1"),
                                    ("askep_int_terapi[]", "13.12.3"), ("askep_int_observasi[]", "13.12.1"),
                                    ("askep_kriteriahasil[]", "13.12.5"),
                                    ("askep_penyebab[]", "13.12.7"), ("askep_penyebab[]", "13.12.2")
                                ],
                                'jatuh': [
                                    ("askep_imp_terapi[]", "13.13.3"), ("askep_imp_terapi[]", "13.13.2"),
                                    ("askep_imp_observasi[]", "13.13.3"), ("askep_imp_observasi[]", "13.13.1"),
                                    ("askep_int_terapi[]", "13.13.3"), ("askep_int_terapi[]", "13.13.2"),
                                    ("askep_int_observasi[]", "13.13.3"), ("askep_int_observasi[]", "13.13.1"),
                                    ("askep_penyebab[]", "13.13.2"), ("askep_penyebab[]", "13.13.12")
                                ]
                            }
                            time.sleep(1.5)
                
                            # Loop pencentangan elemen detail berdasarkan matched_keys
                            for k in matched_keys:
                                if k in detail_checkbox_mapping:
                                    for name_attr, val_attr in detail_checkbox_mapping[k]:
                                        try:
                                            detail_elem = WebDriverWait(driver, 3).until(
                                                EC.presence_of_element_located((By.XPATH, f"//input[@name='{name_attr}' and @value='{val_attr}']"))
                                            )
                                            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", detail_elem)
                                            time.sleep(0.1)
                                            if not detail_elem.is_selected():
                                                try:
                                                    detail_elem.click()
                                                except Exception:
                                                    driver.execute_script("arguments[0].click();", detail_elem)
                                        except Exception as e_detail:
                                            # Mengabaikan jika elemen tidak muncul/belum ter-load karena jeda AJAX
                                            pass 
                            time.sleep(1)  
                            # 6. Menekan tombol Simpan (Save) setelah semua checkbox tercentang
                            try:
                                btn_save_impl = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, "//button[@id='save' and @name='save' and @value='save']"))
                                )
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", btn_save_impl)
                                time.sleep(0.5)
                                try:
                                    btn_save_impl.click()
                                except Exception:
                                    driver.execute_script("arguments[0].click();", btn_save_impl)
                                print("Tombol Simpan implementasi keperawatan berhasil ditekan.")
                                time.sleep(2)
                            except Exception as e_save_impl:
                                print(f"Gagal menekan tombol Simpan implementasi: {e_save_impl}") 
                
            except Exception as auto_err:
                print(f"-> [WARNING AUTOMASI GAGAL] Gagal mengklik tombol copy baris pertama: {auto_err}")
 
    except Exception as e:
        print(f"Error pada ruang {nama_ruang}: {e}")
    finally: 
        driver.quit()
        btn_mulai.config(state="normal") 

def jalankan_semua_automasi(data_teks, kredensial_ganjil, kredensial_genap, nama_perawat_ganjil, nama_perawat_genap): 
    baris_data = [b.strip() for b in data_teks.strip().split('\n') if b.strip()]
    if not baris_data:
        return
 
    maxWindow = min(len(baris_data), 3)
    
    with ThreadPoolExecutor(max_workers=maxWindow) as executor:  
        executor.map(
            lambda data: proses_satu_pasien(
                data, kredensial_ganjil, kredensial_genap, nama_perawat_ganjil, nama_perawat_genap
            ), 
            baris_data
        ) 
    
    root.after(0, lambda: btn_mulai.config(state="normal"))

def routine():  
    selected_nama = combo_akun.get().strip()     
    selected_nama_genap = combo_akun2.get().strip()    
    if not selected_nama or selected_nama not in DAFTAR_AKUN:
        messagebox.showwarning("Peringatan", "Silakan pilih akun petugas untuk Ruang GANJIL terlebih dahulu!")
        return   
    if not selected_nama_genap or selected_nama_genap not in DAFTAR_AKUN:
        messagebox.showwarning("Peringatan", "Silakan pilih akun petugas untuk Ruang GENAP terlebih dahulu!")
        return

    kredensial_ganjil = DAFTAR_AKUN[selected_nama]
    kredensial_genap = DAFTAR_AKUN[selected_nama_genap]

    try:
        btn_mulai.config(state="disabled")
        root.update_idletasks()
    
        input_text = input_vitalSign.get("1.0", END).strip()
        if not input_text:
            messagebox.showwarning("Warning", "Textarea masih kosong!")
            btn_mulai.config(state="normal")
            return
         
        defaults = [None, None, None, None, '97', '0', '36', '20', '1']
        processed_lines = [] 

        for line in input_text.splitlines():
            if not line.strip(): 
                continue 
            parts = line.split('-')
            complete_parts = [parts[i].strip() if i < len(parts) and parts[i].strip() != '' and parts[i].strip() != 'None' else defaults[i] for i in range(9)]
            processed_lines.append("-".join(str(p) for p in complete_parts)) 

        final_output = "\n".join(processed_lines)
        input_vitalSign.delete("1.0", END) 
        input_vitalSign.insert("1.0", final_output)
        
        today_str = datetime.now().strftime("%Y%m%d") 
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        }
        
        success_count = 0
        for line in processed_lines:
            parts = line.split('-')
            room_name = parts[0]
            if not room_name:
                continue
        
            vital_data = {
                "sistole": parts[1] if parts[1] != 'None' else None,
                "diastole": parts[2] if parts[2] != 'None' else None,
                "nadi": parts[3] if parts[3] != 'None' else None,
                "spo2": parts[4] if parts[4] != 'None' else None,
                "status_oks": parts[5],
                "suhu": parts[6] if parts[6] != 'None' else None,
                "respirasi": parts[7] if parts[7] != 'None' else None,
                "kesadaran": parts[8]
            }
            payload = {
                "vital_signs": vital_data
            }
            patch_url = f"{SUPABASE_URL}?room=eq.{room_name}&created_at=eq.{today_str}"
            response = requests.patch(patch_url, headers=headers, json=payload, timeout=10)

            if response.status_code in [200, 204]:
                success_count += 1
        
        messagebox.showinfo("Berhasil", f"Berhasil memformat dan menyimpan {success_count} data ke Supabase!")
        
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan: {e}") 
        btn_mulai.config(state="normal") 
        return # Tambahkan return agar thread tidak jalan jika error di tengah
 
    data_teks_baru = input_vitalSign.get("1.0", END)
     
    t = threading.Thread(
        target=jalankan_semua_automasi, 
        args=(data_teks_baru, kredensial_ganjil, kredensial_genap, selected_nama, selected_nama_genap)
    )
    t.start()
   
def fetchRoomFromDatabase():     
    btn_fetch.config(state=DISABLED)
    root.update_idletasks()
        
    try:
        today_str = datetime.now().strftime("%Y%m%d")  
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        }  
        params = {
            "select": "room,vital_signs",
            "created_at": f"eq.{today_str}",
            "order": "room.asc",
        } 
        response = requests.get(SUPABASE_URL, headers=headers, params=params, timeout=10) 
        if response.status_code == 200:
            data = response.json() 
            input_vitalSign.delete("1.0", END)
            
            if not data:
                input_vitalSign.insert(
                    END, f"Belum ada data ruangan untuk hari ini ({today_str})"
                )
                return  
            
            formatted_lines = []
            for item in data:
                room_name = item.get("room", "")
                vital = item.get("vital_signs") 
                if vital: 
                    sistole = vital.get("sistole", "None")
                    diastole = vital.get("diastole", "None")
                    nadi = vital.get("nadi", "None")
                    spo2 = vital.get("spo2", "None")
                    status_oksigen = vital.get("status_oks", "0")
                    suhu = vital.get("suhu", "None")
                    rr = vital.get("respirasi", "None")
                    kesadaran = vital.get("kesadaran", "1")
                     
                    line = f"{room_name}-{sistole}-{diastole}-{nadi}-{spo2}-{status_oksigen}-{suhu}-{rr}-{kesadaran}"
                else: 
                    line = room_name 
                formatted_lines.append(line) 
            final_output = "\n".join(formatted_lines)
            input_vitalSign.insert(END, final_output) 
        else:
            input_vitalSign.delete("1.0", END)
            input_vitalSign.insert(END, f"Gagal mengambil data! (Error Code: {response.status_code})" ) 
    except Exception as e:
        input_vitalSign.delete("1.0", END)
        input_vitalSign.insert(END, f"Error Koneksi: {e}") 
    finally:
        btn_fetch.config(state='normal')

def check_login():
    password = "asdasd"   
    if entry_password.get() == password:
        login.destroy()  
        main()   
    else: 
        entry_password.delete(0, END)

def check_password_length(*args):
    if len(password_var.get()) == 6:
        check_login() 

def main():
    global selected_nama, root, combo_akun, combo_akun2, input_vitalSign, btn_fetch, btn_mulai 
  
    root = Tk() 
    root.title("EMR automation")   
    root.geometry("+50+50")
    root.after(3600000, root.destroy)
    root.attributes('-topmost', True) 
    ff = 'courier new'
    fs = '10' 
 
    fieldset_new = LabelFrame(root, text=" New Patient ", padx=5, pady=5)
    fieldset_new.grid(row=0, column=0, padx=5, pady=5) 
  
    row1 = ttk.Frame(fieldset_new)
    row1.pack(fill='x', side=TOP, anchor='w') 
    pindahan_INPUT = Entry(row1, width='4') 
    pindahan_INPUT.pack(side=LEFT, padx='1', pady='2')   
    mr_INPUT = Entry(row1, width='8') 
    mr_INPUT.pack(side=LEFT, padx='1', pady='2')   
    nama_INPUT = Entry(row1, width='12') 
    nama_INPUT.pack(side=LEFT, padx='1', pady='2')
    usia_INPUT = Entry(row1, width='4') 
    usia_INPUT.pack(side=LEFT, padx='1') 
    
    row2 = ttk.Frame(fieldset_new)
    row2.pack(fill='x', side=TOP, anchor='w') 
    diagnosa_INPUT = Entry(row2, width='30') 
    diagnosa_INPUT.pack(side=LEFT, padx='1')
    
    row3 = ttk.Frame(fieldset_new)
    row3.pack(fill='x', side=TOP, anchor='w') 
    keluhan_INPUT = Entry(row3, width='30') 
    keluhan_INPUT.pack(side=LEFT, padx='1')
    
    row4 = ttk.Frame(fieldset_new)
    row4.pack(fill='x', side=TOP, anchor='w') 
    rps_INPUT = Entry(row4, width='30') 
    rps_INPUT.pack(side=LEFT, padx='1')
    
    row5 = ttk.Frame(fieldset_new)
    row5.pack(fill='x', side=TOP, anchor='w') 
    rpd_INPUT = Entry(row5, width='30') 
    rpd_INPUT.pack(side=LEFT, padx='1') 
    
    row6 = ttk.Frame(fieldset_new)
    row6.pack(fill='x', side=TOP, anchor='w')  
    sistole_INPUT = Entry(row6, width='5') 
    sistole_INPUT.pack(side=LEFT, padx='1')  
    diastole_INPUT = Entry(row6, width='5') 
    diastole_INPUT.pack(side=LEFT, padx='1')  
    nadi_INPUT = Entry(row6, width='4') 
    nadi_INPUT.pack(side=LEFT, padx='1')  
    suhu_INPUT = Entry(row6, width='4') 
    suhu_INPUT.pack(side=LEFT, padx='1')  
    rr_INPUT = Entry(row6, width='4') 
    rr_INPUT.pack(side=LEFT, padx='1')  
    spo2_INPUT = Entry(row6, width='4') 
    spo2_INPUT.pack(side=LEFT, padx='1')
    
    row7 = ttk.Frame(fieldset_new)
    row7.pack(fill='x', side=TOP, anchor='w')   
    diit_INPUT = Entry(row7, width=5) 
    diit_INPUT.pack(side=LEFT, padx='1') 
    alergi_INPUT = Entry(row7, width=24) 
    alergi_INPUT.pack(side=LEFT, padx='1')  
    
    row8 = ttk.Frame(fieldset_new)
    row8.pack(fill='x', side=TOP, anchor='w')  
    tindakan_INPUT = Entry(row8, width=30) 
    tindakan_INPUT.pack(side=LEFT, padx='1')  
    
    row9 = ttk.Frame(fieldset_new)
    row9.pack(fill='x', side=TOP, anchor='w') 
    dr_INPUT = Text(row9, width=30, height=2)
    dr_INPUT.pack(side=LEFT, padx='1') 
    
    row10 = ttk.Frame(fieldset_new)
    row10.pack(fill='x', side=TOP, anchor='w') 
    terapi_INPUT = Text(row10, width=30, height=5)
    terapi_INPUT.pack(side=LEFT, padx='1')   
     
    row11 = ttk.Frame(fieldset_new)
    row11.pack(fill='x', side=TOP, anchor='w')  
    bersihanJalanNapas_VAR = BooleanVar()  
    bersihanJalanNapas = Checkbutton(row11, text="Bersihan Jalan Napas", variable=bersihanJalanNapas_VAR)
    bersihanJalanNapas.pack(side=LEFT, padx='1') 
    
    row12 = ttk.Frame(fieldset_new)
    row12.pack(fill='x', side=TOP, anchor='w')  
    diare_VAR = BooleanVar()  
    diare = Checkbutton(row12, text="Diare", variable=diare_VAR)
    diare.pack(side=LEFT, padx='1') 
    
    row13 = ttk.Frame(fieldset_new)
    row13.pack(fill='x', side=TOP, anchor='w') 
    hipertermia_VAR = BooleanVar()  
    hipertermia = Checkbutton(row13, text="Hipertermia", variable=hipertermia_VAR)
    hipertermia.pack(side=LEFT, padx='1')
    
    row14 = ttk.Frame(fieldset_new)
    row14.pack(fill='x', side=TOP, anchor='w')
    hipervolemia_VAR = BooleanVar()  
    hipervolemia = Checkbutton(row14, text="Hipervolemia", variable=hipervolemia_VAR)
    hipervolemia.pack(side=LEFT, padx='1')            
    
    row15 = ttk.Frame(fieldset_new)
    row15.pack(fill='x', side=TOP, anchor='w')
    ketidakstabilanGD_VAR = BooleanVar()   
    ketidakstabilanGD = Checkbutton(row15, text="Ketidakstabilan GD", variable=ketidakstabilanGD_VAR)
    ketidakstabilanGD.pack(side=LEFT, padx='1') 
    
    row16 = ttk.Frame(fieldset_new)
    row16.pack(fill='x', side=TOP, anchor='w')
    nausea_VAR = BooleanVar() 
    nausea = Checkbutton(row16, text="Nausea", variable=nausea_VAR)
    nausea.pack(side=LEFT, padx='1')
    
    row17 = ttk.Frame(fieldset_new)
    row17.pack(fill='x', side=TOP, anchor='w')
    nyeriAkut_VAR = BooleanVar()
    nyeriAkut = Checkbutton(row17, text="Nyeri Akut", variable=nyeriAkut_VAR)
    nyeriAkut.pack(side=LEFT, padx='1')
    
    row18 = ttk.Frame(fieldset_new)
    row18.pack(fill='x', side=TOP, anchor='w')
    penurunanCurahJantung_VAR = BooleanVar()
    penurunanCurahJantung = Checkbutton(row18, text="Penurunan Curah Jantung", variable=penurunanCurahJantung_VAR)
    penurunanCurahJantung.pack(side=LEFT, padx='1')
    
    row19 = ttk.Frame(fieldset_new)
    row19.pack(fill='x', side=TOP, anchor='w')
    penurunanKapasitasAdaptif_VAR = BooleanVar()
    penurunanKapasitasAdaptif = Checkbutton(row19, text="Penurunan Kapasitas Adaptif", variable=penurunanKapasitasAdaptif_VAR)
    penurunanKapasitasAdaptif.pack(side=LEFT, padx='1') 
    
    row20 = ttk.Frame(fieldset_new)
    row20.pack(fill='x', side=TOP, anchor='w')
    polaNapas_VAR = BooleanVar()
    polaNapas = Checkbutton(row20, text="Pola Napas", variable=polaNapas_VAR)
    polaNapas.pack(side=LEFT, padx='1')
    
    row21 = ttk.Frame(fieldset_new)
    row21.pack(fill='x', side=TOP, anchor='w')
    resikoInfeksi_VAR = BooleanVar()
    resikoInfeksi = Checkbutton(row21, text="Resiko Infeksi", variable=resikoInfeksi_VAR)
    resikoInfeksi.pack(side=LEFT, padx='1')
    
    row22 = ttk.Frame(fieldset_new)
    row22.pack(fill='x', side=TOP, anchor='w')
    resikoJatuh_VAR = BooleanVar() 
    resikoJatuh = Checkbutton(row22, text="Resiko Jatuh", variable=resikoJatuh_VAR)
    resikoJatuh.pack(side=LEFT, padx='1')
    
    # row24 = ttk.Frame(fieldset_new)
    # row24.pack(fill='x', side=TOP, anchor='w')
    # scan_BT = Button(row24, text="scan-i", command=lambda: scan('i'))
    # scan_BT.pack(side=LEFT, padx='1')  
    # scan_transfer_BT = Button(row24, text="scan-t", command=lambda: scan('t'))
    # scan_transfer_BT.pack(side=LEFT, padx='1')
    
    # row25 = ttk.Frame(fieldset_new)
    # row25.pack(fill='x', side=TOP, anchor='w')
    # auto_dewasa_BT = Button(row25, text="auto-d", command=lambda: automate('d')) 
    # auto_dewasa_BT.pack(side=LEFT, padx='1')
    # auto_geriatri_BT = Button(row25, text="auto-g", command=lambda: automate('g')) 
    # auto_geriatri_BT.pack(side=LEFT, padx='1')
    # asesmen_dewasa_BT = Button(row25, text="akrid", command=lambda: partial_askep('d')) 
    # asesmen_dewasa_BT.pack(side=LEFT, padx='1')
    # asesmen_geriatri_BT = Button(row25, text="akrig", command=lambda: partial_askep('g')) 
    # asesmen_geriatri_BT.pack(side=LEFT, padx='1')

    # =============================================================================================== #
 
    fieldset_routine = LabelFrame(root, text=" Routine ", padx=5, pady=5)
    fieldset_routine.grid(row=0, column=1, sticky="n", padx=5, pady=5)  

    combo_akun = ttk.Combobox(fieldset_routine, values=list(DAFTAR_AKUN.keys()), state="readonly")
    combo_akun.grid(row=0, column=0, sticky="w") 
    
    combo_akun2 = ttk.Combobox(fieldset_routine, values=list(DAFTAR_AKUN.keys()), state="readonly")
    combo_akun2.grid(row=1, column=0, sticky="w") 

    input_vitalSign = Text(fieldset_routine, height=10, width=35, font=('Courier New', '10'))
    input_vitalSign.grid(row=2, column=0, sticky="w") 

    frame_btn = Frame(fieldset_routine)
    frame_btn.grid(row=3, column=0, sticky="w") 
    btn_fetch = Button(frame_btn, text="fetch", command=fetchRoomFromDatabase)
    btn_fetch.pack(side=LEFT, padx='1')      
    btn_mulai = Button(frame_btn, text="routine", command=routine)
    btn_mulai.pack(side=LEFT, padx='1')  

    root.mainloop()
 
login = Tk()  
password_var = StringVar() 
entry_password = Entry(login, textvariable=password_var, show="*")
entry_password.pack(padx=5, pady=5)
entry_password.focus() 
password_var.trace_add("write", check_password_length)
login.mainloop()
 