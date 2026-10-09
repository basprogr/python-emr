import re
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from tkinter import *
import tkinter as tk  
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

SUPABASE_URL = "https://qjwmhtnfowkmwoflwhzy.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFqd21odG5mb3drbXdvZmx3aHp5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY5NjAwMTIsImV4cCI6MjEwMjUzNjAxMn0.ERWHxYn3GJJKHXJaJaZ2vnypcEM0DF8QE4DR_mjF-3s"
 
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
        driver.get(url1)   
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys("20224015") 
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("2024") 
        password_field.send_keys(Keys.RETURN) 
        time.sleep(2) 
 
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
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[-1]) 
        time.sleep(2)  
        current_url = driver.current_url
        
        if "asperawat_ranap" in current_url:
            new_url = current_url.replace("asperawat_ranap", "pemeriksaan_ttv")  
            driver.get(new_url) 
            
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

                    # Tunggu halaman selesai dimuat
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
            
                    # Beri jeda singkat untuk memastikan elemen AJAX termuat setelah diagnosis utama dicentang
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
                
            #  ==================================================

        print(f"Sukses memproses pasien di ruang: {nama_ruang}")

    except Exception as e:
        print(f"Error pada ruang {nama_ruang}: {e}")
    finally:
        # Opsional: Tutup driver otomatis setelah selesai agar tidak menumpuk
        # driver.quit()
        pass

def jalankan_semua_automasi(data_teks):
    # Menjalankan banyak baris data secara simultan menggunakan ThreadPool
    baris_data = [b.strip() for b in data_teks.strip().split('\n') if b.strip()]
    if not baris_data:
        messagebox.showerror("Error", "Data pasien masih kosong!")
        return
 
    maxWindow = min(len(baris_data), 10) 
    with ThreadPoolExecutor(max_workers=maxWindow) as executor:
        executor.map(proses_satu_pasien, baris_data) 

def routine(): 
    data_teks = input_vitalSign.get("1.0", END)
    t = threading.Thread(target=jalankan_semua_automasi, args=(data_teks,))
    t.start()
 
def fetchRoomFromDatabase():    
    btn_fetch.config(state=tk.DISABLED)
    root.update_idletasks()
        
    try:
        today_str = datetime.now().strftime("%Y%m%d") 
        url = f"{SUPABASE_URL}/rest/v1/logbook"

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        } 
        
        # Kita minta kolom 'room' DAN 'vital_signs' dari Supabase
        params = {
            "select": "room,vital_signs",
            "created_at": f"eq.{today_str}",
            "order": "room.asc",
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json() 
            input_vitalSign.delete("1.0", tk.END)
            
            if not data:
                input_vitalSign.insert(
                    tk.END, f"Belum ada data ruangan untuk hari ini ({today_str})"
                )
                return  
            
            formatted_lines = []
            for item in data:
                room_name = item.get("room", "")
                vital = item.get("vital_signs")
                
                # Jika vital_signs sudah ada isinya (tersimpan di DB)
                if vital:
                    # Ambil sesuai urutan defaults: sistole, diastole, nadi, spo2, status_oksigen, suhu, rr, kesadaran
                    sistole = vital.get("sistole", "None")
                    diastole = vital.get("diastole", "None")
                    nadi = vital.get("nadi", "None")
                    spo2 = vital.get("spo2", "None")
                    status_oksigen = vital.get("status_oksigen", "0")
                    suhu = vital.get("suhu", "None")
                    rr = vital.get("rr", "None")
                    kesadaran = vital.get("kesadaran", "1")
                    
                    # Gabungkan kembali dengan pemisah tanda hubung '-'
                    line = f"{room_name}-{sistole}-{diastole}-{nadi}-{spo2}-{status_oksigen}-{suhu}-{rr}-{kesadaran}"
                else:
                    # Kalau belum ada vital signs, tampilkan nama ruangnya saja
                    line = room_name
                    
                formatted_lines.append(line)
                
            final_output = "\n".join(formatted_lines)
            input_vitalSign.insert(tk.END, final_output)
            
        else:
            input_vitalSign.delete("1.0", tk.END)
            input_vitalSign.insert(
                tk.END, f"Gagal mengambil data! (Error Code: {response.status_code})"
            )
            
    except Exception as e:
        input_vitalSign.delete("1.0", tk.END)
        input_vitalSign.insert(tk.END, f"Error Koneksi: {e}")
        
    finally:
        btn_fetch.config(state='normal')
  
def save_formatted_to_database():
    btn_save.config(state="disabled")
    root.update_idletasks()

    try:
        input_text = input_vitalSign.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk disimpan!")
            btn_save.config(state="normal")
            return

        # --- LANGKAH 1: Jalankan proses formatting terlebih dahulu ---
        defaults = [None, None, None, None, '97', '0', '36', '20', '1']
        processed_lines = [] 
        
        for line in input_text.splitlines():
            if not line.strip(): 
                continue 
            parts = line.split('-')
            # Lengkapi bagian yang kurang dengan defaults
            complete_parts = [parts[i].strip() if i < len(parts) and parts[i].strip() != '' and parts[i].strip() != 'None' else defaults[i] for i in range(9)]
            processed_lines.append("-".join(str(p) for p in complete_parts)) 
            
        # Tampilkan kembali hasil format yang rapi ke widget Text
        final_output = "\n".join(processed_lines)
        input_vitalSign.delete("1.0", tk.END) 
        input_vitalSign.insert("1.0", final_output)

        # --- LANGKAH 2: Kirim data yang sudah diformat ke Supabase ---
        today_str = datetime.now().strftime("%Y%m%d")
        url = f"{SUPABASE_URL}/rest/v1/logbook"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        }

        success_count = 0
        for line in processed_lines.splitlines() if isinstance(processed_lines, str) else processed_lines:
            # Pecah kembali string yang sudah rapi
            parts = line.split('-')
            room_name = parts[0]
            
            if not room_name:
                continue

            # Bungkus ke JSONB vital_signs
            vital_data = {
                "sistole": parts[1] if parts[1] != 'None' else None,
                "diastole": parts[2] if parts[2] != 'None' else None,
                "nadi": parts[3] if parts[3] != 'None' else None,
                "spo2": parts[4] if parts[4] != 'None' else None,
                "status_oksigen": parts[5],
                "suhu": parts[6] if parts[6] != 'None' else None,
                "rr": parts[7] if parts[7] != 'None' else None,
                "kesadaran": parts[8]
            }

            payload = {
                "vital_signs": vital_data
            }

            # Update ke Supabase berdasarkan room & created_at
            patch_url = f"{url}?room=eq.{room_name}&created_at=eq.{today_str}"
            response = requests.patch(patch_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code in [200, 204]:
                success_count += 1

        messagebox.showinfo("Berhasil", f"Berhasil memformat dan menyimpan {success_count} data ke Supabase!")

    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan: {e}")
    finally:
        btn_save.config(state="normal")
  

root = Tk()  
input_vitalSign = Text(root, height=10, width=50)
input_vitalSign.pack(padx=2, pady=2) 

btn_fetch = Button(root, text="fetch", command=fetchRoomFromDatabase)
btn_fetch.pack(side=tk.LEFT, padx='1')   
btn_save = Button(root, text="Sync", command=save_formatted_to_database)
btn_save.pack(side=tk.LEFT, padx='1')
btn_mulai = Button(root, text="routine", command=routine)
btn_mulai.pack(side=tk.LEFT, padx='1') 
root.mainloop()