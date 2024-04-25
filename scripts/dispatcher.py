import json
import math

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException


def calculate_vehicles_needed(personnel_count, group_size):
    return math.ceil(personnel_count / group_size)


def dispatch_recovery_vehicle(driver, vehicles_file, recovery_vehicle_type, crashed_cars):
    dispatched_recovery_vehicles = 0
    with open(vehicles_file, 'r') as f:
        vehicle_types = json.load(f)

    for vehicle_id, vehicle_info in vehicle_types.items():
        if vehicle_info['name'] == recovery_vehicle_type:
            checkbox_id = f"vehicle_checkbox_{vehicle_id}"
            try:
                checkbox = WebDriverWait(driver, 1).until(ec.element_to_be_clickable((By.ID, checkbox_id)))
                if not checkbox.is_selected():
                    checkbox.click()
                    dispatched_recovery_vehicles += 1
                    print(f"Dispatched {recovery_vehicle_type} with vehicle ID: {vehicle_id}")
                    if dispatched_recovery_vehicles >= crashed_cars:
                        break
            except (NoSuchElementException, ElementClickInterceptedException, TimeoutException):
                print(f"Checkbox not found or not clickable for {recovery_vehicle_type} with vehicle ID {vehicle_id}.")
                print(f"Vehicle probably dispatched... Continuing!")
                continue


def dispatch_vehicles(driver, mission_id, vehicles_file, mission_requirements, patients,
                      vehicle_dispatch_mapping, crashed_cars, mission_data_file):
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

    if crashed_cars > 0:
        if crashed_cars == 1:
            recovery_vehicle_type = vehicle_dispatch_mapping['Wreckers']
        elif crashed_cars == 2:
            recovery_vehicle_type = vehicle_dispatch_mapping['Flatbed Carriers']
        else:
            recovery_vehicle_type = [vehicle_dispatch_mapping['Wreckers'], vehicle_dispatch_mapping['Flatbed Carriers']]

        for vehicle_id, vehicle_info in vehicle_types.items():
            if isinstance(recovery_vehicle_type, list):
                for recovery_type in recovery_vehicle_type:
                    if vehicle_info['name'] == recovery_type:
                        dispatch_recovery_vehicle(driver, vehicles_file, recovery_vehicle_type, crashed_cars)
            else:
                if vehicle_info['name'] == recovery_vehicle_type:
                    dispatch_recovery_vehicle(driver, vehicles_file, recovery_vehicle_type, crashed_cars)

    if "personnel" in mission_data:
        for personnel, required_count in mission_data["personnel"].items():
            dispatched_count = 0
            required_count = int(required_count / 6)
            vehicle_type_name = "SWAT Armoured Vehicle" if personnel == "SWAT Personnel (In SWAT Vehicles)" \
                else vehicle_dispatch_mapping.get(personnel)

            if not vehicle_type_name:
                print(f"No mapping found for personnel: {personnel}")
                continue

            for vehicle_id, vehicle_info in vehicle_types.items():
                if vehicle_info['name'] == vehicle_type_name and dispatched_count < required_count:
                    checkbox_id = f"vehicle_checkbox_{vehicle_id}"
                    try:
                        checkbox = WebDriverWait(driver, 1).until(ec.element_to_be_clickable((By.ID, checkbox_id)))
                        if not checkbox.is_selected():
                            checkbox.click()
                            dispatched_count += 1
                            print(f"Dispatched {vehicle_type_name} with vehicle ID: {vehicle_id}")
                    except (NoSuchElementException, ElementClickInterceptedException, TimeoutException):
                        print(f"{vehicle_type_name}:{vehicle_id} Already dispatched, continuing...")
                        continue
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
                    try:
                        checkbox.click()
                    except ElementClickInterceptedException:
                        driver.execute_script("arguments[0].click();", checkbox)
                    dispatched_count += 1
                    print(f"Dispatched {vehicle_type_name} with vehicle ID: {vehicle_id}")
                    if dispatched_count == required_count:
                        break
                except (NoSuchElementException, TimeoutException):
                    print(f" {vehicle_type_name} already dispatched, skipping {vehicle_id}.")
                    continue

    try:
        dispatch_button = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.ID, 'alert_btn')))
        dispatch_button.click()
        print("Dispatched all selected vehicles.")
    except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
        print("Dispatch button not found or not clickable. Please rerun script")


def remove_mission(mission_id, mission_data):
    if mission_id in mission_data:
        del mission_data[mission_id]
        print(f"Mission completed but still in map... removing mission ID: {mission_id}")
