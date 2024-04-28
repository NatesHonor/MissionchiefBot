import json

from selenium.common import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def dispatch_police_transport(prisoners, vehicle_dispatch_mapping, vehicle_types, driver, vehicles_file):
    if prisoners > 1:
        prisoner_vehicle = vehicle_dispatch_mapping['Prisoner Transports']

        for vehicle_id, vehicle_info in vehicle_types.items():
            if isinstance(prisoner_vehicle, list):
                for recovery_type in prisoner_vehicle:
                    if vehicle_info['name'] == recovery_type:
                        dispatch_prisoner_van(driver, vehicles_file, prisoner_vehicle, prisoners)
            else:
                if vehicle_info['name'] == prisoner_vehicle:
                    dispatch_prisoner_van(driver, vehicles_file, prisoner_vehicle, prisoners)


def dispatch_prisoner_van(driver, vehicles_file, recovery_vehicle_type, crashed_cars):
    dispatched_recovery_vehicles = 0
    with open(vehicles_file, 'r') as f:
        vehicle_types = json.load(f)

    for vehicle_id, vehicle_info in vehicle_types.items():
        if vehicle_info['name'] == recovery_vehicle_type:
            checkbox_id = f"vehicle_checkbox_{vehicle_id}"
            try:
                checkbox = WebDriverWait(driver, 1).until(ec.element_to_be_clickable((By.ID, checkbox_id)))
                if not checkbox.is_selected():
                    ActionChains(driver).move_to_element(checkbox).perform()
                    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                    driver.execute_script("arguments[0].click();", checkbox)
                    print(f"Vehicle {recovery_vehicle_type}:{vehicle_id} selected.")
                    dispatched_recovery_vehicles += 1
                    if dispatched_recovery_vehicles >= crashed_cars:
                        break
            except (NoSuchElementException, ElementClickInterceptedException, TimeoutException):
                print(f"Vehicle  {recovery_vehicle_type}:{vehicle_id} already Dispatched.")
                continue
