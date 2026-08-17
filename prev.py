import os
import pdfplumber  
import pyautogui
import pyperclip
import qrcode
import re  
import sys
import time 
import tkinter as tk    
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import messagebox, ttk 
from PIL import ImageTk, Image

from datetime import datetime, timedelta
 
currentDate = datetime.now().strftime("%Y-%m-%d")
yesterday = datetime.now() - timedelta(days=1)
previousDate = yesterday.strftime("%Y-%m-%d") 
currentHour = datetime.now().hour  
keluhanUtama = ''
diagnosaMedis = ''
diagnosaKeperawatan = ''

def notify(msg): 
    if not messagebox.askokcancel("Notifikasi", msg):
        sys.exit()  
  
def checkPassword(*args):
    password_set = "asdasd"
    current_input = password_var.get()
 
    if len(current_input) == 6:
        if current_input == password_set:
            root.destroy()
            main()
        else:
            pass
 
def main():   
    def scan(opt):      
        global keluhanUtama
        global diagnosaMedis
        file_options = {
            'i': "print_asperawat_gd.pdf",
            't': "print_transfer.pdf"
        } 
        filename = file_options.get(opt) 
        
        # Jaga-jaga jika opt tidak valid
        if not filename:
            messagebox.showwarning("Peringatan", f"Opsi '{opt}' tidak dikenal.")
            return

        pdf_path = str(Path.home() / "Downloads" / filename)
        
        # Inisialisasi variabel penampung string agar aman dari NameError di akhir code
        keluhanUtama = ""
        diagnosaMedis = ""
        usia_STRING = 0

        # 1. PROSES SCANNING (Cukup buka PDF 1 kali)
        try: 
            with pdfplumber.open(pdf_path) as pdf:
                text_biasa = ""
                text_tabel = ""
                
                # Ambil teks biasa dan tabel sekaligus per halaman
                for page in pdf.pages: 
                    text_biasa += (page.extract_text() or "") + "\n"
                    
                    tables = page.extract_tables()
                    if tables:
                        for t in tables:
                            for baris in t:
                                bersih_baris = [str(elemen) for elemen in baris if elemen not in [None, ""]]
                                text_tabel += " ".join(bersih_baris) + "\n"
                        text_tabel += "\n"

            # --- Scan Identitas Berbasis Teks Biasa ---
            if opt == 'i': 
                pindahan_INPUT.delete(0, tk.END) 
                pindahan_INPUT.insert(0, 'IGD')  
            
            mr = re.search(r'\s(\d{8})\s', text_biasa)
            if mr: 
                mr_INPUT.delete(0, tk.END) 
                mr_INPUT.insert(0, mr.group(1))  
                
            prefixes = ['tn', 'ny', 'sdr', 'sdri', 'an']
            pattern = r'\b(?:' + '|'.join(prefixes) + r')\.?\s+([^\s(]+(?:\s+[^\s(]+)*)' 
            match = re.search(pattern, text_biasa, re.IGNORECASE)
            if match:
                nama_INPUT.delete(0, tk.END)
                nama_INPUT.insert(0, match.group(1).strip()) 
                
            if usia_match := re.search(r"\((\d+)\s+th", text_biasa):
                usia_INPUT.delete(0, tk.END)
                usia_INPUT.insert(0, usia_match.group(1))
                usia_STRING = int(usia_match.group(1)) # Konversi di sini agar aman

            # --- Scan Berbasis Struktur Tabel ---
            if opt == 'i':   
                if keluhan := re.search(r"Keluhan Utama\s*(.*?)\s*Riwayat Penyakit", text_tabel, re.DOTALL):
                    keluhanUtama = " ".join(keluhan.group(1).split()) 
                    keluhan_INPUT.delete(0, tk.END) 
                    keluhan_INPUT.insert(0, keluhanUtama)

                rps = re.search(r"dahulu dan keluarga \)\s*(.*?)\s*Riwayat Pengobatan", text_tabel, re.DOTALL) 
                rps_INPUT.delete(0, tk.END) 
                if rps:   
                    rps_INPUT.insert(0, ' '.join(rps.group(1).split())) 
                else:
                    rps_INPUT.insert(0, keluhanUtama)  
                    
                rpd = re.search(r"konsumsi obat saat ini \)\s*(.*?)\s*Riwayat Kelahiran", text_tabel, re.DOTALL)
                rpd_INPUT.delete(0, tk.END) 
                if rpd:    
                    rpd_INPUT.insert(0, ' '.join(rpd.group(1).split())) 
                else: 
                    rpd_INPUT.insert(0, '-')  
                    
                diagnosa = re.search(r"DIAGNOSIS SESUAI ICD-10\s*(.*?)\s*Permasalahan Medis", text_tabel, re.DOTALL)
                if diagnosa:   
                    remove_numbering = re.sub(r"\d+\s*\.\s*", "", diagnosa.group(1))  
                    diagnosa_INPUT.delete(0, tk.END) 
                    diagnosaMedis = ' + '.join(remove_numbering.split('\n'))
                    diagnosa_INPUT.insert(0, diagnosaMedis)   

                sistole = re.search(r"Sistole\s*:\s*(.*?)\s*mmHg", text_tabel, re.IGNORECASE) 
                if sistole:   
                    sistole_INPUT.delete(0, tk.END) 
                    sistole_INPUT.insert(0, sistole.group(1).strip())  
                    
                diastole = re.search(r"Diastole\s*:\s*(.*?)\s*mmHg", text_tabel, re.IGNORECASE) 
                if diastole:   
                    diastole_INPUT.delete(0, tk.END) 
                    diastole_INPUT.insert(0, diastole.group(1).strip())  
                    
                nadi = re.search(r"nadi\s*(.*?)\s*x/menit", text_tabel, re.IGNORECASE)
                if nadi: 
                    nadi_INPUT.delete(0, tk.END) 
                    nadi_INPUT.insert(0, nadi.group(1).strip())  
                    
                suhu = re.search(r"(?i)suhu\s+(\S+)", text_tabel, re.IGNORECASE)
                if suhu: 
                    comaToPeriod = suhu.group(1).strip().replace(',', '.')
                    suhu_INPUT.delete(0, tk.END) 
                    suhu_INPUT.insert(0, comaToPeriod)  
                    
                rr_match = re.search(r"(?i)rr\s+(\d+)\s+x/menit", text_tabel, re.IGNORECASE)
                if rr_match: 
                    rr_INPUT.delete(0, tk.END) 
                    rr_INPUT.insert(0, rr_match.group(1).strip())  
                    
                spo2 = re.search(r"(?i)\bspo2\b\s*(\d+)%", text_tabel, re.IGNORECASE)
                if spo2: 
                    spo2_INPUT.delete(0, tk.END) 
                    spo2_INPUT.insert(0, spo2.group(1).strip())   
                    
                alergi = re.search(r'Alergi\s+([^\n]+)', text_tabel, re.IGNORECASE)  
                alergi_INPUT.delete(0, tk.END) 
                if alergi: 
                    if alergi.group(1).strip().lower() != "tidak": 
                        alergi_removeYa = alergi.group(1).replace('Ya : ', '')
                        alergi_INPUT.insert(0, alergi_removeYa.strip()) 
                    else:
                        alergi_INPUT.insert(0, '-') 
                                    
                dr = re.findall(r"dr\.\s+([\w\s]+?)\s+Sp\.", text_tabel, re.IGNORECASE | re.DOTALL)  
                dr_unique = set(match.strip().replace("\n", " ") for match in dr)  
                if dr: 
                    dr_INPUT.delete("1.0", tk.END)    
                    for doctor in dr_unique:
                        dr_INPUT.insert(tk.END, doctor + "\n") 
                        
                aji = re.search(r"\s*Satriyo\s*Aji\s*", text_tabel, re.IGNORECASE | re.DOTALL)  
                if aji:   
                    dr_INPUT.insert(tk.END, aji.group().strip().replace("\n", " ") + "\n") 
                    
                tx = re.search(r"PLAN OF\s*CARE\s*\)\s*(.*?)\s*Konsultasi Dokter", text_tabel, re.DOTALL)  
                if tx: 
                    lines = tx.group(1).strip().splitlines() 
                    # cleaned_lines = [f"- {re.sub(r'^[-\s]+', '', line)}" for line in lines if not re.search(r'mrs', line, re.IGNORECASE)] 
                    
                    cleaned_lines = [
                        f"- {subbed_line}"
                        for line in lines
                        if not re.search(r"mrs", line, re.IGNORECASE)
                        for subbed_line in [re.sub(r"^[-\s]+", "", line)]
                    ]
                    result = "\n".join(cleaned_lines) 
                    terapi_INPUT.delete("1.0", tk.END)
                    terapi_INPUT.insert(tk.END, result) 
                    
                report() 
                rx()
            
            else: # Jika opt == 't' (Transfer)
                allTextWithoutNewLine = text_tabel.replace('\n', '. ')   
    
                if keluhan := re.search(r"Keluhan Utama\s*(.*?)\s*Riwayat Penyakit", allTextWithoutNewLine):
                    keluhanUtama = " ".join(keluhan.group(1).split())
                    keluhan_INPUT.delete(0, tk.END) 
                    keluhan_INPUT.insert(0, keluhanUtama)
                
                rps_INPUT.delete(0, tk.END) 
                rps_INPUT.insert(0, '-') 
                rpd_INPUT.delete(0, tk.END) 
                rpd_INPUT.insert(0, '-') 
    
                if diagnosa := re.search(r"Diagnosa(.*?)Alasan Admisi", allTextWithoutNewLine):
                    diagnosaMedis = diagnosa.group(1).strip()
                    diagnosa_INPUT.delete(0, tk.END)
                    diagnosa_INPUT.insert(0, diagnosaMedis)
            
                sistole_match = re.search(r'Sistole\s*:\s*(\d+)\s*mmhg', text_tabel, flags=re.IGNORECASE)
                if sistole_match:   
                    sistole_INPUT.delete(0, tk.END) 
                    sistole_INPUT.insert(0, sistole_match.group(1)) 

                diastole_match = re.search(r'Diastole\s*:\s*(\d+)\s*mmhg', text_tabel, flags=re.IGNORECASE)
                if diastole_match:    
                    diastole_INPUT.delete(0, tk.END) 
                    diastole_INPUT.insert(0, diastole_match.group(1)) 
            
                nadi_match = re.search(r"(?i)nadi\s+(\d+)\s+x/menit", text_tabel, flags=re.IGNORECASE)
                if nadi_match: 
                    nadi_INPUT.delete(0, tk.END) 
                    nadi_INPUT.insert(0, nadi_match.group(1).strip()) 

                suhu_match = re.search(r"Suhu(.*?)GCS", text_tabel, flags=re.IGNORECASE)
                if suhu_match: 
                    comaToPeriod = suhu_match.group(1).strip().replace(',', '.')
                    suhu_INPUT.delete(0, tk.END) 
                    suhu_INPUT.insert(0, comaToPeriod) 

                rr_match = re.search(r"Pernafasan(.*?)Tensi", text_tabel, flags=re.IGNORECASE)
                if rr_match: 
                    rr_INPUT.delete(0, tk.END) 
                    rr_INPUT.insert(0, rr_match.group(1).strip()) 
            
                spo2_match = re.search(r"SPO2(.*?)Suhu", text_tabel, flags=re.IGNORECASE)
                if spo2_match: 
                    spo2_INPUT.delete(0, tk.END) 
                    spo2_INPUT.insert(0, spo2_match.group(1).strip())  
            
                alergi_match = re.search(r'Alergi\s+([^\n]+)', text_tabel, flags=re.IGNORECASE) 
                alergi_INPUT.delete(0, tk.END) 
                if alergi_match: 
                    if alergi_match.group(1).strip().lower() != "tidak": 
                        alergi_removeYa = alergi_match.group(1).replace('Ya, ', '').replace('Bahan Alergen :', '')
                        alergi_INPUT.insert(0, alergi_removeYa.strip()) 
                    else:
                        alergi_INPUT.insert(0, '-')
    
                diet_match = re.search(r"Diet(.*?)Makan", text_tabel)
                if diet_match: 
                    diit_INPUT.delete(0, tk.END) 
                    diit_INPUT.insert(0, diet_match.group(1).strip()) 

                inf_match = re.search(r"Infus \(dalam 24 jam\)(.*?)Obat Injeksi", allTextWithoutNewLine, re.DOTALL)
                inj_match = re.search(r"Obat Injeksi(.*?)Obat Oral", allTextWithoutNewLine, re.DOTALL)
                po_match = re.search(r"Obat Oral(.*?)Prosedur Medis", allTextWithoutNewLine, re.DOTALL)
    
                raw_data = [
                    inf_match.group(1) if inf_match else "",
                    inj_match.group(1) if inj_match else "",
                    po_match.group(1) if po_match else ""
                ]
                items = ",".join(filter(None, raw_data)).split(',') 
                res = "\n".join(f"- {item.strip()}" for item in items if item.strip()) 
                terapi_INPUT.delete("1.0", tk.END)
                terapi_INPUT.insert("1.0", res) 

        except Exception as e: 
            messagebox.showerror('Error Scanner', f"Terjadi kesalahan saat membaca file:\n{e}")
            return

        # 2. LOGIK AUTOPICK DIAGNOSE (Sekarang Aman dari NameError)
        keluhan_low = keluhanUtama.lower()
        diag_low = diagnosaMedis.lower()

        bersihanJalanNapas_VAR.set('batuk' in keluhan_low)
        diare_VAR.set('diare' in keluhan_low or 'bab cair' in keluhan_low)
        hipertermia_VAR.set('panas' in keluhan_low or 'demam' in keluhan_low)
        hipervolemia_VAR.set('ckd' in diag_low or 'bengkak' in keluhan_low)
        ketidakstabilanGD_VAR.set('dm' in diag_low)
        nausea_VAR.set('mual' in keluhan_low or 'muntah' in keluhan_low)
        nyeriAkut_VAR.set('nyeri' in keluhan_low or 'sakit' in keluhan_low)
        penurunanCurahJantung_VAR.set('nyeri dada' in keluhan_low or 'ngongsrong' in keluhan_low or 'ngos' in keluhan_low)
        penurunanKapasitasAdaptif_VAR.set('lemas' in keluhan_low and ('separuh' in keluhan_low or 'sebelah' in keluhan_low))
        polaNapas_VAR.set('sesak' in keluhan_low)
        resikoInfeksi_VAR.set('luka' in keluhan_low)
        resikoJatuh_VAR.set(usia_STRING > 60)
 
    def terima_transfer():   
        time.sleep(2)   
        pyautogui.write(rr_INPUT.get())
        pyautogui.press('tab')  
        pyautogui.write(sistole_INPUT.get())
        pyautogui.press('tab')  
        pyautogui.write(diastole_INPUT.get())
        pyautogui.press('tab')  
        pyautogui.write(nadi_INPUT.get())
        pyautogui.press('tab')  
        pyautogui.press('tab')  
        pyautogui.write(spo2_INPUT.get())
        pyautogui.press('tab')   
        pyautogui.write(suhu_INPUT.get())
        pyautogui.press('tab')  
        pyautogui.write('456')
        pyautogui.press('tab')  
        pyautogui.write('isokor')
        pyautogui.press('tab')  
        pyautogui.write('positif')   
        pyautogui.press('tab')  
        pyautogui.press('tab')  
        pyautogui.press('tab')   
        pyautogui.press('enter')
        messagebox.showinfo("?", "Terima transfer selesai") 
  
    def cppt(opt):   
        global diagnosaKeperawatan 

        cpptTime = ''
        if currentHour > 6 and currentHour < 14:
            cpptTime = currentDate + ' 12:00:00'
            handOverTime = currentDate + ' 14:00:00' 
        elif currentHour > 13 and currentHour < 21:
            cpptTime = currentDate + ' 19:00:00'
            handOverTime = currentDate + ' 21:00:00' 
        else:
            # Shif malam
            if currentHour > 20 and currentHour < 24 :
                # ganti ke tanggal berikutnya jika sebelum jam 24
                today = datetime.today()  
                next_day = today + timedelta(days=1) 
                tomorrow = next_day.strftime("%Y-%m-%d")

                cpptTime = tomorrow + ' 05:00:00'
                handOverTime = tomorrow + ' 07:00:00'  
            else : 
                # jika diatas jam 24, gunakan tanggal yang sama
                cpptTime = currentDate + ' 05:00:00'
                handOverTime = currentDate + ' 07:00:00' 
 
        pyautogui.write(cpptTime)
        pyautogui.press('tab')
        pyautogui.press('tab')
        
        if opt == 'c' or opt == 'copy': 
            # Subyektif

            pyautogui.hotkey('ctrl', 'a')  
            pyautogui.hotkey('ctrl', 'c')  
            s = pyperclip.paste()  
            s_res = re.sub(r'pasien mengatakan\s*', '', s, flags=re.IGNORECASE)   
            pyperclip.copy(s_res)  
            pyautogui.hotkey('ctrl', 'v')   

            pyautogui.press('tab') 

            pyautogui.hotkey('ctrl', 'a')  
            pyautogui.hotkey('ctrl', 'c')  
            o = pyperclip.paste()   
            o_res = re.sub(r"\s*Rr[\s\S]*?(?:\sO2|lpm)\b", "\nDELETED", o)  
            pyperclip.copy(o_res)  
            pyautogui.hotkey('ctrl', 'v')
 
            pyautogui.press('tab') 
            pyautogui.press('tab') 

            # Asesmen
 
            pyautogui.hotkey('ctrl', 'a')  
            pyautogui.hotkey('ctrl', 'c')  
            asesmen = pyperclip.paste()  

            diagnoseList = []
            implementasi = [] # sekalian bikin implementasi lah
            intervensi = [] # sekalian bikin intervensi dari asesmen yang didapat 
 
            if re.search(r'nyeri', asesmen, re.IGNORECASE):
                diagnoseList.append("nyeri akut") 
                implementasi.append('skala nyeri menurun')
                implementasi.append('grimace berkurang')
                intervensi.append("kaji keluhan nyeri") 
 
            if re.search(r'pola napas', asesmen, re.IGNORECASE):
                diagnoseList.append("pola napas tidak efektif")
                implementasi.append('frekuensi napas membaik')  
                implementasi.append('dipsnea menurun')  
                intervensi.append("pantau kepatenan jalan napas")  
                intervensi.append("monitor saturasi secara berkala") 

            if re.search(r'pola nafas', asesmen, re.IGNORECASE):
                diagnoseList.append("pola napas tidak efektif")  
                implementasi.append('frekuensi napas membaik')  
                implementasi.append('dipsnea menurun')   
                intervensi.append("pantau kepatenan jalan napas") 
                intervensi.append("monitor saturasi secara berkala") 

            if re.search(r'bersihan', asesmen, re.IGNORECASE):
                diagnoseList.append("bersihan jalan napas tidak efektif") 
                implementasi.append('produksi sputum menurun')   
                implementasi.append('wheezing/ronchi menurun')   
                intervensi.append("kaji keluhan batuk") 
                intervensi.append("monitor suara nafas") 

            if re.search(r'curah jantung', asesmen, re.IGNORECASE):
                diagnoseList.append("penurunan curah jantung")
                implementasi.append('status hemodinamik membaik')   
                intervensi.append("monitor status hemodinamik") 
            
            if re.search(r'hipertermi', asesmen, re.IGNORECASE):
                diagnoseList.append("hipertermia")
                implementasi.append('suhu tubuh dalam batas normal')   
                intervensi.append("monitor suhu tubuh bila perlu") 

            if re.search(r'hipervolemi', asesmen, re.IGNORECASE):
                diagnoseList.append("hipervolemia")
                implementasi.append('intake dan output seimbang')   
                implementasi.append('edema berkurang')   
                intervensi.append("batasi asupan cairan") 
                intervensi.append("monitor keseimbangan cairan") 

            if re.search(r'nausea', asesmen, re.IGNORECASE):
                diagnoseList.append("nausea")
                implementasi.append('keluhan mual berkurang')   
                intervensi.append("monitor keluhan muntah") 
                intervensi.append("pantau isyarat nonverbal ketidaknyamanan") 

            if re.search(r'adaptif', asesmen, re.IGNORECASE):
                diagnoseList.append("penurunan kapasitas adaptif intrakranial")
                implementasi.append('tingkat kesadaran membaik')   
                implementasi.append('irama napas membaik')   
                intervensi.append("monitor peningkatan tekanan darah") 
                intervensi.append("monitor irreguleritas irama napas") 
                intervensi.append("monitor penurunan tingkat kesadaran") 

            if re.search(r'ketidakstabilan', asesmen, re.IGNORECASE):
                diagnoseList.append("resiko ketidakstabilan kadar gula darah")
                implementasi.append('kadar gula darah dalam batas normal')   
                intervensi.append("pantau kadar gula darah secara berkala") 

            if re.search(r'infeksi', asesmen, re.IGNORECASE):
                diagnoseList.append("resiko infeksi")
                implementasi.append('tidak ada tanda infeksi') 
                intervensi.append("pantau tanda tanda infeksi") 

            if re.search(r'jatuh', asesmen, re.IGNORECASE):
                diagnoseList.append("resiko jatuh")
                implementasi.append('tidak ada kejadian jatuh')  
                intervensi.append("pasang kunci bed dan siderail") 
 
            # Convert diagnoseList to a numbered string with new lines
            asesmen_numbering = '\n'.join(f"{i+1}. {item}" for i, item in enumerate(diagnoseList))  
            diagnosaKeperawatan = asesmen_numbering
            pyperclip.copy(asesmen_numbering)  
            pyautogui.hotkey('ctrl', 'v')   
            pyautogui.press('tab') 
            pyautogui.press('tab') 

            # Planning

            pyautogui.hotkey('ctrl', 'a')  
            implementasi.insert(0, 'ttv dalam batas normal') 
            implementasi_numbering = '\n'.join(f"{i+1}. {item}" for i, item in enumerate(implementasi))  
            pyperclip.copy(implementasi_numbering)  
            pyautogui.hotkey('ctrl', 'v')   
            pyautogui.press('tab') 
            pyautogui.press('tab')  
              
            # Intervensi 

            intervensi.insert(0, "monitor tanda vital") # Add to beginning list
            intervensi.append("kolaborasi dengan tim medis") # Add to end of list 
            intervensi_numbering = '\n'.join(f"{i+1}. {item}" for i, item in enumerate(intervensi)) 
            pyperclip.copy(intervensi_numbering)  
            pyautogui.hotkey('ctrl', 'v')   

            pyautogui.press('tab') 
            pyautogui.press('right') 
            pyautogui.press('left') 
            pyautogui.press('tab')  
            pyautogui.write(handOverTime) 
            pyautogui.press('tab')  

            if currentHour > 6 and currentHour < 14:
                pyautogui.write('p')  
            elif currentHour > 13 and currentHour < 21:
                pyautogui.write('s')  
            else:
                pyautogui.write('m') 
            pyautogui.press('tab')   

        else: 
            # Subyektif 
            pyautogui.write(keluhan_INPUT.get()) 
            if nyeriAkut_VAR.get() :
                pyautogui.write(', nyeri hilang timbul, tidak menjalar')
            
            # Obyektif
            pyautogui.press('tab')
            pyautogui.write('akral hangat, kesadaran composmentis, GCS E4V5M6,') 
            if bersihanJalanNapas_VAR.get() :
                pyautogui.write(' ronchi (+)')

            pyautogui.press('enter')
            pyautogui.write('TD : ' + sistole_INPUT.get()  + '/' + diastole_INPUT.get()  + ' mmHg')
            pyautogui.press('enter')
            pyautogui.write('Nadi : ' + nadi_INPUT.get()  + ' x/menit')
            pyautogui.press('enter')
            pyautogui.write('Suhu : ' + suhu_INPUT.get() +' C')
            pyautogui.press('enter')
            pyautogui.write('Respirasi : ' + rr_INPUT.get() +'x')
            pyautogui.press('enter')
            pyautogui.write('SpO2 : ' + spo2_INPUT.get() +'%') 
            pyautogui.press('tab') 
            pyautogui.press('tab') 
            
            # DIAGNOSA 
            if bersihanJalanNapas_VAR.get() :
                pyautogui.write('- Bersihan jalan napas tidak efektif')
                pyautogui.press('enter') 
            if hipertermia_VAR.get() :
                pyautogui.write('- Hipertermia')
                pyautogui.press('enter') 
            if hipervolemia_VAR.get() :
                pyautogui.write('- Hipervolemia')
                pyautogui.press('enter') 
            if nausea_VAR.get() :
                pyautogui.write('- Nausea')
                pyautogui.press('enter') 
            if nyeriAkut_VAR.get() :
                pyautogui.write('- Nyeri akut')
                pyautogui.press('enter') 
            if penurunanCurahJantung_VAR.get() :
                pyautogui.write('- Penurunan Curah Jantung')
                pyautogui.press('enter') 
            if penurunanKapasitasAdaptif_VAR.get() :
                pyautogui.write('- Penurunan Kapasitas Adaptif Intrakranial')
                pyautogui.press('enter') 
            if polaNapas_VAR.get() :
                pyautogui.write('- Pola napas tidak efektif')
                pyautogui.press('enter') 
            if resikoInfeksi_VAR.get() :
                pyautogui.write('- Resiko infeksi')
                pyautogui.press('enter') 
            if resikoJatuh_VAR.get() :
                pyautogui.write('- Resiko jatuh')
                pyautogui.press('enter')  
            pyautogui.press('tab') 
            pyautogui.press('tab') 

            # IMPLEMENTASI

            if opt == 'p': 
                pyautogui.write('- ttv dalam batas normal')
                pyautogui.press('enter') 

                if bersihanJalanNapas_VAR.get() :
                    pyautogui.write('- produksi sputum menurun')
                    pyautogui.press('enter') 
                    pyautogui.write('- wheezing/ronchi menurun')
                    pyautogui.press('enter') 
                if hipertermia_VAR.get() :
                    pyautogui.write('- suhu tubuh dalam batas normal')
                    pyautogui.press('enter') 
                if hipervolemia_VAR.get() :
                    pyautogui.write('- intake dan output seimbang')
                    pyautogui.press('enter') 
                    pyautogui.write('- edema menurun')
                    pyautogui.press('enter') 
                if nausea_VAR.get() :
                    pyautogui.write('- Keluhan mual menurun')
                    pyautogui.press('enter') 
                if nyeriAkut_VAR.get() :
                    pyautogui.write('- skala nyeri menurun')
                    pyautogui.press('enter') 
                    pyautogui.write('- grimace berkurang')
                    pyautogui.press('enter') 
                if penurunanCurahJantung_VAR.get() :
                    pyautogui.write('- status hemodinamik membaik')
                    pyautogui.press('enter')  
                if penurunanKapasitasAdaptif_VAR.get() :
                    pyautogui.write('- tingkat kesadaran membaik')
                    pyautogui.press('enter')  
                    pyautogui.write('- irama napas reguler')
                    pyautogui.press('enter')  
                if polaNapas_VAR.get() :
                    pyautogui.write('- frekuensi napas membaik')
                    pyautogui.press('enter') 
                    pyautogui.write('- dispnea menurun')
                    pyautogui.press('enter') 
                if resikoInfeksi_VAR.get() :
                    pyautogui.write('- tidak ada tanda tanda infeksi')
                    pyautogui.press('enter') 
                if resikoJatuh_VAR.get() :
                    pyautogui.write('- tidak ada kejadian jatuh')
                    pyautogui.press('enter')  
            else: 
                lines = dr_INPUT.get("1.0", tk.END).strip().split("\n")  # Memecah teks menjadi daftar baris
                formatted_lines = [f"lapor dr. {line.strip()}" for line in lines]  # Menambahkan "lapor dr."
                res = "\n".join(formatted_lines)  # Menggabungkan kembali menjadi string 
                pyautogui.write(res)
            
            pyautogui.press('tab')
            pyautogui.press('tab')

            # INTERVENSI

            if opt == 'p': 
                pyautogui.write('- monitor ttv')
                pyautogui.press('enter') 
                if bersihanJalanNapas_VAR.get() :
                    pyautogui.write('- kaji keluhan batuk')
                    pyautogui.press('enter') 
                if hipertermia_VAR.get() :
                    pyautogui.write('- monitor suhu tubuh secara berkala')
                    pyautogui.press('enter') 
                if hipervolemia_VAR.get() :
                    pyautogui.write('- batasi asupan cairan')
                    pyautogui.press('enter') 
                    pyautogui.write('- monitor keseimbangan cairan')
                    pyautogui.press('enter') 
                if nausea_VAR.get() :
                    pyautogui.write('- monitor keluhan muntah')
                    pyautogui.press('enter') 
                if nyeriAkut_VAR.get() :
                    pyautogui.write('- kaji keluhan nyeri')
                    pyautogui.press('enter') 
                if penurunanCurahJantung_VAR.get() :
                    pyautogui.write('- monitor status hemodinamik')
                    pyautogui.press('enter')  
                if penurunanKapasitasAdaptif_VAR.get() :
                    pyautogui.write('- monitor peningkatan tekanan darah')
                    pyautogui.press('enter')  
                    pyautogui.write('- monitor irreguleritas irama napas')
                    pyautogui.press('enter')  
                    pyautogui.write('- monitor penurunan tingkat kesadaran')
                    pyautogui.press('enter')  
                if polaNapas_VAR.get() :
                    pyautogui.write('- pantau kepatenan jalan napas')
                    pyautogui.press('enter') 
                    pyautogui.write('- monitor saturasi secara berkala')
                    pyautogui.press('enter') 
                if resikoInfeksi_VAR.get() :
                    pyautogui.write('- pantau adanya tanda tanda infeksi')
                    pyautogui.press('enter') 
                if resikoJatuh_VAR.get() :
                    pyautogui.write('- pasang kunci bed dan siderail')
                    pyautogui.press('enter') 
                pyautogui.write('- kolaborasi dengan tim medis') 

                pyautogui.press('tab') 
                pyautogui.press('right') 
                pyautogui.press('left') 
                pyautogui.press('tab')  
                pyautogui.write(handOverTime) 
                pyautogui.press('tab')  

                if currentHour > 6 and currentHour < 14:
                    pyautogui.write('p')  
                elif currentHour > 13 and currentHour < 21:
                    pyautogui.write('s')  
                else:
                    pyautogui.write('m') 
                pyautogui.press('tab')   
    
            else:
                pyautogui.write('advis belum terhubung') 
                pyautogui.press('tab') 
                pyautogui.press('right')  
 
    def discharge():   
        pyautogui.write("KIE minum obat sesuai anjuran")
        pyautogui.press('enter') 
        pyautogui.write("KIE kontrol sesuai jadwal")
        pyautogui.press('tab')
        pyautogui.press('tab') 
        pyautogui.press('enter')  

    def akrid():     
        # -- anamnesis
        pyautogui.write(keluhan_INPUT.get()) 
        pyautogui.press('tab')
        pyautogui.write(rps_INPUT.get()) 
        pyautogui.press('tab')
        pyautogui.write(rpd_INPUT.get())  
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('tab')

        if alergi_INPUT.get() == '' or alergi_INPUT.get() == '-':
            pyautogui.press('right')
            pyautogui.press('left') 
            pyautogui.press('tab')
        else:
            pyautogui.press('right')
            pyautogui.press('tab')
            pyautogui.write(alergi_INPUT.get())

        # -- psiko
        pyautogui.press('tab') 
        pyautogui.press('space')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('space')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('space')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.write('tidak ada')

        # -- sosial
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.write('tidak ada')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.write('tidak ada')

        # -- ekonomi
        for i in range(11):
            pyautogui.press('tab')   
        pyautogui.press('right') 
        pyautogui.press('left') 
        
        # -- nilai budaya
        pyautogui.press('tab') 
        pyautogui.write('tidak ada') 
        pyautogui.press('tab') 
        pyautogui.write('tidak ada') 
        
        # -- ttv
        pyautogui.press('tab')   
        pyautogui.write(sistole_INPUT.get())   
        pyautogui.press('tab')   
        pyautogui.write(diastole_INPUT.get())   
        pyautogui.press('tab')   
        pyautogui.write(nadi_INPUT.get())   
        pyautogui.press('tab')   
        pyautogui.press('right')   
        pyautogui.press('left')   
        pyautogui.press('tab')   
        pyautogui.write(rr_INPUT.get()) 
        for i in range(4):   
            pyautogui.press('tab')    
        pyautogui.write(suhu_INPUT.get())   
        pyautogui.press('tab')   
        pyautogui.write(spo2_INPUT.get())   
        pyautogui.press('tab')   
        
        # -- B1
        pyautogui.press('tab') 
        pyautogui.press('space') 
        for i in range(9):
            pyautogui.press('tab')  
        pyautogui.press('space') 
        for i in range(6):
            pyautogui.press('tab')  
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('space') 
        for i in range(8):
            pyautogui.press('tab')  
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 

        # -- B2 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('left')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('left')  
        pyautogui.press('tab') 

        # -- B3 
        pyautogui.press('tab')
        pyautogui.write('E4V5M6') 
        pyautogui.press('tab')
        pyautogui.press('space')
        for i in range(14):
            pyautogui.press('tab') 
        pyautogui.press('space') 
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('space')
        for i in range(6): 
            pyautogui.press('tab') 
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        
        # -- B4 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab')  
        pyautogui.write('-+ 500') 
        pyautogui.press('tab') 
        pyautogui.write('kuning') 
        
        # -- B5
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab')  
        pyautogui.press('tab') 
        pyautogui.write('> 2x') 
        pyautogui.press('tab') 
        pyautogui.write('-+ 500 cc') 
        for i in range(5): 
            pyautogui.press('tab') 
        pyautogui.press('space') 
        for i in range(3): 
            pyautogui.press('tab') 
        pyautogui.write(diit_INPUT.get()) 
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        for i in range(7): 
            pyautogui.press('tab') 
        pyautogui.press('space') 
        pyautogui.press('tab')
        for i in range(4): 
            pyautogui.press('tab') 
        pyautogui.press('space')  
        for i in range(14): 
            pyautogui.press('tab') 
        pyautogui.press('right')
        pyautogui.press('left')  
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.write('kuning')  
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        
        # -- B6
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.write('5') 
        pyautogui.press('tab') 
        pyautogui.write('5') 
        pyautogui.press('tab') 
        pyautogui.write('5') 
        pyautogui.press('tab') 
        pyautogui.write('5')  
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('right') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  
        
        # -- endokrin 
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')   
        for i in range(6): 
            pyautogui.press('tab') 

        # -- asesmen nyeri 
        if nyeriAkut_VAR.get() :
            pyautogui.press('tab') 
            pyautogui.press('right') 
            pyautogui.press('tab') 
            pyautogui.press('enter')
            pyautogui.press('down') 
            pyautogui.press('down') 
            pyautogui.press('down') 
            pyautogui.press('enter') 
            pyautogui.press('tab') 
            pyautogui.press('right') 
            pyautogui.press('left') 
            pyautogui.press('tab') 
            pyautogui.press('right') 
            pyautogui.press('tab') 
            pyautogui.press('tab') 
            pyautogui.press('right') 
            pyautogui.press('left') 
            for i in range(5): 
                pyautogui.press('tab') 
            pyautogui.press('tab') 
        else:
            pyautogui.press('tab') 
            pyautogui.press('right') 
            pyautogui.press('left') 
            pyautogui.press('tab') 
     
        # -- nutrisi
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')

        # -- FUNGSIONAL INDEX
        for i in range(10): 
            pyautogui.press('tab')
        
        # -- MORSE FALL SCALE
        for i in range(2): 
            pyautogui.press('tab')
            pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right') 

        # -- DEKUBITUS 
        for i in range(5): 
            pyautogui.press('tab')
            pyautogui.press('right')
            pyautogui.press('right')
            pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('right')

        # -- RESIKO PENYAKIT MENULAR
        pyautogui.press('tab')
        pyautogui.press('right')
        
        # -- RESTRAIN
        for i in range(6):
            pyautogui.press('tab') 
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab') 

        # -- EWS
        pyautogui.press('tab') 
        pyautogui.write(rr_INPUT.get())  
        pyautogui.press('tab') 
        pyautogui.write(spo2_INPUT.get())  
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.write(suhu_INPUT.get()) 
        pyautogui.press('tab') 
        pyautogui.write(sistole_INPUT.get()) 
        pyautogui.press('tab') 
        pyautogui.write(nadi_INPUT.get())
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  

        # -- DISCARD PLANNING
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        for i in range(3):
            pyautogui.press('tab') 
            pyautogui.press('right')  
        for i in range(30):
            pyautogui.press('tab') 
        pyautogui.press('space')  
        for i in range(11):
            pyautogui.press('tab') 
        pyautogui.press('space')  
        for i in range(20):
            pyautogui.press('tab') 
        pyautogui.write('-')    
 
    def akrig():     
        # -- anamnesis
        pyautogui.write(keluhan_INPUT.get()) 
        pyautogui.press('tab')
        pyautogui.write(rps_INPUT.get()) 
        pyautogui.press('tab')
        pyautogui.write(rpd_INPUT.get())  
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('tab')

        if alergi_INPUT.get() == '' or alergi_INPUT.get() == '-':
            pyautogui.press('right')
            pyautogui.press('left') 
            pyautogui.press('tab')
        else:
            pyautogui.press('right')
            pyautogui.press('tab')
            pyautogui.write(alergi_INPUT.get())

        # -- psiko
        pyautogui.press('tab') 
        pyautogui.press('space')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('space')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('space')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.write('tidak ada')

        # -- sosial
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.write('tidak ada')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.write('tidak ada')

        # -- ekonomi
        for i in range(11):
            pyautogui.press('tab')   
        pyautogui.press('right') 
        pyautogui.press('left') 
        
        # -- nilai budaya
        pyautogui.press('tab') 
        pyautogui.write('tidak ada') 
        pyautogui.press('tab') 
        pyautogui.write('tidak ada') 
        
        # -- ttv
        pyautogui.press('tab')   
        pyautogui.write(sistole_INPUT.get())   
        pyautogui.press('tab')   
        pyautogui.write(diastole_INPUT.get())   
        pyautogui.press('tab')   
        pyautogui.write(nadi_INPUT.get())   
        pyautogui.press('tab')   
        pyautogui.press('right')   
        pyautogui.press('left')   
        pyautogui.press('tab')   
        pyautogui.write(rr_INPUT.get()) 
        for i in range(4):   
            pyautogui.press('tab')    
        pyautogui.write(suhu_INPUT.get())   
        pyautogui.press('tab')   
        pyautogui.write(spo2_INPUT.get())   
        pyautogui.press('tab')   
        
        # -- B1
        pyautogui.press('tab') 
        pyautogui.press('space') 
        for i in range(9):
            pyautogui.press('tab')  
        pyautogui.press('space') 
        for i in range(6):
            pyautogui.press('tab')  
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('space') 
        for i in range(8):
            pyautogui.press('tab')  
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 

        # -- B2 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('left')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('left')  
        pyautogui.press('tab') 

        # -- B3 
        pyautogui.press('tab')
        pyautogui.write('E4V5M6') 
        pyautogui.press('tab')
        pyautogui.press('space')
        for i in range(14):
            pyautogui.press('tab') 
        pyautogui.press('space') 
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('space')
        for i in range(6): 
            pyautogui.press('tab') 
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        
        # -- B4 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab')  
        pyautogui.write('-+ 500') 
        pyautogui.press('tab') 
        pyautogui.write('kuning') 
        
        # -- B5
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab')  
        pyautogui.press('tab') 
        pyautogui.write('> 2x') 
        pyautogui.press('tab') 
        pyautogui.write('-+ 500 cc') 
        for i in range(5): 
            pyautogui.press('tab') 
        pyautogui.press('space') 
        for i in range(3): 
            pyautogui.press('tab') 
        pyautogui.write(diit_INPUT.get()) 
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        for i in range(7): 
            pyautogui.press('tab') 
        pyautogui.press('space') 
        pyautogui.press('tab')
        for i in range(4): 
            pyautogui.press('tab') 
        pyautogui.press('space')  
        for i in range(14): 
            pyautogui.press('tab') 
        pyautogui.press('right')
        pyautogui.press('left')  
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.write('kuning')  
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left') 
        pyautogui.press('tab')
        
        # -- B6
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.write('5') 
        pyautogui.press('tab') 
        pyautogui.write('5') 
        pyautogui.press('tab') 
        pyautogui.write('5') 
        pyautogui.press('tab') 
        pyautogui.write('5')  
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('right') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  
        
        # -- endokrin 
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')  
        pyautogui.press('tab') 
        pyautogui.press('right')   
        for i in range(6): 
            pyautogui.press('tab') 
 
        # -- asesmen nyeri 
        if nyeriAkut_VAR.get() :
            pyautogui.press('tab') 
            pyautogui.press('right') 
            pyautogui.press('tab') 
            pyautogui.press('enter')
            pyautogui.press('down') 
            pyautogui.press('down') 
            pyautogui.press('down') 
            pyautogui.press('enter') 
            pyautogui.press('tab') 
            pyautogui.press('right') 
            pyautogui.press('left') 
            pyautogui.press('tab') 
            pyautogui.press('right') 
            pyautogui.press('tab') 
            pyautogui.press('tab') 
            pyautogui.press('right') 
            pyautogui.press('left') 
            for i in range(5): 
                pyautogui.press('tab') 
            pyautogui.press('tab') 
        else:
            pyautogui.press('tab') 
            pyautogui.press('right') 
            pyautogui.press('left') 
            pyautogui.press('tab') 

        # -- nutrisi
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')

        # -- FUNGSIONAL INDEX
        for i in range(10): 
            pyautogui.press('tab')

        # -- ONTARIO FALL SCALE
        for i in range(9): 
            pyautogui.press('tab')
            pyautogui.press('right')
        for i in range(2): 
            pyautogui.press('tab')
            pyautogui.press('right')
            pyautogui.press('left')

        # -- DEKUBITUS 
        for i in range(5): 
            pyautogui.press('tab')
            pyautogui.press('right')
            pyautogui.press('right')
            pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('right')

        # -- RESIKO PENYAKIT MENULAR
        pyautogui.press('tab')
        pyautogui.press('right')

        # -- FUNGSI KOGNITIF
        for i in range(10):
            pyautogui.press('tab')
            pyautogui.press('right')
            pyautogui.press('left')

        # -- PENGKAJIAN DEPRESI
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        for i in range(3):
            pyautogui.press('tab')
            pyautogui.press('right')
        for i in range(2):
            pyautogui.press('tab')
            pyautogui.press('right')
            pyautogui.press('left')
        for i in range(4):
            pyautogui.press('tab')
            pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('tab')
        pyautogui.press('right')
        pyautogui.press('left')
        for i in range(2):
            pyautogui.press('tab')
            pyautogui.press('right')

        # -- RESTRAIN
        for i in range(6):
            pyautogui.press('tab') 
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab') 
        pyautogui.press('tab') 
        pyautogui.press('right')
        pyautogui.press('left')
        pyautogui.press('tab') 

        # -- EWS
        pyautogui.press('tab') 
        pyautogui.write(rr_INPUT.get())  
        pyautogui.press('tab') 
        pyautogui.write(spo2_INPUT.get())  
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab') 
        pyautogui.write(suhu_INPUT.get()) 
        pyautogui.press('tab') 
        pyautogui.write(sistole_INPUT.get()) 
        pyautogui.press('tab') 
        pyautogui.write(nadi_INPUT.get())
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left')  

        # -- DISCARD PLANNING
        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        for i in range(3):
            pyautogui.press('tab') 
            pyautogui.press('right')  
        for i in range(30):
            pyautogui.press('tab') 
        pyautogui.press('space')  
        for i in range(11):
            pyautogui.press('tab') 
        pyautogui.press('space')  
        for i in range(20):
            pyautogui.press('tab') 
        pyautogui.write('-')    
 
    def report():   
        # reset preview field
        report_EN.delete("1.0", tk.END)

        h = datetime.now().hour
        sapaan = '-' 
        if h < 10 :
            sapaan = 'pagi'
        elif 10 <= h < 15 :
            sapaan = 'siang'
        elif 14 <= h < 19 :
            sapaan = 'sore'
        else :
            sapaan = 'malam'

        text = 'Selamat ' + sapaan +' dokter,\n'
        text += 'Melaporkan pasien baru pindahan dari '+ pindahan_INPUT.get() +',\n\n'
        text += '*a/n '+ nama_INPUT.get().upper() +' / '+ usia_INPUT.get() +'th*\n'
        text += 'dengan '+ diagnosa_INPUT.get() + '\n\n'
        text += 'Keluhan : '+ keluhan_INPUT.get() + '\n\n'
        text += "```GCS  : 456\n"
        text += 'TD   : '+ sistole_INPUT.get() +'/'+ diastole_INPUT.get() +' mmHg\n'
        text += 'Nadi : '+ nadi_INPUT.get() +' x/menit\n'
        text += 'Suhu : '+ suhu_INPUT.get() +' C\n'
        text += 'RR   : '+ rr_INPUT.get() +' x/menit\n'
        text += 'SpO2 : '+ spo2_INPUT.get() +"%```\n\n"
        text += "`Terapi`\n"
        text += terapi_INPUT.get("1.0", tk.END) + '\n\n' 

        if tindakan_INPUT.get() != '':
            text += "`Rencana Tindakan`\n"
            text += tindakan_INPUT.get() + '\n\n'

        text += 'Apakah ada advis tambahan dokter? \nTerimakasih ...'  
        
        report_EN.insert(tk.END, text)  

    def rx():   
        try:
            # Reset preview field
            rx_EN.delete("1.0", tk.END)

            h = datetime.now().hour
            sapaan = '-' 
            if 3 <= h < 10 :
                sapaan = 'pagi'
            elif 10 <= h < 15 :
                sapaan = 'siang'
            elif 14 <= h < 19 :
                sapaan = 'sore'
            else :
                sapaan = 'malam' 

            text = 'Selamat ' + sapaan +' dokter, RID minta tolong eresep nggih.\n\n'
            text += '```Nama :``` *' + nama_INPUT.get().upper() + '*\n'
            text += '```RM   :``` *' + mr_INPUT.get() + '*\n\n'

            # split kalimat per baris baru
            lines = terapi_INPUT.get("1.0", tk.END).splitlines() 

            for line in lines:
                # jika obat syrup
                if 'syr' in line:
                    text += line + ' (1)\n'
                else: 
                    # temukan aturan pakai
                    res = re.search(r'(\d+)x', line, re.IGNORECASE)
                    if res: 
                        total = int(res.group(1)) * 3
                        text += line + ' (' + str(total) + ')\n' 
                    else:
                        text += line + ' (3)\n'
                        
            text += '\nTerimakasih ...'
            
            rx_EN.insert(tk.END, text)
  
        except Exception as e: 
            messagebox.showinfo("Error", e)  
    
    def copy_report(): 
        t = report_EN.get("1.0", tk.END) 
        app.clipboard_clear() 
        app.clipboard_append(t)
    
    def copy_rx(): 
        t = rx_EN.get("1.0", tk.END) 
        app.clipboard_clear() 
        app.clipboard_append(t)

    # TAB 3 | Diagnose

    def reset(): 
        bersihanJalanNapas_VAR.set(False)  
        diare_VAR.set(False)  
        hipertermia_VAR.set(False)  
        hipervolemia_VAR.set(False)  
        ketidakstabilanGD_VAR.set(False)   
        nausea_VAR.set(False)   
        nyeriAkut_VAR.set(False)
        penurunanCurahJantung_VAR.set(False)
        penurunanKapasitasAdaptif_VAR.set(False)
        polaNapas_VAR.set(False)
        resikoInfeksi_VAR.set(False)
        resikoJatuh_VAR.set(False)

    def diagnose():
        # Kumpulan variabel dengan nama dan nilainya
        variables = [
            ("bersihanJalanNapas_VAR", bersihanJalanNapas_VAR.get()),
            ("diare_VAR", diare_VAR.get()),
            ("hipertermia_VAR", hipertermia_VAR.get()),
            ("hipervolemia_VAR", hipervolemia_VAR.get()),
            ("ketidakstabilanGD_VAR", ketidakstabilanGD_VAR.get()),
            ("nausea_VAR", nausea_VAR.get()),
            ("nyeriAkut_VAR", nyeriAkut_VAR.get()),
            ("penurunanCurahJantung_VAR", penurunanCurahJantung_VAR.get()),
            ("penurunanKapasitasAdaptif_VAR", penurunanKapasitasAdaptif_VAR.get()),
            ("polaNapas_VAR", polaNapas_VAR.get()),
            ("resikoInfeksi_VAR", resikoInfeksi_VAR.get()),
            ("resikoJatuh_VAR", resikoJatuh_VAR.get())
        ] 
        # Cari variabel terakhir yang bernilai True
        last_true = None
        for name, value in variables:
            if value:
                last_true = name
   
        for _ in range(5):
            pyautogui.press('tab')
        if bersihanJalanNapas_VAR.get():
                pyautogui.press('space')
                if last_true == 'bersihanJalanNapas_VAR' :
                    # implement()
                    return
        for _ in range(8):
            pyautogui.press('tab')
        if diare_VAR.get():
                pyautogui.press('space')    
                if last_true == 'diare_VAR' :
                    # implement()
                    return 
        for _ in range(32):
            pyautogui.press('tab')
        if hipertermia_VAR.get():
                pyautogui.press('space')   
                if last_true == 'hipertermia_VAR' :
                    # implement()
                    return  
        for _ in range(2):
            pyautogui.press('tab')
        if hipervolemia_VAR.get():
                pyautogui.press('space')  
                if last_true == 'hipervolemia_VAR' :
                    # implement()
                    return  
        for _ in range(24):
            pyautogui.press('tab')
        if ketidakstabilanGD_VAR.get():
                pyautogui.press('space')    
                if last_true == 'ketidakstabilanGD_VAR' :
                    # implement()
                    return
        for _ in range(10):
            pyautogui.press('tab')
        if nausea_VAR.get():
                pyautogui.press('space')    
                if last_true == 'nausea_VAR' :
                    # implement()
                    return
        for _ in range(2):
            pyautogui.press('tab')
        if nyeriAkut_VAR.get():
                pyautogui.press('space')    
                if last_true == 'nyeriAkut_VAR' :
                    # implement()
                    return
        for _ in range(6):
            pyautogui.press('tab')
        if penurunanCurahJantung_VAR.get():
                pyautogui.press('space')    
                if last_true == 'penurunanCurahJantung_VAR' :
                    # implement()
                    return
        for _ in range(2):
            pyautogui.press('tab')
        if penurunanKapasitasAdaptif_VAR.get():
                pyautogui.press('space')    
                if last_true == 'penurunanKapasitasAdaptif_VAR' :
                    # implement()
                    return
        for _ in range(8):
            pyautogui.press('tab')
        if polaNapas_VAR.get():
                pyautogui.press('space')    
                if last_true == 'polaNapas_VAR' :
                    # implement()
                    return
        for _ in range(28):
            pyautogui.press('tab')
        if resikoInfeksi_VAR.get():
                pyautogui.press('space')    
                if last_true == 'resikoInfeksi_VAR' :
                    # implement()
                    return
        for _ in range(4):
            pyautogui.press('tab')
        if resikoJatuh_VAR.get():
                pyautogui.press('space')   
                if last_true == 'resikoJatuh_VAR' :
                    # implement()
                    return 
        messagebox.showinfo('Notifikasi', "Diagnosa selesai. Lanjutkan implementasi?")

    def implement():  
        # PENYEBAB 
        if bersihanJalanNapas_VAR.get():
            for _ in range(12):
                pyautogui.press('tab')
            pyautogui.press('space')   
            pyautogui.press('tab') 
        if diare_VAR.get():
            for _ in range(9):
                pyautogui.press('tab')
            pyautogui.press('space')   
            for _ in range(4):
                pyautogui.press('tab')   
        if hipertermia_VAR.get():
            for _ in range(5):
                pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(3):
                pyautogui.press('tab')  
        if hipervolemia_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')   
            for _ in range(3):
                pyautogui.press('tab') 
        if ketidakstabilanGD_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')    
            for _ in range(11):
                pyautogui.press('tab') 
        if nausea_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')
            for _ in range(17):
                pyautogui.press('tab') 
        if nyeriAkut_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(2):
                pyautogui.press('tab') 
        if penurunanCurahJantung_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(2):
                pyautogui.press('tab')    
        if penurunanKapasitasAdaptif_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(3):
                pyautogui.press('tab')   
        if polaNapas_VAR.get():
            for _ in range(8):
                pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(7):
                pyautogui.press('tab')  
        if resikoInfeksi_VAR.get():
            for _ in range(13):
                pyautogui.press('tab')
            pyautogui.press('space')   
            for _ in range(20):
                pyautogui.press('tab')  
        if resikoJatuh_VAR.get():
            for _ in range(4):
                pyautogui.press('tab')
            pyautogui.press('space')   
            for _ in range(23):
                pyautogui.press('tab') 

        # GEJALA
        
        if bersihanJalanNapas_VAR.get():
            pyautogui.press('tab') 
            pyautogui.press('space')   
            for _ in range(11):
                pyautogui.press('tab')
        if diare_VAR.get():
            for _ in range(4):
                pyautogui.press('tab')
            pyautogui.press('space')   
            for _ in range(2):
                pyautogui.press('tab')   
        if hipertermia_VAR.get():
            for _ in range(6):
                pyautogui.press('tab')
            pyautogui.press('space')   
        if hipervolemia_VAR.get():
            for _ in range(9):
                pyautogui.press('tab')  
            pyautogui.press('space')   
            for _ in range(6):
                pyautogui.press('tab')  
        if ketidakstabilanGD_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space')    
            for _ in range(13):
                pyautogui.press('tab')  
        if nausea_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')
            for _ in range(10):
                pyautogui.press('tab')  
        if nyeriAkut_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(12):
                pyautogui.press('tab')  
        if penurunanCurahJantung_VAR.get():
            for _ in range(16):
                pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(3):
                pyautogui.press('tab')   
        if penurunanKapasitasAdaptif_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(13):
                pyautogui.press('tab')  
        if polaNapas_VAR.get(): 
            pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(12):
                pyautogui.press('tab')   

        # LUARAN
        
        if bersihanJalanNapas_VAR.get():
            pyautogui.press('tab')  
        if diare_VAR.get(): 
            pyautogui.press('tab') 
        if hipertermia_VAR.get():
            pyautogui.press('tab')
        if hipervolemia_VAR.get():
            pyautogui.press('tab')  
        if ketidakstabilanGD_VAR.get():
            pyautogui.press('tab') 
        if nausea_VAR.get():
            pyautogui.press('tab') 
        if nyeriAkut_VAR.get():
            pyautogui.press('tab')
        if penurunanCurahJantung_VAR.get():
            pyautogui.press('tab')  
        if penurunanKapasitasAdaptif_VAR.get():
            pyautogui.press('tab') 
        if polaNapas_VAR.get(): 
            pyautogui.press('tab') 
        if resikoInfeksi_VAR.get():
            pyautogui.press('tab') 
        if resikoJatuh_VAR.get(): 
            pyautogui.press('tab') 
    
        # KRITERIA HASIL
        
        if bersihanJalanNapas_VAR.get():
            for _ in range(3):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            pyautogui.press('tab')   
            pyautogui.press('space') 
            for _ in range(5):
                pyautogui.press('tab')  
            pyautogui.press('space') 
            for _ in range(3):
                pyautogui.press('tab')  
        if diare_VAR.get():
            pyautogui.press('tab')   
            pyautogui.press('space') 
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space')   
            for _ in range(2):
                pyautogui.press('tab')
            pyautogui.press('space')   
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space')  
        if hipertermia_VAR.get():
            pyautogui.press('tab')   
            pyautogui.press('space')  
            for _ in range(6):
                pyautogui.press('tab')
            pyautogui.press('space')
            for _ in range(3):
                pyautogui.press('tab')   
        if hipervolemia_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')  
            pyautogui.press('space')  
            for _ in range(2):
                pyautogui.press('tab')  
            pyautogui.press('space')  
            for _ in range(2):
                pyautogui.press('tab')  
            pyautogui.press('space') 
            for _ in range(3):
                pyautogui.press('tab')  
            pyautogui.press('space')  
            for _ in range(4):
                pyautogui.press('tab')  
        if ketidakstabilanGD_VAR.get():
            for _ in range(4):
                pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(7):
                pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(5):
                pyautogui.press('tab') 
        if nausea_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')
            for _ in range(4):
                pyautogui.press('tab') 
            pyautogui.press('space')
            for _ in range(7):
                pyautogui.press('tab')  
        if nyeriAkut_VAR.get():
            for _ in range(12):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            for _ in range(7):
                pyautogui.press('tab') 
            pyautogui.press('space')  
            for _ in range(6):
                pyautogui.press('tab')   
        if penurunanCurahJantung_VAR.get():
            for _ in range(4):
                pyautogui.press('tab')
            pyautogui.press('space')  
            pyautogui.press('tab') 
        if penurunanKapasitasAdaptif_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(5):
                pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(9):
                pyautogui.press('tab')  
        if polaNapas_VAR.get(): 
            for _ in range(3):
                pyautogui.press('tab')   
            pyautogui.press('space')  
            pyautogui.press('tab')   
            pyautogui.press('space')
            for _ in range(6):
                pyautogui.press('tab')   
            pyautogui.press('space')    
            for _ in range(3):
                pyautogui.press('tab')  
        if resikoInfeksi_VAR.get(): 
            for _ in range(3):
                pyautogui.press('tab')   
            pyautogui.press('space')   
            for _ in range(2):
                pyautogui.press('tab')   
            pyautogui.press('space')    
        if resikoJatuh_VAR.get(): 
            pyautogui.press('tab')   
            pyautogui.press('space')     
            for _ in range(3):
                pyautogui.press('tab') 

        # INTERVENSI | OBSERVASI
        
        if bersihanJalanNapas_VAR.get():
            pyautogui.press('tab')   
            pyautogui.press('space') 
            for _ in range(3):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            for _ in range(7):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            pyautogui.press('tab')  
        if diare_VAR.get():
            for _ in range(5):
                pyautogui.press('tab')
            pyautogui.press('space')  
            pyautogui.press('tab')   
            pyautogui.press('space')  
            for _ in range(2):
                pyautogui.press('tab')
            pyautogui.press('space')    
            pyautogui.press('tab')   
        if hipertermia_VAR.get():
            for _ in range(2):
                pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(3):
                pyautogui.press('tab')    
        if hipervolemia_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')  
            pyautogui.press('space')  
            pyautogui.press('tab')  
            pyautogui.press('space')    
            for _ in range(4):
                pyautogui.press('tab')   
        if ketidakstabilanGD_VAR.get():
            for _ in range(2):
                pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space')  
            pyautogui.press('tab')
            pyautogui.press('space')   
            for _ in range(2):
                pyautogui.press('tab')  
        if nausea_VAR.get():
            for _ in range(6):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            for _ in range(4):
                pyautogui.press('tab')  
            pyautogui.press('space') 
            for _ in range(3):
                pyautogui.press('tab')  
        if nyeriAkut_VAR.get():
            for _ in range(4):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            for _ in range(2):
                pyautogui.press('tab') 
            pyautogui.press('space')  
            for _ in range(6):
                pyautogui.press('tab')   
        if penurunanCurahJantung_VAR.get():
            for _ in range(2):
                pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(3):
                pyautogui.press('tab')
        if penurunanKapasitasAdaptif_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space')
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space')
            for _ in range(6):
                pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(7):
                pyautogui.press('tab')   
        if polaNapas_VAR.get(): 
            for _ in range(3):
                pyautogui.press('tab')   
            pyautogui.press('space')   
            for _ in range(6):
                pyautogui.press('tab')   
            pyautogui.press('space')  
            pyautogui.press('tab')
        if resikoInfeksi_VAR.get(): 
            pyautogui.press('tab')   
            pyautogui.press('space')    
            pyautogui.press('tab')   
        if resikoJatuh_VAR.get(): 
            pyautogui.press('tab')   
            pyautogui.press('space')     
            for _ in range(2):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            pyautogui.press('tab')     

        # INTERVENSI | TERAPIUTIK
        
        if bersihanJalanNapas_VAR.get():
            pyautogui.press('tab')   
            pyautogui.press('space') 
            for _ in range(11):
                pyautogui.press('tab')   
        if diare_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space')   
            for _ in range(2):
                pyautogui.press('tab')
            pyautogui.press('space')   
        if hipertermia_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(5):
                pyautogui.press('tab')   
        if hipervolemia_VAR.get():
            for _ in range(2):
                pyautogui.press('tab')  
            pyautogui.press('space') 
            pyautogui.press('tab')    
        if ketidakstabilanGD_VAR.get():
            for _ in range(5):
                pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(2):
                pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(2):
                pyautogui.press('tab') 
        if nausea_VAR.get():
            pyautogui.press('tab') 
            pyautogui.press('space') 
            for _ in range(6):
                pyautogui.press('tab')  
            pyautogui.press('space') 
            for _ in range(2):
                pyautogui.press('tab')  
            pyautogui.press('space')  
            for _ in range(2):
                pyautogui.press('tab')  
        if nyeriAkut_VAR.get():
            for _ in range(2):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            pyautogui.press('tab') 
            pyautogui.press('space')  
            for _ in range(4):
                pyautogui.press('tab')    
        if penurunanCurahJantung_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(3):
                pyautogui.press('tab') 
        if penurunanKapasitasAdaptif_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')
            for _ in range(11):
                pyautogui.press('tab')  
        if polaNapas_VAR.get(): 
            pyautogui.press('tab')   
            pyautogui.press('space')   
            for _ in range(9):
                pyautogui.press('tab')   
        if resikoInfeksi_VAR.get(): 
            pyautogui.press('tab')   
            pyautogui.press('space') 
            for _ in range(2): 
                pyautogui.press('tab')   
        if resikoJatuh_VAR.get():     
            for _ in range(2):
                pyautogui.press('tab') 
            pyautogui.press('space')  
            pyautogui.press('tab')   
            pyautogui.press('space')  
            for _ in range(2):
                pyautogui.press('tab')
    
        # INTERVENSI | EDUKASI
        
        if bersihanJalanNapas_VAR.get(): 
            for _ in range(7):
                pyautogui.press('tab')   
        if diare_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')  
        if hipertermia_VAR.get():
            pyautogui.press('tab') 
        if hipervolemia_VAR.get():
            for _ in range(4):
                pyautogui.press('tab')   
        if ketidakstabilanGD_VAR.get():
            for _ in range(10):
                pyautogui.press('tab') 
        if nausea_VAR.get(): 
            for _ in range(7):
                pyautogui.press('tab')  
        if nyeriAkut_VAR.get():
            for _ in range(6):
                pyautogui.press('tab')   
        if penurunanKapasitasAdaptif_VAR.get(): 
            for _ in range(2):
                pyautogui.press('tab')  
        if polaNapas_VAR.get():   
            for _ in range(3):
                pyautogui.press('tab')   
        if resikoInfeksi_VAR.get():  
            for _ in range(6): 
                pyautogui.press('tab')   
        if resikoJatuh_VAR.get():       
            for _ in range(5):
                pyautogui.press('tab') 
        
        # INTERVENSI | KOLABORASI
        
        if bersihanJalanNapas_VAR.get():
            pyautogui.press('tab')   
            pyautogui.press('space')   
        if diare_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space')   
        if hipertermia_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')  
        if hipervolemia_VAR.get():
            pyautogui.press('tab')  
            pyautogui.press('space') 
            pyautogui.press('tab')    
            pyautogui.press('tab')    
        if ketidakstabilanGD_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(3):
                pyautogui.press('tab') 
        if nausea_VAR.get():
            pyautogui.press('tab') 
            pyautogui.press('space')  
        if nyeriAkut_VAR.get():
            pyautogui.press('tab') 
            pyautogui.press('space') 
            pyautogui.press('tab')  
        if penurunanCurahJantung_VAR.get(): 
            for _ in range(4):
                pyautogui.press('tab') 
        if penurunanKapasitasAdaptif_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')
            for _ in range(2):
                pyautogui.press('tab')  
        if polaNapas_VAR.get(): 
            pyautogui.press('tab')   
            pyautogui.press('space')    
        if resikoInfeksi_VAR.get(): 
            pyautogui.press('tab')

        # IMPLEMENTASI - OBSERVASI
        
        if bersihanJalanNapas_VAR.get():
            pyautogui.press('tab')   
            pyautogui.press('space') 
            for _ in range(3):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            for _ in range(7):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            pyautogui.press('tab')  
        if diare_VAR.get():
            for _ in range(5):
                pyautogui.press('tab')
            pyautogui.press('space')  
            pyautogui.press('tab')   
            pyautogui.press('space')  
            for _ in range(2):
                pyautogui.press('tab')
            pyautogui.press('space')    
            pyautogui.press('tab')   
        if hipertermia_VAR.get():
            for _ in range(2):
                pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(3):
                pyautogui.press('tab')    
        if hipervolemia_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')  
            pyautogui.press('space')  
            pyautogui.press('tab')  
            pyautogui.press('space')    
            for _ in range(4):
                pyautogui.press('tab')   
        if ketidakstabilanGD_VAR.get():
            for _ in range(2):
                pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space')  
            pyautogui.press('tab')
            pyautogui.press('space')   
            for _ in range(2):
                pyautogui.press('tab')  
        if nausea_VAR.get():
            for _ in range(6):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            for _ in range(4):
                pyautogui.press('tab')  
            pyautogui.press('space') 
            for _ in range(3):
                pyautogui.press('tab')  
        if nyeriAkut_VAR.get():
            for _ in range(4):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            for _ in range(2):
                pyautogui.press('tab') 
            pyautogui.press('space')  
            for _ in range(6):
                pyautogui.press('tab')   
        if penurunanCurahJantung_VAR.get():
            for _ in range(2):
                pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(3):
                pyautogui.press('tab')
        if penurunanKapasitasAdaptif_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space')
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space')
            for _ in range(6):
                pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(7):
                pyautogui.press('tab')   
        if polaNapas_VAR.get(): 
            pyautogui.press('tab')   
            pyautogui.press('space')   
            for _ in range(6):
                pyautogui.press('tab')   
            pyautogui.press('space')  
            for _ in range(2):
                pyautogui.press('tab')
        if resikoInfeksi_VAR.get(): 
            pyautogui.press('tab')   
            pyautogui.press('space')    
            pyautogui.press('tab')   
        if resikoJatuh_VAR.get(): 
            pyautogui.press('tab')   
            pyautogui.press('space')     
            for _ in range(2):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            pyautogui.press('tab')     

        # IMPLEMENTASI | TERAPIUTIK
        
        if bersihanJalanNapas_VAR.get():
            pyautogui.press('tab')   
            pyautogui.press('space') 
            for _ in range(11):
                pyautogui.press('tab')   
        if diare_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space')   
            for _ in range(2):
                pyautogui.press('tab')
            pyautogui.press('space')   
        if hipertermia_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(7):
                pyautogui.press('tab')   
        if hipervolemia_VAR.get():
            for _ in range(2):
                pyautogui.press('tab')  
            pyautogui.press('space') 
            pyautogui.press('tab')    
        if ketidakstabilanGD_VAR.get():
            for _ in range(5):
                pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(2):
                pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(2):
                pyautogui.press('tab') 
        if nausea_VAR.get():
            pyautogui.press('tab') 
            pyautogui.press('space') 
            for _ in range(6):
                pyautogui.press('tab')  
            pyautogui.press('space') 
            for _ in range(2):
                pyautogui.press('tab')  
            pyautogui.press('space')  
            for _ in range(2):
                pyautogui.press('tab')  
        if nyeriAkut_VAR.get():
            for _ in range(2):
                pyautogui.press('tab') 
            pyautogui.press('space') 
            pyautogui.press('tab') 
            pyautogui.press('space')  
            for _ in range(4):
                pyautogui.press('tab')    
        if penurunanCurahJantung_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')  
            for _ in range(3):
                pyautogui.press('tab') 
        if penurunanKapasitasAdaptif_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')
            for _ in range(11):
                pyautogui.press('tab')  
        if polaNapas_VAR.get(): 
            for _ in range(4):
                pyautogui.press('tab')   
            pyautogui.press('space')   
            for _ in range(2):
                pyautogui.press('tab')   
        if resikoInfeksi_VAR.get(): 
            pyautogui.press('tab')   
            pyautogui.press('space') 
            for _ in range(2): 
                pyautogui.press('tab')   
            pyautogui.press('space') 
            pyautogui.press('tab')   
        if resikoJatuh_VAR.get():     
            for _ in range(2):
                pyautogui.press('tab') 
            pyautogui.press('space')  
            pyautogui.press('tab')   
            pyautogui.press('space')  
            for _ in range(4):
                pyautogui.press('tab')
    
        # IMPLEMENTASI | EDUKASI
        
        if bersihanJalanNapas_VAR.get(): 
            for _ in range(7):
                pyautogui.press('tab')   
        if diare_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')  
        if hipertermia_VAR.get():
            pyautogui.press('tab') 
        if hipervolemia_VAR.get():
            for _ in range(4):
                pyautogui.press('tab')   
        if ketidakstabilanGD_VAR.get():
            for _ in range(10):
                pyautogui.press('tab') 
        if nausea_VAR.get(): 
            for _ in range(7):
                pyautogui.press('tab')  
        if nyeriAkut_VAR.get():
            for _ in range(6):
                pyautogui.press('tab')   
        if penurunanKapasitasAdaptif_VAR.get(): 
            for _ in range(2):
                pyautogui.press('tab')  
        if polaNapas_VAR.get():   
            for _ in range(3):
                pyautogui.press('tab')   
        if resikoInfeksi_VAR.get():  
            for _ in range(6): 
                pyautogui.press('tab')   
        if resikoJatuh_VAR.get():       
            for _ in range(5):
                pyautogui.press('tab') 
        
        # IMPLEMENTASI | KOLABORASI
        
        if bersihanJalanNapas_VAR.get():
            pyautogui.press('tab')   
            pyautogui.press('space')   
        if diare_VAR.get():
            for _ in range(3):
                pyautogui.press('tab')
            pyautogui.press('space')   
        if hipertermia_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')  
        if hipervolemia_VAR.get():
            pyautogui.press('tab')  
            pyautogui.press('space') 
            pyautogui.press('tab')    
            pyautogui.press('tab')    
        if ketidakstabilanGD_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space') 
            for _ in range(4):
                pyautogui.press('tab') 
        if nausea_VAR.get():
            pyautogui.press('tab') 
            pyautogui.press('space')  
        if nyeriAkut_VAR.get():
            pyautogui.press('tab') 
            pyautogui.press('space') 
            pyautogui.press('tab')  
        if penurunanCurahJantung_VAR.get(): 
            for _ in range(4):
                pyautogui.press('tab') 
        if penurunanKapasitasAdaptif_VAR.get():
            pyautogui.press('tab')
            pyautogui.press('space')
            for _ in range(2):
                pyautogui.press('tab')  
        if polaNapas_VAR.get(): 
            pyautogui.press('tab')   
            pyautogui.press('space')    
        if resikoInfeksi_VAR.get(): 
            pyautogui.press('tab')  
        
        pyautogui.press('tab') 
        pyautogui.press('enter')  
  
    def handover(opt):  
        if opt == 'copy': 
            for _ in range(3):
                pyautogui.press('tab') 
            pyautogui.press('space') 
 
            if currentHour > 6 and currentHour < 14:
                pyautogui.press('down')  
            elif currentHour > 13 and currentHour < 21:
                pyautogui.press('down') 
                pyautogui.press('down')  
            else:
                pyautogui.press('down') 
                pyautogui.press('down') 
                pyautogui.press('down')
            pyautogui.press('enter')   
    
            for _ in range(36):
                pyautogui.press('tab')  
             
        if opt == 'new' :
            # sebelum jam 7 terhitung shif tanggal sebelumnya  
            if currentHour < 7 : 
                pyautogui.typewrite(previousDate)
            else :
                pyautogui.typewrite(currentDate)

            for _ in range(2):
                pyautogui.press('tab') 
            pyautogui.typewrite('-') 
            pyautogui.press('tab') 
  
            teks = dr_INPUT.get("1.0", tk.END).strip() 
            time.sleep(3) 
            for nama in teks.splitlines():
                nama_bersih = nama.strip() # Membersihkan spasi di awal/akhir nama jika ada
                
                if nama_bersih: # Memastikan baris tersebut tidak kosong
                    pyautogui.typewrite(nama_bersih) 
                    pyautogui.press('down') 
                    pyautogui.press('enter')  
                    time.sleep(0.5) 

            pyautogui.press('tab') 
            pyautogui.typewrite('0')
            pyautogui.press('tab')  
            pyautogui.typewrite('20') 
            for _ in range(2):
                pyautogui.press('tab') 
                pyautogui.typewrite('1')
            pyautogui.press('tab') 
            pyautogui.typewrite('chepalic')
            pyautogui.press('tab') 
            pyautogui.typewrite('0')
            for _ in range(7):
                pyautogui.press('tab')
            pyautogui.press('space')

            if currentHour > 6 and currentHour < 14:
                pyautogui.press('down')  
            elif currentHour > 13 and currentHour < 21:
                pyautogui.press('down') 
                pyautogui.press('down')  
            else:
                pyautogui.press('down') 
                pyautogui.press('down') 
                pyautogui.press('down')
            pyautogui.press('enter')  

            pyautogui.press('tab')
            pyautogui.typewrite(keluhan_INPUT.get())
            pyautogui.press('tab')
            pyautogui.typewrite(diagnosa_INPUT.get())
            pyautogui.press('tab')
            pyautogui.typewrite(diagnosaKeperawatan)

            if alergi_INPUT.get() == '' or alergi_INPUT.get() == '-' :
                pyautogui.press('tab')
                pyautogui.press('tab')
            else :
                pyautogui.press('tab')
                pyautogui.press('right')
                pyautogui.press('tab')
                pyautogui.typewrite(alergi_INPUT.get())

            pyautogui.press('tab')
            pyautogui.typewrite('infus')
            pyautogui.press('tab')
            pyautogui.typewrite(diit_INPUT.get())
            pyautogui.press('tab')
            pyautogui.typewrite('lab, thorax, ecg')
            pyautogui.press('tab') 
            pyautogui.press('tab')
            pyautogui.typewrite(rpd_INPUT.get())

            for i in range(22):   
                pyautogui.press('tab')

            pyautogui.typewrite('pasien pindahan IGD')
            for _ in range(2):
                pyautogui.press('enter')
            pyautogui.typewrite(terapi_INPUT.get())

            for i in range(3):   
                pyautogui.press('tab')
         
        if currentHour > 6 and currentHour < 14: 
            handOverTime = currentDate + ' 14:00:00' 
        elif currentHour > 13 and currentHour < 21: 
            handOverTime = currentDate + ' 21:00:00' 
        else:
            # Shif malam
            if currentHour > 20 and currentHour < 24 :
                # ganti ke tanggal berikutnya jika sebelum jam 24
                today = datetime.today()  
                next_day = today + timedelta(days=1) 
                tomorrow = next_day.strftime("%Y-%m-%d")
    
                handOverTime = tomorrow + ' 07:00:00'  
            else : 
                # jika diatas jam 24, gunakan tanggal yang sama 
                handOverTime = currentDate + ' 07:00:00' 
    
        pyautogui.write(handOverTime) 

        pyautogui.press('tab') 
        pyautogui.press('space') 

    def automate(opt): 
        time.sleep(2) 
        openLink('discharge')  
        notify("Isi discharge planning?")
        time.sleep(1)
        discharge() 
        messagebox.showinfo('Notifikasi', "Lanjutkan TTV?") 
        time.sleep(1)
        openLink('ttv') 
        messagebox.showinfo('Notifikasi', "Isi TTV?") 
        time.sleep(1)
        vitalSignNewPatient() 
        messagebox.showinfo('Notifikasi', "Lanjutkan CPPT?")  
        time.sleep(1)
        openLink('cppt') 
        messagebox.showinfo('Notifikasi', "Isi CPPT lapor dokter?")  
        time.sleep(2)
        cppt('l')
        messagebox.showinfo('Notifikasi', "Isi CPPT perawat?")  
        time.sleep(2)
        cppt('p')
        messagebox.showinfo('Notifikasi', 'Lanjutkan asesmen?')  
        time.sleep(2)
        if opt == 'd' :
            openLink('asesmenDewasa')
            messagebox.showinfo('Notifikasi', 'Isi asesmen dewasa?')
            time.sleep(2)
            akrid()
        else :
            openLink('asesmenGeriatri')  
            messagebox.showinfo('Notifikasi', 'Isi asesmen geriatri?')
            time.sleep(2)
            akrig() 
        messagebox.showinfo('Notifikasi', "Lanjutkan diagnosa?")  
        time.sleep(2)
        diagnose()  
        messagebox.showinfo('Notifikasi', "Lanjutkan implementasi?")  
        time.sleep(2)
        implement()   
        notify('Switch account. Lanjut handover?')  
        time.sleep(1)
        openLink('handover')   
        notify('Isi handover?')  
        time.sleep(2)
        handover('new')

    class modEntry(tk.Entry):
        def __init__(self, master=None, placeholder='', color='grey', *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.placeholder = placeholder
            self.placeholder_color = color
            self.default_fg_color = self['fg']

            self.bind("<FocusIn>", self._clear_placeholder)
            self.bind("<FocusOut>", self._add_placeholder)

            self._add_placeholder()

        def _clear_placeholder(self, event=None):
            if self['fg'] == self.placeholder_color and self.get() == self.placeholder:
                self.delete(0, tk.END)
                self['fg'] = self.default_fg_color

        def _add_placeholder(self, event=None):
            if not self.get():
                self.insert(0, self.placeholder)
                self['fg'] = self.placeholder_color
  
    class modText(tk.Text):
        def __init__(self, master=None, placeholder='', color='grey', *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.placeholder = placeholder
            self.placeholder_color = color
            self.default_fg_color = self['fg'] if 'fg' in kwargs else 'black'

            self._add_placeholder()
            self.bind("<FocusIn>", self._clear_placeholder)
            self.bind("<FocusOut>", self._add_placeholder)

        def _add_placeholder(self, event=None):
            if self.get("1.0", "end-1c") == "":
                self.insert("1.0", self.placeholder)
                self.config(fg=self.placeholder_color)

        def _clear_placeholder(self, event=None):
            if self.get("1.0", "end-1c") == self.placeholder:
                self.delete("1.0", "end")
                self.config(fg=self.default_fg_color)
 
    # Consistent backup path
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    backUpPath = os.path.join(SCRIPT_DIR, "ttv.txt")

    def vitalSignBackUp(): 
        try:
            data = vitalSignInput.get("1.0", tk.END) 
            with open(backUpPath, "w", encoding="utf-8") as f:
                f.write(data) 
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan data: {e}")

    def vitalSignLoad():
        try: 
            loadButton.config(text="Loading TTV data ...", state="disabled")
            app.update_idletasks()  
            if not os.path.exists(backUpPath):
                raise FileNotFoundError

            with open(backUpPath, "r", encoding="utf-8") as f:
                file_content = f.read().strip() 
            
            vitalSignInput.delete("1.0", tk.END)
            vitalSignInput.insert("1.0", file_content)  
            
        except FileNotFoundError:
            messagebox.showwarning("Warning", "File ttv.txt tidak ditemukan di direktori script.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data: {e}")
        finally: 
            loadButton.config(text="Load", state="normal")
 
    def generate_buttons():
        hour = datetime.now().hour  
        if hour > 6 and hour < 14 : 
            shift, ket = 'morning', ' (P)'
        else:
            shift, ket = 'notMorning', ''
        generateButton.config(text="Formatting ...", state="disabled")
        app.update_idletasks()
        try: 
            input_text = vitalSignInput.get("1.0", tk.END).strip() 
            if not input_text:
                generateButton.config(text="Generate", state="normal")
                return  
            defaults = [None, None, None, None, "97", "0", "36", "22"]
            processed_lines = [] 
            for line in input_text.splitlines():
                if not line.strip(): 
                    continue 
                parts = line.split('-')
                complete_parts = [parts[i] if i < len(parts) else defaults[i] for i in range(8)]
                processed_lines.append("-".join(complete_parts)) 
            final_output = "\n".join(processed_lines) 
            vitalSignInput.delete("1.0", tk.END) 
            vitalSignInput.insert("1.0", final_output)  
            time.sleep(0.5)  
            generateButton.config(text="Creating backup data ...", state="disabled")
            app.update_idletasks() 
            vitalSignBackUp()
            time.sleep(0.5)  
        except Exception as e: 
            messagebox.showerror("Error", f"{e}") 
        finally:
            input_text = vitalSignInput.get("1.0", tk.END).strip()
            lines = input_text.split('\n')  
            for widget in routineFieldset.winfo_children():
                widget.destroy() 
            for line in lines:
                if line.strip():
                    parts = line.split('-')
                    room = parts[0]
                    
                    b = tk.Button(routineFieldset, text=f'{room}{ket}', command=lambda l=line, s=shift: routine(l, s))
                    b.pack(fill='x', pady=2, padx=2)  
            generateButton.config(text="Generate", state="normal")
 
    def vitalSignNewPatient():   
        pyautogui.write(rr_INPUT.get())
        pyautogui.press('tab')  
        pyautogui.write(spo2_INPUT.get())
        pyautogui.press('tab')  
        pyautogui.press('tab')  
        pyautogui.write(suhu_INPUT.get())
        pyautogui.press('tab')  
        pyautogui.write(sistole_INPUT.get())
        pyautogui.press('tab')  
        pyautogui.write(diastole_INPUT.get())
        pyautogui.press('tab')  
        pyautogui.write(nadi_INPUT.get()) 
    
    def vitalSignRoutine(line_data): 
        data = line_data.split('-') 
        
        # Mapping variabel 
        sistole  = data[1]
        diastole = data[2]
        nadi     = data[3]
        spo2     = data[4]
        o2       = data[5] 
        suhu     = data[6]
        rr       = data[7]
  
        pyautogui.write(rr)
        pyautogui.press('tab') 
        pyautogui.write(spo2)
        pyautogui.press('tab') 
        if o2 == '0' : 
            pyautogui.press('tab') 
        else: 
            pyautogui.press('right')
            pyautogui.press('tab')   
        pyautogui.write(suhu)
        pyautogui.press('tab') 
        pyautogui.write(sistole)
        pyautogui.press('tab') 
        pyautogui.write(diastole)
        pyautogui.press('tab') 
        pyautogui.write(nadi)
        pyautogui.press('enter')

    def openLink(opt): 
        pyautogui.hotkey('ctrl', 'l')  
        pyautogui.hotkey('ctrl', 'c')  
        url = pyperclip.paste()  

        if opt == 'asesmenDewasa':
            newURL = re.sub(r"(rawatinap/)[^?]+", r"\1asperawat_ranap", url)  
        if opt == 'asesmenGeriatri':
            newURL = re.sub(r"(rawatinap/)[^?]+", r"\1asperawat_ranap_geriatri", url)  
        if opt == 'cppt': 
            newURL = re.sub(r"(rawatinap/)[^?]+", r"\1cppt", url)  
        if opt == 'diagnose': 
            newURL = re.sub(r"(rawatinap/)[^?]+", r"\1implementasi_keperawatan", url) 
        if opt == 'discharge': 
            newURL = re.sub(r"(rawatinap/)[^?]+", r"\1discharge_planning", url)  
        if opt == 'handover': 
            newURL = re.sub(r"(rawatinap/)[^?]+", r"\1handover_dewasa1", url)  
        if opt == 'ttv':
            newURL = re.sub(r"(rawatinap/)[^?]+", r"\1pemeriksaan_ttv", url)  
 
        pyperclip.copy(newURL)  
        pyautogui.hotkey('ctrl', 'v')   
        pyautogui.press('enter')  

    diagnoseList = []
    implementationList = [] 
    interventionList = [] 

    def copyCPPT(line_data):  
        data = line_data.split('-')
        
        # Mapping variabel 
        sistole  = data[1]
        diastole = data[2]
        nadi     = data[3]
        spo2     = data[4]
        o2       = data[5] 
        suhu     = data[6]
        rr       = data[7]

        statusO2 = ''
        if o2 == '0' :
            statusO2 = 'tanpa O2'
        else :
            statusO2 = f'dengan O2 {o2} lpm'

        stringTTV = f'TD: {sistole}/{diastole}, N: {nadi}, S: {suhu}, RR: {rr}, SPO2: {spo2}% {statusO2}'
    
        cpptTime = ''
        if currentHour > 6 and currentHour < 14:
            cpptTime = currentDate + ' 12:00:00'
            handOverTime = currentDate + ' 14:00:00' 
        elif currentHour > 13 and currentHour < 21:
            cpptTime = currentDate + ' 19:00:00'
            handOverTime = currentDate + ' 21:00:00' 
        else:
            # Shif malam
            if currentHour > 20 and currentHour < 24 :
                # ganti ke tanggal berikutnya jika sebelum jam 24
                today = datetime.today()  
                next_day = today + timedelta(days=1) 
                tomorrow = next_day.strftime("%Y-%m-%d")

                cpptTime = tomorrow + ' 05:00:00'
                handOverTime = tomorrow + ' 07:00:00'  
            else : 
                # jika diatas jam 24, gunakan tanggal yang sama
                cpptTime = currentDate + ' 05:00:00'
                handOverTime = currentDate + ' 07:00:00' 
 
        pyautogui.write(cpptTime)
        pyautogui.press('tab')
        pyautogui.press('tab')

        pyautogui.hotkey('ctrl', 'a')  
        pyautogui.hotkey('ctrl', 'c')  
        s = pyperclip.paste()  
        s_res = re.sub(r'(?:pasien|px)\s*mengatakan\s*', '', s, flags=re.IGNORECASE)   
        pyperclip.copy(s_res)  
        pyautogui.hotkey('ctrl', 'v')   

        pyautogui.press('tab') 

        pyautogui.hotkey('ctrl', 'a')  
        pyautogui.hotkey('ctrl', 'c')  
        o = pyperclip.paste()   
        o_res = re.sub(r"\s*Rr[\s\S]*?(?:\sO2|lpm)\b", f"\n{stringTTV}", o)  
        pyperclip.copy(o_res)  
        pyautogui.hotkey('ctrl', 'v')
 
        pyautogui.press('tab') 
        pyautogui.press('tab') 

        # Asesmen
 
        pyautogui.hotkey('ctrl', 'a')  
        pyautogui.hotkey('ctrl', 'c')  
        asesmen = pyperclip.paste()  
 
        if re.search(r'nyeri', asesmen, re.IGNORECASE):
            diagnoseList.append("nyeri akut") 
            implementationList.append('skala nyeri menurun')
            implementationList.append('grimace berkurang')
            interventionList.append("kaji keluhan nyeri") 
 
        if re.search(r'pola napas', asesmen, re.IGNORECASE):
            diagnoseList.append("pola napas tidak efektif")
            implementationList.append('frekuensi napas membaik')  
            implementationList.append('dipsnea menurun')  
            interventionList.append("pantau kepatenan jalan napas")  
            interventionList.append("monitor saturasi secara berkala") 

        if re.search(r'pola nafas', asesmen, re.IGNORECASE):
            diagnoseList.append("pola napas tidak efektif")  
            implementationList.append('frekuensi napas membaik')  
            implementationList.append('dipsnea menurun')   
            interventionList.append("pantau kepatenan jalan napas") 
            interventionList.append("monitor saturasi secara berkala") 

        if re.search(r'bersihan', asesmen, re.IGNORECASE):
            diagnoseList.append("bersihan jalan napas tidak efektif") 
            implementationList.append('produksi sputum menurun')   
            implementationList.append('wheezing/ronchi menurun')   
            interventionList.append("kaji keluhan batuk") 
            interventionList.append("monitor suara nafas") 

        if re.search(r'curah jantung', asesmen, re.IGNORECASE):
            diagnoseList.append("penurunan curah jantung")
            implementationList.append('status hemodinamik membaik')   
            interventionList.append("monitor status hemodinamik") 

        if re.search(r'hipertermi', asesmen, re.IGNORECASE):
            diagnoseList.append("hipertermia")
            implementationList.append('suhu tubuh dalam batas normal')   
            interventionList.append("monitor suhu tubuh bila perlu") 

        if re.search(r'hipervolemi', asesmen, re.IGNORECASE):
            diagnoseList.append("hipervolemia")
            implementationList.append('intake dan output seimbang')   
            implementationList.append('edema berkurang')   
            interventionList.append("batasi asupan cairan") 
            interventionList.append("monitor keseimbangan cairan") 

        if re.search(r'nausea', asesmen, re.IGNORECASE):
            diagnoseList.append("nausea")
            implementationList.append('keluhan mual berkurang')   
            interventionList.append("monitor keluhan muntah") 
            interventionList.append("pantau isyarat nonverbal ketidaknyamanan") 

        if re.search(r'adaptif', asesmen, re.IGNORECASE):
            diagnoseList.append("penurunan kapasitas adaptif intrakranial")
            implementationList.append('tingkat kesadaran membaik')   
            implementationList.append('irama napas membaik')   
            interventionList.append("monitor peningkatan tekanan darah") 
            interventionList.append("monitor irreguleritas irama napas") 
            interventionList.append("monitor penurunan tingkat kesadaran") 

        if re.search(r'ketidakstabilan', asesmen, re.IGNORECASE):
            diagnoseList.append("resiko ketidakstabilan kadar gula darah")
            implementationList.append('kadar gula darah dalam batas normal')   
            interventionList.append("pantau kadar gula darah secara berkala") 

        if re.search(r'infeksi', asesmen, re.IGNORECASE):
            diagnoseList.append("resiko infeksi")
            implementationList.append('tidak ada tanda infeksi') 
            interventionList.append("pantau tanda tanda infeksi") 

        if re.search(r'jatuh', asesmen, re.IGNORECASE):
            diagnoseList.append("resiko jatuh")
            implementationList.append('tidak ada kejadian jatuh')  
            interventionList.append("pasang kunci bed dan siderail") 
 
        # Convert diagnoseList to a numbered string with new lines
        asesmen_numbering = '\n'.join(f"{i+1}. {item}" for i, item in enumerate(diagnoseList))  
        pyperclip.copy(asesmen_numbering)  
        pyautogui.hotkey('ctrl', 'v')   
        pyautogui.press('tab') 
        pyautogui.press('tab') 

        # Planning 
        pyautogui.hotkey('ctrl', 'a')  
        implementationList.insert(0, 'ttv dalam batas normal') 
        implementationList_numbering = '\n'.join(f"{i+1}. {item}" for i, item in enumerate(implementationList))  
        pyperclip.copy(implementationList_numbering)  
        pyautogui.hotkey('ctrl', 'v')   
        pyautogui.press('tab') 
        pyautogui.press('tab')  

        # interventionList  
        interventionList.insert(0, "monitor tanda vital") # Add to beginning list
        interventionList.append("kolaborasi dengan tim medis") # Add to end of list 
        interventionList_numbering = '\n'.join(f"{i+1}. {item}" for i, item in enumerate(interventionList)) 
        pyperclip.copy(interventionList_numbering)  
        pyautogui.hotkey('ctrl', 'v')   

        pyautogui.press('tab') 
        pyautogui.press('right') 
        pyautogui.press('left') 
        pyautogui.press('tab')  
        pyautogui.write(handOverTime) 
        pyautogui.press('tab')  

        if currentHour > 6 and currentHour < 14:
            pyautogui.write('p')  
        elif currentHour > 13 and currentHour < 21:
            pyautogui.write('s')  
        else:
            pyautogui.write('m') 
        pyautogui.press('tab')
 
        setDiagnose(diagnoseList)
 

    def setDiagnose(diagnoseList):
        reset()
        
        # Sinkronisasi
        diagnose_map = { 
            "bersihan jalan napas": bersihanJalanNapas_VAR,
            "diare": diare_VAR,
            "hipertermia": hipertermia_VAR,
            "hipervolemia": hipervolemia_VAR,
            "resiko ketidakstabilan kadar gula darah": ketidakstabilanGD_VAR,
            "nausea": nausea_VAR,
            "nyeri akut": nyeriAkut_VAR,
            "penurunan curah jantung": penurunanCurahJantung_VAR,
            "penurunan kapasitas adaptif intrakranial": penurunanKapasitasAdaptif_VAR,
            "pola napas tidak efektif": polaNapas_VAR,
            "resiko infeksi": resikoInfeksi_VAR,
            "resiko jatuh": resikoJatuh_VAR
        }
        
        for diagnosis in diagnoseList:
            if diagnosis in diagnose_map:
                diagnose_map[diagnosis].set(True)

    def diagnoseDate() : 
        currentHour = datetime.now().hour   
        pyautogui.press('tab')
        pyautogui.press('space') 
        if currentHour > 6 and currentHour < 14: 
            pyautogui.press('down') 
        elif currentHour > 13 and currentHour < 21:
            for i in range(2): 
                pyautogui.press('down') 
        else:
            for i in range(3): 
                pyautogui.press('down') 
        pyautogui.press('enter')
        for i in range(5): 
            pyautogui.press('tab')
    
    def routine(line, shift):
        time.sleep(2)
        openLink('ttv') 
        notify('Isi TTV?')
        time.sleep(1)
        vitalSignRoutine(line)  
        notify('Lanjut CPPT?')
        time.sleep(1)
        openLink('cppt')  
        notify('Rewrite CPPT?')
        time.sleep(2)
        copyCPPT(line)   
        setDiagnose(diagnoseList)
        if shift != 'morning' : 
            notify('Pindah ke diagnosa?')
            time.sleep(1)    
        openLink('diagnose') 
        notify('Isi diagnosa?')
        time.sleep(1) 
        diagnoseDate()
        diagnose() 
        notify('Lanjut implementasi?')
        time.sleep(2)
        implement()  
        diagnoseList.clear()
        interventionList.clear()
        implementationList.clear()
 
    def routine2():
        time.sleep(2)
        openLink('handover') 
        notify('Isi handover?')
        time.sleep(2)
        handover('copy')

    def getFile(opt):
        time.sleep(2)  
        pyautogui.hotkey("ctrl", "l")  
        pyautogui.hotkey("ctrl", "c")  
        url_asal = pyperclip.paste()  
        match = re.search(r"idx=(\d+)&idp=(\d+)", url_asal) 
        if match:
            idx = match.group(1)
            idp = match.group(2) 

            if opt == 'igd':
                url_baru = f"http://20.20.20.6/app.mersi-hospital/live.rme/igd/print_asperawat_gd?idp={idp}&idx={idx}&print=ok" 
            if opt == 'irj':
                url_baru = f'http://20.20.20.6/app.mersi-hospital/live.rme/rawatinap/transfer_pasien_rajal?idx={idx}&idp={idp}'
        else:
            print("Parameter idx atau idp tidak ditemukan.")

        pyperclip.copy(url_baru)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")  

    def partial_askep(opt):
        time.sleep(2)
        if opt == 'd' :
            akrid()
        if opt == 'g' :
            akrig()         
        messagebox.showinfo('Notifikasi', "Lanjutkan diagnosa?")  
        time.sleep(2)
        diagnose()  
        messagebox.showinfo('Notifikasi', "Lanjutkan implementasi?")  
        time.sleep(2)
        implement()   

    def generateQR(opt): 
        phone = '6281515066734'

        if opt == 'report' :
            msg = report_EN.get("1.0", tk.END).strip()
        if opt == 'rx' :
            msg = rx_EN.get("1.0", tk.END).strip()

        if not msg:
            notify('Empty message not allowed') 
            return 

        try: 
            encoded_text = urllib.parse.quote(msg) 
            wa_link = f"https://wa.me/{phone}?text={encoded_text}"
             
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(wa_link)
            qr.make(fit=True) 
             
            img_qr = qr.make_image(fill_color="black", back_color="white") 
            img_qr = img_qr.resize((400, 400), Image.Resampling.LANCZOS) 
            img_tk = ImageTk.PhotoImage(img_qr)
             
            popup = tk.Toplevel(app) 
            popup.title("Scan QR Code")
            popup.geometry("450x600") 
            popup.configure(bg="white")
            popup.resizable(False, False)  
            popup.transient(app)
            popup.grab_set()
 
            lbl_info = tk.Label(popup, text="Silakan scan untuk membuka WhatsApp", bg="white", font=("Arial", 10, "bold"))
            lbl_info.pack(pady=10) 
            lbl_popup_qr = tk.Label(popup, image=img_tk, bg="white")
            lbl_popup_qr.image = img_tk 
            lbl_popup_qr.pack(pady=5)
             
            btn_close = tk.Button(popup, text="Tutup", command=popup.destroy, bg="#d33", fg="white", width=10)
            btn_close.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat QR Code: {e}")
 
    # ========== Main apps GUI ==========
 
    app = tk.Tk()
    app.title("males-banget")   
    app.geometry("+0+0")
    app.after(7200000, app.destroy)
    app.attributes('-topmost', True)   
    ff = 'Calibri'
    fs = '8' 
    notebook = ttk.Notebook(app)
    notebook.pack(expand=True, fill='both')
 
    tab1 = ttk.Frame(notebook) 
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook) 
 
    notebook.add(tab1, text=' Routine ') 
    notebook.add(tab2, text=' New Patient ')
    notebook.add(tab3, text=' Report ') 

    # ========== Tab 1 : Routine ========== 

    vitalSignFieldset = ttk.LabelFrame(tab1, text=" Vital Signs ")
    vitalSignFieldset.pack(fill='x', padx=5, pady=5) 
    vitalSignInput = tk.Text(vitalSignFieldset, width=30, height=10, font=(ff, fs))
    vitalSignInput.pack(fill='x', padx=5)
     
    loadButton = tk.Button(vitalSignFieldset, text="Load", font=(ff, fs), command=vitalSignLoad)
    loadButton.pack(side=tk.LEFT, padx='1')
    generateButton = tk.Button(vitalSignFieldset, text="Generate", font=(ff, fs), command=generate_buttons)
    generateButton.pack(side=tk.LEFT, padx='1')

    routineFieldset = ttk.LabelFrame(tab1, text=" Routine ")
    routineFieldset.pack(fill='x', padx=5, pady=5)    
    info = tk.Label(routineFieldset, text='Generated button will appear here', font=(ff, fs)) 
    info.pack()  
    
    routineHandoverFieldset = ttk.LabelFrame(tab1, text=" Handover ")
    routineHandoverFieldset.pack(fill='x', padx=5, pady=5)    
    handoverButton = tk.Button(routineHandoverFieldset, text="Fill out handover", command=routine2)
    handoverButton.pack(fill='x', padx=1)

    # ========== Tab 2 : New Patient ==========

    infoFieldset = ttk.LabelFrame(tab2, text=" ● Summary ")
    infoFieldset.pack(fill='x', padx=5, pady=5)  
 
    row1 = ttk.Frame(infoFieldset)
    row1.pack(fill='x', side=tk.TOP, anchor='w') 
    pindahan_INPUT = modEntry(row1, width='4', font=(ff, fs), placeholder='From') 
    pindahan_INPUT.pack(side=tk.LEFT, padx='1', pady='2')   
    mr_INPUT = modEntry(row1, width='8', font=(ff, fs), placeholder='MR') 
    mr_INPUT.pack(side=tk.LEFT, padx='1', pady='2')   
    nama_INPUT = modEntry(row1, width='12', font=(ff, fs), placeholder='Name') 
    nama_INPUT.pack(side=tk.LEFT, padx='1', pady='2')
    usia_INPUT = modEntry(row1, width='4', font=(ff, fs), placeholder='Age') 
    usia_INPUT.pack(side=tk.LEFT, padx='1') 

    row2 = ttk.Frame(infoFieldset)
    row2.pack(fill='x', side=tk.TOP, anchor='w') 
    diagnosa_INPUT = modEntry(row2, width='30', font=(ff, fs), placeholder='Diagnose') 
    diagnosa_INPUT.pack(side=tk.LEFT, padx='1')
     
    row3 = ttk.Frame(infoFieldset)
    row3.pack(fill='x', side=tk.TOP, anchor='w') 
    keluhan_INPUT = modEntry(row3, width='30', font=(ff, fs), placeholder='Keluhan') 
    keluhan_INPUT.pack(side=tk.LEFT, padx='1')
  
    row4 = ttk.Frame(infoFieldset)
    row4.pack(fill='x', side=tk.TOP, anchor='w') 
    rps_INPUT = modEntry(row4, width='30', font=(ff, fs), placeholder='RPS') 
    rps_INPUT.pack(side=tk.LEFT, padx='1')
 
    row5 = ttk.Frame(infoFieldset)
    row5.pack(fill='x', side=tk.TOP, anchor='w') 
    rpd_INPUT = modEntry(row5, width='30', font=(ff, fs), placeholder='RPD') 
    rpd_INPUT.pack(side=tk.LEFT, padx='1') 
  
    row6 = ttk.Frame(infoFieldset)
    row6.pack(fill='x', side=tk.TOP, anchor='w')  
    sistole_INPUT = modEntry(row6, width='5', font=(ff, fs), placeholder='Sis') 
    sistole_INPUT.pack(side=tk.LEFT, padx='1')  
    diastole_INPUT = modEntry(row6, width='5', font=(ff, fs), placeholder='Dia') 
    diastole_INPUT.pack(side=tk.LEFT, padx='1')  
    nadi_INPUT = modEntry(row6, width='4', font=(ff, fs), placeholder='N') 
    nadi_INPUT.pack(side=tk.LEFT, padx='1')  
    suhu_INPUT = modEntry(row6, width='4', font=(ff, fs), placeholder='S') 
    suhu_INPUT.pack(side=tk.LEFT, padx='1')  
    rr_INPUT = modEntry(row6, width='4', font=(ff, fs), placeholder='RR') 
    rr_INPUT.pack(side=tk.LEFT, padx='1')  
    spo2_INPUT = modEntry(row6, width='4', font=(ff, fs), placeholder='Sat') 
    spo2_INPUT.pack(side=tk.LEFT, padx='1')
  
    row7 = ttk.Frame(infoFieldset)
    row7.pack(fill='x', side=tk.TOP, anchor='w')   
    diit_INPUT = modEntry(row7, width=5, font=(ff, fs), placeholder='Diet') 
    diit_INPUT.pack(side=tk.LEFT, padx='1') 
    alergi_INPUT = modEntry(row7, width=24, font=(ff, fs), placeholder='Allergy') 
    alergi_INPUT.pack(side=tk.LEFT, padx='1')  
      
    row8 = ttk.Frame(infoFieldset)
    row8.pack(fill='x', side=tk.TOP, anchor='w')  
    tindakan_INPUT = modEntry(row8, width=30, font=(ff, fs), placeholder='Plan') 
    tindakan_INPUT.pack(side=tk.LEFT, padx='1')  
 
    row9 = ttk.Frame(infoFieldset)
    row9.pack(fill='x', side=tk.TOP, anchor='w') 
    dr_INPUT = modText(row9, width=30, height=2, font=(ff, fs), placeholder='Doctor')
    dr_INPUT.pack(side=tk.LEFT, padx='1') 
    
    row10 = ttk.Frame(infoFieldset)
    row10.pack(fill='x', side=tk.TOP, anchor='w') 
    terapi_INPUT = modText(row10, width=30, height=5, font=(ff, fs), placeholder='Therapy')
    terapi_INPUT.pack(side=tk.LEFT, padx='1')   

    diagnoseFieldset = ttk.LabelFrame(tab2, text=" ● Diagnose ")
    diagnoseFieldset.pack(fill='x', padx=5, pady=5) 
 
    row11 = ttk.Frame(diagnoseFieldset)
    row11.pack(fill='x', side=tk.TOP, anchor='w')  
    bersihanJalanNapas_VAR = tk.BooleanVar()  
    bersihanJalanNapas = tk.Checkbutton(row11, text="Bersihan Jalan Napas", font=(ff, fs), variable=bersihanJalanNapas_VAR)
    bersihanJalanNapas.pack(side=tk.LEFT, padx='1') 

    row12 = ttk.Frame(diagnoseFieldset)
    row12.pack(fill='x', side=tk.TOP, anchor='w')  
    diare_VAR = tk.BooleanVar()  
    diare = tk.Checkbutton(row12, text="Diare", font=(ff, fs), variable=diare_VAR)
    diare.pack(side=tk.LEFT, padx='1') 
  
    row13 = ttk.Frame(diagnoseFieldset)
    row13.pack(fill='x', side=tk.TOP, anchor='w') 
    hipertermia_VAR = tk.BooleanVar()  
    hipertermia = tk.Checkbutton(row13, text="Hipertermia", font=(ff, fs), variable=hipertermia_VAR)
    hipertermia.pack(side=tk.LEFT, padx='1')

    row14 = ttk.Frame(diagnoseFieldset)
    row14.pack(fill='x', side=tk.TOP, anchor='w')
    hipervolemia_VAR = tk.BooleanVar()  
    hipervolemia = tk.Checkbutton(row14, text="Hipervolemia", font=(ff, fs), variable=hipervolemia_VAR)
    hipervolemia.pack(side=tk.LEFT, padx='1')            

    row15 = ttk.Frame(diagnoseFieldset)
    row15.pack(fill='x', side=tk.TOP, anchor='w')
    ketidakstabilanGD_VAR = tk.BooleanVar()   
    ketidakstabilanGD = tk.Checkbutton(row15, text="Ketidakstabilan GD", font=(ff, fs), variable=ketidakstabilanGD_VAR)
    ketidakstabilanGD.pack(side=tk.LEFT, padx='1') 

    row16 = ttk.Frame(diagnoseFieldset)
    row16.pack(fill='x', side=tk.TOP, anchor='w')
    nausea_VAR = tk.BooleanVar() 
    nausea = tk.Checkbutton(row16, text="Nausea", font=(ff, fs), variable=nausea_VAR)
    nausea.pack(side=tk.LEFT, padx='1')

    row17 = ttk.Frame(diagnoseFieldset)
    row17.pack(fill='x', side=tk.TOP, anchor='w')
    nyeriAkut_VAR = tk.BooleanVar()
    nyeriAkut = tk.Checkbutton(row17, text="Nyeri Akut", font=(ff, fs), variable=nyeriAkut_VAR)
    nyeriAkut.pack(side=tk.LEFT, padx='1')

    row18 = ttk.Frame(diagnoseFieldset)
    row18.pack(fill='x', side=tk.TOP, anchor='w')
    penurunanCurahJantung_VAR = tk.BooleanVar()
    penurunanCurahJantung = tk.Checkbutton(row18, text="Penurunan Curah Jantung", font=(ff, fs), variable=penurunanCurahJantung_VAR)
    penurunanCurahJantung.pack(side=tk.LEFT, padx='1')

    row19 = ttk.Frame(diagnoseFieldset)
    row19.pack(fill='x', side=tk.TOP, anchor='w')
    penurunanKapasitasAdaptif_VAR = tk.BooleanVar()
    penurunanKapasitasAdaptif = tk.Checkbutton(row19, text="Penurunan Kapasitas Adaptif", font=(ff, fs), variable=penurunanKapasitasAdaptif_VAR)
    penurunanKapasitasAdaptif.pack(side=tk.LEFT, padx='1') 

    row20 = ttk.Frame(diagnoseFieldset)
    row20.pack(fill='x', side=tk.TOP, anchor='w')
    polaNapas_VAR = tk.BooleanVar()
    polaNapas = tk.Checkbutton(row20, text="Pola Napas", font=(ff, fs), variable=polaNapas_VAR)
    polaNapas.pack(side=tk.LEFT, padx='1')

    row21 = ttk.Frame(diagnoseFieldset)
    row21.pack(fill='x', side=tk.TOP, anchor='w')
    resikoInfeksi_VAR = tk.BooleanVar()
    resikoInfeksi = tk.Checkbutton(row21, text="Resiko Infeksi", font=(ff, fs), variable=resikoInfeksi_VAR)
    resikoInfeksi.pack(side=tk.LEFT, padx='1')

    row22 = ttk.Frame(diagnoseFieldset)
    row22.pack(fill='x', side=tk.TOP, anchor='w')
    resikoJatuh_VAR = tk.BooleanVar()
    resikoJatuh = tk.Checkbutton(row22, text="Resiko Jatuh", font=(ff, fs), variable=resikoJatuh_VAR)
    resikoJatuh.pack(side=tk.LEFT, padx='1')
   
    row23 = ttk.Frame(diagnoseFieldset)
    row23.pack(fill='x', side=tk.TOP, anchor='w')
    getAsesmenIGD = tk.Button(row23, text="asesmen IGD", font=(ff, fs), command=lambda: getFile('igd'))
    getAsesmenIGD.pack(side=tk.LEFT, padx='1')
    getAsesmenIRJ = tk.Button(row23, text="transfer ", font=(ff, fs), command=lambda: getFile('irj'))
    getAsesmenIRJ.pack(side=tk.LEFT, padx='1')
 
    row24 = ttk.Frame(diagnoseFieldset)
    row24.pack(fill='x', side=tk.TOP, anchor='w')
    scan_BT = tk.Button(row24, text="scan-i", font=(ff, fs), command=lambda: scan('i'))
    scan_BT.pack(side=tk.LEFT, padx='1')  
    scan_transfer_BT = tk.Button(row24, text="scan-t", font=(ff, fs), command=lambda: scan('t'))
    scan_transfer_BT.pack(side=tk.LEFT, padx='1')
   
    row25 = ttk.Frame(diagnoseFieldset)
    row25.pack(fill='x', side=tk.TOP, anchor='w')
    auto_dewasa_BT = tk.Button(row25, text="auto-d", font=(ff, fs), command=lambda: automate('d')) 
    auto_dewasa_BT.pack(side=tk.LEFT, padx='1')
    auto_geriatri_BT = tk.Button(row25, text="auto-g", font=(ff, fs), command=lambda: automate('g')) 
    auto_geriatri_BT.pack(side=tk.LEFT, padx='1')
    asesmen_dewasa_BT = tk.Button(row25, text="akrid", font=(ff, fs), command=lambda: partial_askep('d')) 
    asesmen_dewasa_BT.pack(side=tk.LEFT, padx='1')
    asesmen_geriatri_BT = tk.Button(row25, text="akrig", font=(ff, fs), command=lambda: partial_askep('g')) 
    asesmen_geriatri_BT.pack(side=tk.LEFT, padx='1')

    # ========== Tab 3 : Report and Rx ========== 

    report_FR = ttk.Frame(tab3)
    report_FR.grid(row=0, column=0, padx=5, sticky="ew")    
    report_LB = tk.Label(report_FR, text='Lapor Pasien :', font=(ff, fs)) 
    report_LB.pack(side=tk.LEFT)    
    btn_generate = tk.Button(report_FR, text="QR", font=(ff, fs), command=lambda: generateQR('report'))
    btn_generate.pack(side=tk.RIGHT)  
    report_button = tk.Button(report_FR, text="compose", font=(ff, fs), command=report) 
    report_button.pack(side=tk.RIGHT) 
    report_copy_BT = tk.Button(report_FR, text="copy", font=(ff, fs), command=copy_report) 
    report_copy_BT.pack(side=tk.RIGHT)  

    report_EN = tk.Text(tab3, width=20, height=15, font=(ff, fs)) 
    report_EN.grid(row=1, column=0, padx=5, sticky="nsew")  
 
    rx_FR = ttk.Frame(tab3)
    rx_FR.grid(row=2, column=0, padx=5, sticky="ew")   

    rx_LB = tk.Label(rx_FR, text='Resep :', font=(ff, fs)) 
    rx_LB.pack(side=tk.LEFT)   
    qr_rx = tk.Button(rx_FR, text="QR", font=(ff, fs), command=lambda: generateQR('rx'))
    qr_rx.pack(side=tk.RIGHT)  
    rx_BT = tk.Button(rx_FR, text="compose", font=(ff, fs), command=rx) 
    rx_BT.pack(side=tk.RIGHT) 
    rx_copy_BT = tk.Button(rx_FR, text="copy", font=(ff, fs), command=copy_rx) 
    rx_copy_BT.pack(side=tk.RIGHT)  

    rx_EN = tk.Text(tab3, width=20, height=10, font=(ff, fs)) 
    rx_EN.grid(row=3, column=0, padx=5, sticky="nsew")   

    app.mainloop()
      
# Login GUI
root = tk.Tk()
root.title('?')
root.after(10000, root.destroy)
    
# 1. Variable penampung teks
password_var = tk.StringVar()

# 2. Trigger fungsi checkPassword setiap kali teks berubah
password_var.trace_add("write", checkPassword)

# 3. Entry widget
password_entry = tk.Entry(root, textvariable=password_var, show="*")
password_entry.pack(padx=20, pady=20)
password_entry.focus()

root.mainloop() 