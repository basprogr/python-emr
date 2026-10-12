ini script ku :

SUPABASE_URL = "https://qjwmhtnfowkmwoflwhzy.supabase.co/rest/v1/logbook" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFqd21odG5mb3drbXdvZmx3aHp5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY5NjAwMTIsImV4cCI6MjEwMjUzNjAxMn0.ERWHxYn3GJJKHXJaJaZ2vnypcEM0DF8QE4DR_mjF-3s"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}
 
def proses_satu_pasien(data_pasien): 
    pecah = data_pasien.split('-')
    if len(pecah) < 8:
        print(f"Format salah untuk data: {data_pasien}")
        return 
    
    nama_ruang   = pecah[0].strip()
    # Tanda vital tidak disimpan di sini karena ditangani oleh fungsi sync/save terpisah,
    # tapi kita ambil untuk keperluan parsing baris jika dibutuhkan.
    
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
                nama_pasien = nama_pasien_elem.text.strip()
            except Exception as e:
                print(f"Gagal mengambil identitas pasien: {e}")

            try:
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
                print(f"Gagal mengambil diagnosa: {e}")

            print(f"Nama Pasien    : {nama_pasien}")
            print(f"No RM          : {no_rm}")
            print(f"Diagnosa Medis : {diagnosa_medis}") 
 
            # Push data Identitas Pasien ke Supabase
            payload = {
                "room": nama_ruang,
                "patient_name": nama_pasien,
                "no_rm": no_rm,
                "diagnosa_medis": diagnosa_medis,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            try:
                response = requests.post(SUPABASE_URL, json=payload, headers=HEADERS)
                if response.status_code in [200, 201]:
                    print(f"Berhasil menyimpan data identitas pasien {nama_pasien} ke database!")
                else:
                    print(f"Gagal menyimpan ke database. Status: {response.status_code}, Respon: {response.text}")
            except Exception as req_err:
                print(f"Terjadi kesalahan koneksi: {req_err}")
 
    except Exception as e:
        print(f"Error pada ruang {nama_ruang}: {e}")
    finally: 
        driver.quit() # Diaktifkan kembali agar tidak meninggalkan sisa proses Chrome terbuka di background

def save_formatted_to_database():
    btn_save.config(state="disabled")
    root.update_idletasks()

    try:
        input_text = input_vitalSign.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk disimpan!")
            btn_save.config(state="normal")
            return 

        defaults = [None, None, None, None, '97', '0', '36', '20', '1']
        processed_lines = []  
        for line in input_text.splitlines():
            if not line.strip(): 
                continue 
            parts = line.split('-')
            complete_parts = [parts[i].strip() if i < len(parts) and parts[i].strip() and parts[i].strip() != 'None' else defaults[i] for i in range(9)]
            processed_lines.append("-".join(str(p) for p in complete_parts)) 
             
        final_output = "\n".join(processed_lines)
        input_vitalSign.delete("1.0", tk.END) 
        input_vitalSign.insert("1.0", final_output)

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

            # Update ke Supabase berdasarkan room (menggunakan filter rlike/eq)
            patch_url = f"{SUPABASE_URL}?room=eq.{room_name}&order=created_at.desc&limit=1"
            response = requests.patch(patch_url, headers=HEADERS, json=payload, timeout=10)
            
            if response.status_code in [200, 204]:
                success_count += 1

        messagebox.showinfo("Berhasil", f"Berhasil memperbarui {success_count} data tanda vital di Supabase!")

    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan: {e}")
    finally:
        btn_save.config(state="normal")

def jalankan_semua_automasi(data_teks):
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

root = Tk()  
input_vitalSign = Text(root, height=10, width=50)
input_vitalSign.pack(padx=2, pady=2) 
btn_mulai = Button(root, text="routine", command=routine)
btn_mulai.pack(side=tk.LEFT, padx='1') 
btn_save = Button(root, text="sync", command=save_formatted_to_database)  
btn_save.pack(side=tk.LEFT, padx='1') 
root.mainloop()

dan ini table logbook milikku :

## Table `logbook`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary Identity |
| `room` | `varchar` |  |
| `patient_name` | `varchar` |  Nullable |
| `tasks` | `jsonb` |  Nullable |
| `therapies` | `jsonb` |  Nullable |
| `created_at` | `varchar` |  |
| `vital_signs` | `jsonb` |  Nullable |
| `no_rm` | `varchar` |  Nullable |
| `diagnosa_medis` | `varchar` |  Nullable |
  

  entah kenapa fungsi def proses_satu_pasien(data_pasien) tidak berjalan dengan baik
