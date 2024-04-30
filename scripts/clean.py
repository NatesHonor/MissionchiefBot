from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def mission_cleaner(driver, mission_numbers):
    for mission_number in mission_numbers:
        mission_url = f"https://www.missionchief.com/missions/{mission_number}"
        driver.get(mission_url)

        patient_elements = driver.find_elements(By.CLASS_NAME, "mission_patient")
        num_patients = len(patient_elements)
        ambulances = driver.find_elements(By.XPATH, "//td/small[contains(text(), '(ALS Ambulance)')]")

        while len(ambulances) > num_patients:
            ambulance = ambulances[-1]
            try:
                cancel_button = ambulance.find_element(
                    By.XPATH, ".//div[@class='btn-group']/a[contains(@class, 'btn-backalarm-ajax')]")
                cancel_button.click()
            except NoSuchElementException:
                print(f"No cancel button found for ambulance in mission {mission_number}. Skipping this ambulance.")
                continue

            ambulances.pop()

        if len(ambulances) == 0 and num_patients > 0:
            print(f"No ambulances found for mission {mission_number} with {num_patients} patient(s). Skipping this mission.")
            continue

        assert len(ambulances) == num_patients
