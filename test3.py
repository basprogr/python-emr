import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
 
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)

try: 
    driver.get("http://20.20.20.6/app.mersi-hospital/live/ri/entry/transaksi_mrs_aktif")
    driver.maximize_window()      
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_field.send_keys("20224015") 
    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys("2024") 
    password_field.send_keys(Keys.RETURN) 
    time.sleep(2)
    driver.get("http://20.20.20.6/app.mersi-hospital/live/ri/entry/transaksi_mrs_aktif") 
    time.sleep(5)
 
    tab_utama = driver.current_window_handle
  
    row_target = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//tr[contains(., '310 Bed D')]"))
    )
    row_target.click()  
    time.sleep(1) 
    btn_rme = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btn-rme"))
    )
    btn_rme.click() 
    time.sleep(5) 


    current_url = driver.current_url
    print(current_url)
    new_url = current_url.replace("asperawat_ranap", "pemeriksaan_ttv")  
    driver.get(new_url)
    # time.sleep(3)  
 
    # semua_tab = driver.window_handles 
    # if len(semua_tab) > 1: 
    #     tab_baru = semua_tab[-1]
    #     driver.switch_to.window(tab_baru)  
    #     time.sleep(2) # Contoh melihat tab baru sebentar  
    #     driver.switch_to.window(tab_utama)
    # else:
    #     print("Tidak ada tab baru yang terdeteksi.")

    # print("Skrip selesai. Anda kembali di tab utama dan browser tetap terbuka.")

except Exception as e:
    print(f"Terjadi error: {e}")