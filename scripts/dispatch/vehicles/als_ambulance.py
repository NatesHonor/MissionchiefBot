from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException


def dispatch_ems(patients, vehicle_dispatch_mapping, vehicle_types, driver):
    ems_chief_type = vehicle_dispatch_mapping.get('EMS Chiefs')
    if patients >= 10:
        for vehicle_id, vehicle_info in vehicle_types.items():
            if vehicle_info['name'] == ems_chief_type:
                checkbox_id = f"vehicle_checkbox_{vehicle_id}"
                try:
                    checkbox = WebDriverWait(driver, 1).until(ec.element_to_be_clickable((By.ID, checkbox_id)))
                    if not checkbox.is_selected():
                        checkbox.click()
                        print(f"Dispatched {ems_chief_type} with vehicle ID: {vehicle_id}")
                        break
                except (NoSuchElementException, ElementClickInterceptedException, TimeoutException):
                    print(f"{ems_chief_type}:{vehicle_id} Already dispatched, continuing...")
                    continue
    als_ambulance_type = vehicle_dispatch_mapping.get('ambulances', 'Default Ambulance Type')
    for vehicle_id, vehicle_info in vehicle_types.items():
        if vehicle_info['name'] == als_ambulance_type and patients > 0:
            checkbox_id = f"vehicle_checkbox_{vehicle_id}"
            try:
                checkbox = WebDriverWait(driver, 1).until(ec.element_to_be_clickable((By.ID, checkbox_id)))
                if not checkbox.is_selected():
                    checkbox.click()
                    patients -= 1
                    print(f"Dispatched {als_ambulance_type} with vehicle ID: {vehicle_id}")
                    if patients == 0:
                        break
            except (NoSuchElementException, ElementClickInterceptedException, TimeoutException):
                print(f"{als_ambulance_type}:{vehicle_id} Already dispatched, continuing...")
                continue
