# =========================
# IMPORTS
# =========================
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# =========================
# INICIAR DRIVER
# =========================
driver = webdriver.Chrome()
driver.maximize_window()

# =========================
# ABRIR SITE UBER
# =========================
driver.get("https://drivers.uber.com/earnings/activities")

# =========================
# LOGIN MANUAL
# =========================
wait = WebDriverWait(driver, 300)

# =========================
# VALIDAR LOGIN
# =========================
wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//h5[contains(text(),'Informações da atividade')]")
    )
)

print("Login detectado com sucesso!")

# =========================
# ABRIR SELETOR DE DATA (CALENDÁRIO)
# =========================
range_data = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//input[contains(@aria-label, 'Select a date range')]")
    )
)

driver.execute_script("arguments[0].click();", range_data)

print("Calendário aberto!")
time.sleep(2)

# =========================
# ABRIR DROPDOWN DE ANO
# =========================
select_ano = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//*[contains(@aria-label, 'Year')]")
    )
)

driver.execute_script("arguments[0].click();", select_ano)

print("Dropdown de ano aberto!")

# =========================
# ESPERAR POPOVER
# =========================
popover = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//div[@data-baseweb='popover']")
    )
)

# =========================
# PEGAR LISTBOX
# =========================
listbox = popover.find_element(
    By.XPATH, ".//ul[@role='listbox']"
)

# =========================
# SELECIONAR ANO
# =========================
ANO_DESEJADO = "2025"

anos = listbox.find_elements(By.XPATH, ".//div[@role='option']")

for ano in anos:
    if ano.text.strip() == ANO_DESEJADO:
        driver.execute_script("arguments[0].scrollIntoView(true);", ano)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", ano)
        print(f"Ano {ANO_DESEJADO} selecionado!")
        break

time.sleep(3)

# =========================
# SELECIONAR MÊS
# =========================

MÊS_DESEJADO = "OCTOBER"

meses = listbox.find_elements(By.XPATH, ".//div[@role='option']")

for mes in meses:
    if mes.text.strip() == MÊS_DESEJADO:
        driver.execute_script("arguments[0].scrollIntoView(true);", mes)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", mes)
        print(f"Mês {MÊS_DESEJADO} selecionado!")
        break

time.sleep(3)

# =========================
# SELECIONAR SEGUNDA-FERA
# =========================
DIA_DESEJADO = "Monday"
