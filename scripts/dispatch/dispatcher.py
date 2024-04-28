import json
import time

from data.mission_utils import remove_mission
from scripts.dispatch.vehicles.tow_truck import dispatch_tow_truck
from scripts.dispatch.vehicles.als_ambulance import dispatch_ems
from scripts.dispatch.vehicles.prisoner_transport import dispatch_police_transport
from scripts.dispatch.personnel.personnel import dispatch_personnel

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException


def dispatch_vehicles(driver, mission_id, vehicles_file, mission_requirements, patients,
                      vehicle_dispatch_mapping, crashed_cars, mission_data_file, prisoners, personnel_dispatch_mapping):
    with open(vehicles_file, 'r') as f:
        vehicle_types = json.load(f)

    with open(mission_data_file, 'r') as f:
        mission_data = json.load(f)

    mission_url = f"https://www.missionchief.com/missions/{mission_id}"
    driver.get(mission_url)

    try:
        transport_needed_alert = driver.find_element(By.XPATH, "//*[contains(text(), 'Transport is needed!')]")
        if transport_needed_alert:
            print(f"Skipping mission {mission_id} because it has a transport request.")
            return
    except NoSuchElementException:
        pass

    try:
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, 'all')))
    except TimeoutException:
        remove_mission(mission_id, mission_data)
        return

    dispatch_personnel(driver, mission_id, vehicles_file, mission_data_file, personnel_dispatch_mapping)
    dispatch_tow_truck(crashed_cars, vehicle_dispatch_mapping, vehicle_types, driver, vehicles_file)
    dispatch_police_transport(prisoners, vehicle_dispatch_mapping, vehicle_types, driver, vehicles_file)
    dispatch_ems(patients, vehicle_dispatch_mapping, vehicle_types, driver)

    for requirement, required_count in mission_requirements.items():
        dispatched_count = 0
        vehicle_type_name = vehicle_dispatch_mapping.get(requirement)
        if not vehicle_type_name:
            print(f"No mapping found for requirement: {requirement}")
            continue

        for vehicle_id, vehicle_info in vehicle_types.items():
            if vehicle_info['name'] == vehicle_type_name and dispatched_count < required_count:
                checkbox_id = f"vehicle_checkbox_{vehicle_id}"
                try:
                    checkbox = WebDriverWait(driver, 0).until(ec.element_to_be_clickable((By.ID, checkbox_id)))
                    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                    driver.execute_script("arguments[0].click();", checkbox)
                    dispatched_count += 1
                    print(f"Vehicle {vehicle_type_name}:{vehicle_id} selected.")
                    if dispatched_count == required_count:
                        break
                except TimeoutException:
                    print(f"Skipping {vehicle_type_name}:{vehicle_id}.")
                    continue
                except ElementClickInterceptedException:
                    print(
                        f"ElementClickInterceptedException for vehicle ID {vehicle_id},"
                        f" trying alternative click method.")
                    driver.execute_script("arguments[0].click();", checkbox)
                except (NoSuchElementException, TimeoutException):
                    print(f"Skipping {vehicle_type_name}:{vehicle_id}.")
                    continue

    try:
        dispatch_button = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.ID, 'alert_btn')))
        dispatch_button.click()
        print("Dispatched all selected vehicles.")
        time.sleep(5)
    except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
        print("Dispatch button not found. Moving on...")
