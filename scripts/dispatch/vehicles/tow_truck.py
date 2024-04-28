import json

from selenium.common import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import sys

from colorama import init
init(strip=not sys.stdout.isatty()) # strip colors if stdout is redirected
from termcolor import cprint
from pyfiglet import figlet_format

cprint(figlet_format('v 1.0.3', font='big'),
       'yellow', 'on_red', attrs=['bold'])


def dispatch_tow_truck(crashed_cars, vehicle_dispatch_mapping, vehicle_types, driver, vehicles_file):
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
                    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                    driver.execute_script("arguments[0].click();", checkbox)
                    print(f"Vehicle {recovery_vehicle_type}:{vehicle_id} selected.")
                    dispatched_recovery_vehicles += 1
                    if dispatched_recovery_vehicles >= crashed_cars:
                        break
            except (NoSuchElementException, ElementClickInterceptedException, TimeoutException):
                print(f"Checkbox not found or not clickable for {recovery_vehicle_type} with vehicle ID {vehicle_id}.")
                print(f"Vehicle probably dispatched... Continuing!")
                continue
