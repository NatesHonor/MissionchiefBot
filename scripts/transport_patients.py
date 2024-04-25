import json
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def transport_all_ems_patients(driver, vehicle_data_file):
    with open(vehicle_data_file, 'r') as f:
        vehicle_data = json.load(f)

    for vehicle_id, vehicle_info in vehicle_data.items():
        if vehicle_info['name'].lower() == 'als ambulance':
            vehicle_url = f"https://www.missionchief.com/vehicles/{vehicle_id}"
            driver.get(vehicle_url)
            try:
                transport_request_header = WebDriverWait(driver, 1).until(
                    ec.presence_of_element_located((By.ID, 'h2_sprechwunsch'))
                )
                if transport_request_header:
                    transport_buttons = driver.find_elements(By.XPATH, "//a[contains(@id, 'btn_approach_')]")
                    if transport_buttons:
                        random.choice(transport_buttons).click()
                        print(f"Transport initiated for patient in vehicle ID: {vehicle_id}")
            except (NoSuchElementException, TimeoutException):
                continue
