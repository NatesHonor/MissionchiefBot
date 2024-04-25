import json
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def dispatch_police_prisoner_vans(driver, mission_id, vehicle_data_file):
    with open(vehicle_data_file, 'r') as f:
        vehicle_data = json.load(f)

    mission_url = f"https://www.missionchief.com/missions/{mission_id}"
    driver.get(mission_url)

    try:
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, 'all')))
    except TimeoutException:
        print("The mission page did not load in time.")
        return

    try:
        prisoners_element = driver.find_element(By.ID, 'h2_prisoners')
        total_prisoners = int(prisoners_element.text.split()[0])
    except NoSuchElementException:
        print("Prisoners element not found.")
        return

    if total_prisoners > 1:
        transport_rows = driver.find_elements(By.XPATH, "//tr[contains(@id, 'vehicle_row')]")
        transport_dispatched = False
        for row in transport_rows:
            if 'Police Prisoner Van' in row.text:
                transport_dispatched = True
                break

        if not transport_dispatched:
            print("Dispatching Police Prisoner Van for multiple prisoners.")
            dispatch_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'Dispatch')]")
            for button in dispatch_buttons:
                if 'Police Prisoner Van' in button.get_attribute('href'):
                    button.click()
                    print("Police Prisoner Van dispatched.")
                    break
        else:
            print("Transport already dispatched. Finding the vehicle to initiate transport.")
            for row in transport_rows:
                transport_button = row.find_element(By.XPATH, ".//a[contains(text(), 'Transport')]")
                if transport_button:
                    transport_button.click()
                    print("Initiated transport for the dispatched Police Prisoner Van.")
                    break

    elif total_prisoners == 1:
        print("Selecting a random prison with available cells for 1 prisoner.")
        prison_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Available cells:')]")
        available_prisons = [link for link in prison_links if '0' not in link.text]
        if available_prisons:
            random.choice(available_prisons).click()
            print("Random prison selected for 1 prisoner.")
        else:
            print("No prisons with available cells found.")
