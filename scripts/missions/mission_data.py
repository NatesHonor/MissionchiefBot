from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from scripts.missions.fetchdata import process_mission_data


def gather_mission_data(driver, mission_numbers):
    missions_data = {}
    total_missions = len(mission_numbers)

    for index, mission_number in enumerate(mission_numbers, start=1):
        try:
            mission_url = f"https://www.missionchief.com/missions/{mission_number}"
            print(f"Opening mission {index}/{total_missions}")
            driver.get(mission_url)
            try:
                driver.find_element(By.ID, f"mission_countdown_{mission_number}")
                print(f"Skipping mission {mission_number} because it's currently in progress!")
                continue
            except NoSuchElementException:
                pass

            images = driver.find_elements(By.TAG_NAME, "img")
            for img in images:
                if "gelb" in img.get_attribute("src"):
                    print(f"Mission {mission_number} currently has units dispatched to it, skipping!")
                    break
            else:
                mission_title = driver.find_element(By.ID, "mission_general_info").get_attribute("data-mission-title")

                mission_data = {"title": mission_title, "average_credits": 100, "vehicles": {}, "personnel": {},
                                "patients": 0, "prisoners": 0, "crashed_cars": 0}

                missing_personnel = driver.find_elements(By.XPATH, '//div[@data-requirement-type="personnel"]')
                missing_vehicles = driver.find_elements(By.XPATH, '//div[@data-requirement-type="vehicles"]')
                patient_elements = driver.find_elements(By.CLASS_NAME, "mission_patient")
                alerts = driver.find_elements(By.CLASS_NAME, "alert-danger")
                ems_chief_dispatched = False
                exit_out_of_loop = False
                for alert in alerts:
                    if "We need: EMS Chief" in alert.text and not ems_chief_dispatched:
                        mission_data["vehicles"]["EMS Chief"] = mission_data["vehicles"].get("EMS Chief", 1)
                        print(f"Dispatching an EMS Chief for mission {mission_number}!")
                        ems_chief_dispatched = True
                        break
                    elif "We need: Ambulance" in alert.text:
                        mission_data["vehicles"]["Ambulance"] = mission_data["vehicles"].get("Ambulance", 0) + 1
                        print(f"Skipping mission {mission_number} because it requires an ambulance!")
                        break

                for patient in patient_elements:
                    try:
                        missing_text = patient.find_element(By.XPATH, ".//div[@class='alert alert-danger']").text
                        if "Ambulance" in missing_text:
                            mission_data["vehicles"]["Ambulance"] = mission_data["vehicles"].get("Ambulance", 0) + 1
                            exit_out_of_loop = True
                            break
                        elif "EMS Chief" in missing_text:
                            mission_data["vehicles"]["EMS Chief"] = mission_data["vehicles"].get("EMS Chief", 1)
                            exit_out_of_loop = True
                            break
                    except NoSuchElementException:
                        continue

                if missing_personnel or missing_vehicles:
                    try:
                        for personnel_element in missing_personnel:
                            requirement = personnel_element.text.strip().replace("Missing Personnel: ", "")
                            personnels = requirement.split(", ")
                            for personnel in personnels:
                                number, personnel_type = personnel.split(" ", 1)
                                number = number.split("x")[0]
                                number_of_personnel = int(number)
                                mission_data["personnel"][personnel_type] = number_of_personnel
                        for vehicle_element in missing_vehicles:
                            requirement = vehicle_element.text.strip().replace("Missing Vehicles: ", "")
                            vehicles = requirement.split(", ")
                            for vehicle in vehicles:
                                number, vehicle_type = vehicle.split(" ", 1)
                                number_of_vehicles = int(number)
                                mission_data["vehicles"][vehicle_type] = number_of_vehicles
                    except NoSuchElementException:
                        break
                else:
                    if not exit_out_of_loop:
                        missions_data[mission_number] = process_mission_data(driver, mission_data)
        except NoSuchElementException:
            print(f"Mission help button not found for mission {mission_number}, skipping this mission.")
            continue

    print(f"Total missions data gathered: {missions_data}")

    return missions_data
