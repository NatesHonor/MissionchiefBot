import json
import math
import time

from scripts.dispatch.vehicles.tow_truck import dispatch_tow_truck
from scripts.dispatch.vehicles.als_ambulance import dispatch_ems
from scripts.dispatch.vehicles.prisoner_transport import dispatch_police_transport
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException


def calculate_vehicles_needed(personnel_count, group_size):
    return math.ceil(personnel_count / group_size)


def dispatch_vehicles(driver, mission_id, vehicles_file, mission_requirements, patients,
                      vehicle_dispatch_mapping, crashed_cars, mission_data_file, prisoners):
    with open(vehicles_file, 'r') as f:
        vehicle_types = json.load(f)
    with open(mission_data_file, 'r') as f:
        mission_data = json.load(f)

    mission_url = f"https://www.missionchief.com/missions/{mission_id}"
    driver.get(mission_url)

    try:
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, 'all')))
    except TimeoutException:
        remove_mission(mission_id, mission_data)
        return

    dispatch_tow_truck(crashed_cars, vehicle_dispatch_mapping, vehicle_types, driver, vehicles_file)
    dispatch_police_transport(prisoners, vehicle_dispatch_mapping, vehicle_types, driver, vehicles_file)
    dispatch_ems(patients, vehicle_dispatch_mapping, vehicle_types, driver)

    for requirement, required_count in mission_requirements.items():
        dispatched_count = 0
        vehicle_type_name = vehicle_dispatch_mapping.get(requirement)
        if not vehicle_type_name:
            print(f"No mapping found for requirement: {requirement}")
            continue

        if requirement == "personnel":
            required_count = calculate_vehicles_needed(required_count, 6)
            print(f"Calculated {required_count} vehicles needed for {required_count * 6} personnel")

        for vehicle_id, vehicle_info in vehicle_types.items():
            if vehicle_info['name'] == vehicle_type_name and dispatched_count < required_count:
                checkbox_id = f"vehicle_checkbox_{vehicle_id}"
                try:
                    checkbox = WebDriverWait(driver, 0).until(ec.element_to_be_clickable((By.ID, checkbox_id)))
                    try:
                        checkbox.click()
                        dispatched_count += 1
                        print(f"Dispatched {vehicle_type_name} with vehicle ID: {vehicle_id}")
                        if dispatched_count == required_count:
                            break
                    except ElementClickInterceptedException:
                        driver.execute_script("arguments[0].click();", checkbox)
                except (NoSuchElementException, TimeoutException):
                    print(f" {vehicle_type_name} already dispatched, skipping {vehicle_id}.")
                    continue
    try:
        dispatch_button = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.ID, 'alert_btn')))
        dispatch_button.click()
        print("Dispatched all selected vehicles.")
        time.sleep(5)
    except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
        print("Dispatch button not found or not clickable. Please rerun script")


def remove_mission(mission_id, mission_data):
    if mission_id in mission_data:
        del mission_data[mission_id]
        print(f"Mission completed but still in map... removing mission ID: {mission_id}")
