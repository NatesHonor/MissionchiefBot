import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def transport_needed(driver, mission_id):
    try:
        transport_needed_alert = driver.find_element(By.XPATH, "//*[contains(text(), 'Transport is needed!')]")
        if transport_needed_alert:
            logging.info(f"Skipping mission {mission_id} because it has a transport request.")
            return True
    except NoSuchElementException:
        pass
    return False


def prisoner_needed(driver, mission_id):
    try:
        prisoner_needed_alert = driver.find_element(By.XPATH, "//*[contains(text(), 'Prisoners must be transported.')]")
        if prisoner_needed_alert:
            logging.warning(f"Skipping mission {mission_id} because it has a prisoner request.")
            logging.info(f"Handling prisoner request on mission {mission_id}.")
            click_non_danger_buttons_under_prisoner_element(driver)
            return True
    except NoSuchElementException:
        pass
    return False


def click_non_danger_buttons_under_prisoner_element(driver):
    try:
        prisoner_element = driver.find_element(By.CLASS_NAME, 'vehicle_prisoner_select')
        prisoner_buttons = prisoner_element.find_elements(By.TAG_NAME, 'a')
        for button in prisoner_buttons:
            button_class = button.get_attribute('class')
            if 'btn-danger' not in button_class:
                button.click()
                logging.info(f"Clicked non-danger button under prisoner element.")
    except NoSuchElementException:
        logging.info("Prisoner element not found on the page.")


def wait_for_element(driver, selector, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(ec.presence_of_element_located((By.ID, selector)))
    except TimeoutException:
        return False
    return True
