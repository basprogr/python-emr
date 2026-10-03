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
    # chrome_options.add_argument("--headless") 
    
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
                    text_s = text_s.replace("pasien mengatakan", "").replace("px mengatakan", "").strip() 
                    driver.execute_script("CKEDITOR.instances.txtevaluasi_s.setData(arguments[0]);", text_s)
                    print("Berhasil memperbarui txtevaluasi_s via CKEditor API.")
                except Exception as e_s:
                    print(f"Gagal memproses txtevaluasi_s: {e_s}") 
            
                try:
                    time.sleep(0.5) 
                    text_o = driver.execute_script("return CKEDITOR.instances.txtevaluasi_o.getData();") or ""
 
                    if "Rr :" in text_o and " O2" in text_o:
                        idx_start = text_o.find("Rr :")
                        idx_end = text_o.find(" O2", idx_start) # Aman dari SpO2 karena mencari " O2" (ada spasi)
                        if idx_end != -1: 
                            sisa_belakang = text_o[idx_end + len(" O2"):]
                            text_o = text_o[:idx_start]
                    else:
                        sisa_belakang = ""
             
                    if status_oks > 0:
                        str_oksigen = f"dengan O2 {status_oks}lpm" # Sesuaikan format spasi lpm-nya
                    else:
                        str_oksigen = "tanpa O2"
             
                    new_vitals = f"Rr : {respirasi} x/menit\nSuhu : {suhu} °C\nNadi : {nadi} x/menit\nTD : {sistole}/{diastole} mmHg\nSpO2 : {spo2}% {str_oksigen}"
                    final_text = text_o.strip() + "\n" + new_vitals + sisa_belakang 
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
                        formatted_a_html = "<br>".join(formatted_a_list)
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
                        list_p_html = "<br>".join(list_p)
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
                        list_instruksi_html = "<br>".join(list_instruksi)
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
        
    messagebox.showinfo("Selesai", "Semua data TTV dan CPPT pasien berhasil diproses!")

def tombol_mulai_klik(): 
    data_teks = text_input.get("1.0", END)
    t = threading.Thread(target=jalankan_semua_automasi, args=(data_teks,))
    t.start()
 
root = Tk()
root.title("Auto Input TTV & CPPT Pasien - Mersi Hospital (Simultan)")
root.geometry("650x450")

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