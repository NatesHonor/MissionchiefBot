from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


def gather_mission_data(driver, mission_numbers):
    missions_data = {}
    total_credits = 0

    for mission_number in mission_numbers:
        try:
            mission_url = f"https://www.missionchief.com/missions/{mission_number}"
            print(f"Opening mission URL: {mission_url}")
            driver.get(mission_url)
            try:
                driver.find_element(By.ID, f"mission_countdown_{mission_number}")
                print(f"Skipping mission {mission_number} because it's currently in progress!")
                continue
            except NoSuchElementException:
                pass

            mission_help_button = driver.find_element(By.ID, "mission_help")
            mission_help_button.click()
            table_rows = driver.find_elements(By.XPATH, '//table[@class="table table-striped"]/tbody/tr')

            mission_data = {"vehicles": {}, "personnel": {}, "patients": 0, "average_credits": 100, "crashed_cars": 0}
            for row in table_rows:
                columns = row.find_elements(By.TAG_NAME, 'td')
                requirement = columns[0].text.strip()
                value = columns[1].text.strip()

                if "Required" in requirement and "Station" not in requirement:
                    if "Personnel" in requirement:
                        personnel_requirements = value.split('\n')  # Split by line breaks
                        for personnel_requirement in personnel_requirements:
                            split_requirement = personnel_requirement.split('x')  # Split by 'x'
                            if len(split_requirement) == 2:
                                number_of_personnel, personnel = split_requirement
                                number_of_personnel = int(number_of_personnel.strip())
                                personnel = personnel.strip()
                                mission_data["personnel"][personnel] = number_of_personnel
                            else:
                                print(f"Unexpected personnel requirement format: {personnel_requirement}")
                    else:
                        vehicle = requirement.replace("Required ", "")
                        number_of_vehicles = int(''.join([char for char in value if char.isdigit()]))
                        mission_data["vehicles"][vehicle] = number_of_vehicles
                elif requirement == "Max. Patients":
                    mission_data["patients"] = int(value)
                elif requirement == "Average credits":
                    mission_data["average_credits"] = int(value)
                elif requirement == "Maximum amount of crashed cars":
                    mission_data["crashed_cars"] = int(value)

            missions_data[mission_number] = mission_data
            total_credits += mission_data["average_credits"]

        except NoSuchElementException:
            print(f"Mission help button not found for mission {mission_number}, skipping this mission.")
            continue

    print(f"Total missions data gathered: {missions_data}")
    print(f"Average Credits that you will earn: {total_credits}")

    return missions_data
