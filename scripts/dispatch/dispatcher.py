import configparser
import logging
import math

from scripts.dispatch.vehicles.tow_truck import dispatch_tow_truck
from scripts.dispatch.vehicles.prisoner_transport import dispatch_police_transport
from scripts.dispatch.personnel.personnel import dispatch_personnel
from scripts.dispatch.functions.select import select_vehicles
from scripts.dispatch.functions.check import transport_needed, prisoner_needed, wait_for_element, \
    click_and_wait_for_refresh
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException

logging.basicConfig(level=logging.INFO)

config = configparser.ConfigParser()
config.read('config.ini')

def dispatch_vehicles(driver, mission_id, vehicle_pool, mission_requirements,
                      vehicle_dispatch_mapping, crashed_cars, mission_data_file, prisoners, personnel_dispatch_mapping):
    mission_url = f"https://www.missionchief.com/missions/{mission_id}"
    driver.get(mission_url)
    try:
        click_and_wait_for_refresh(driver, '.btn.btn-xs.btn-warning.missing_vehicles_load.btn-block')
    except TimeoutException:
        logging.error("Timeout while waiting for 'Load missing' button.")

    transport_needed(driver, mission_id)
    prisoner_needed(driver, mission_id)
    wait_for_element(driver, 'all')

    dispatch_personnel(driver, mission_id, vehicle_pool, mission_data_file, personnel_dispatch_mapping)
    dispatch_tow_truck(crashed_cars, vehicle_dispatch_mapping, vehicle_pool, driver)
    dispatch_police_transport(prisoners, vehicle_dispatch_mapping, vehicle_pool, driver)

    for requirement, required_count in mission_requirements.items():
        requirement = requirement.lower()
        words = requirement.split()
        processed_words = [word[:-1] if word.endswith('s') else word for word in words]
        requirement = ' '.join(processed_words)
        vehicle_type_names = None

        if requirement == "ambulance" and required_count >= 7:
            logging.info(f"Dispatching Mass Casualty Unit instead of 7 ambulances for mission {mission_id}.")
            vehicle_type_names = vehicle_dispatch_mapping.get("mass casualty unit")
            if vehicle_type_names:
                dispatched_count = select_vehicles(driver, vehicle_type_names, "mass casualty unit", required_count)
                required_count -= dispatched_count
                if required_count <= 0:
                    continue

        if (requirement == "k-9 unit" or requirement == "k-9 unit") and required_count > 2:
            logging.info(f"Dispatching K-9 Carrier instead of K-9 Unit for mission {mission_id}.")
            vehicle_type_names = vehicle_dispatch_mapping.get("k-9 carrier")
            required_count = 1
        elif requirement == "arff unit" or requirement == "arff units" and required_count >= 2:
            temp_count = math.ceil(required_count / 2)
            required_count = temp_count
        elif requirement == "swat personnel (in swat vehicles)":
            temp_count = math.ceil(required_count / 6)
            required_count = temp_count
        else:
            vehicle_type_names = vehicle_dispatch_mapping.get(requirement)

        if not vehicle_type_names:
            logging.info(f"No mapping found for requirement: {requirement}. Trying the second mapping...")
            vehicle_type_names = vehicle_dispatch_mapping.get(requirement + "_2")

        if not vehicle_type_names:
            logging.info(f"No mapping found for requirement: {requirement}")
            continue

        if isinstance(vehicle_type_names, list):
            vehicle_types = vehicle_type_names
        else:
            vehicle_types = [vehicle_type_names]
        for vehicle_type in vehicle_types:
            matching_vehicles = {vehicle_id: info for vehicle_id, info in vehicle_pool.copy().items() if
                                 info['name'] == vehicle_type}

            vehicle_ids = list(matching_vehicles.keys())
            dispatched_count = select_vehicles(driver, vehicle_ids, vehicle_type, required_count)
            logging.info(f"Dispatched {dispatched_count} out of {required_count} for {vehicle_type}")
            if dispatched_count >= required_count:
                break

    try:
        if config.get('dispatches', 'dispatch_type') == "alliance":
            dispatch_button = WebDriverWait(driver, 3).until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-success.alert_next_alliance')))
        else:
            dispatch_button = WebDriverWait(driver, 3).until(ec.element_to_be_clickable((By.ID, 'alert_btn')))
        driver.execute_script("arguments[0].scrollIntoView();", dispatch_button)
        driver.execute_script("arguments[0].click();", dispatch_button)
        logging.info("Dispatching all selected vehicles.")
    except TimeoutException:
        logging.error("Dispatch failed on first attempt. Retrying...  (Attempt 1/2)")
        try:
            dispatch_button = WebDriverWait(driver, 3).until(ec.element_to_be_clickable((By.ID, 'alert_btn')))
            driver.execute_script("arguments[0].scrollIntoView();", dispatch_button)
            driver.execute_script("arguments[0].click();", dispatch_button)
            logging.info("Dispatched all selected vehicles. (Attempt 2/2)")
        except TimeoutException:
            logging.error("Dispatching failed, giving up...")
    except NoSuchElementException as e:
        logging.info(f"Could not find dispatch button for mission {mission_id} due to it not being found. {e}")
