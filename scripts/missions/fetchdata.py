from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def grab_average_credits(driver):
    try:
        average_credits_element = driver.find_element(By.XPATH, '//tr[td[text()="Average credits"]]/td[2]')
        average_credits = int(average_credits_element.text.strip())
        return average_credits
    except NoSuchElementException:
        return 0

def process_mission_data(driver, mission_data):
    mission_help_button = driver.find_element(By.ID, "mission_help")
    mission_help_button.click()
    table_rows = driver.find_elements(By.XPATH, '//table[@class="table table-striped"]/tbody/tr')

    for row in table_rows:
        columns = row.find_elements(By.TAG_NAME, 'td')
        requirement = columns[0].text.strip()
        value = columns[1].text.strip()

        if ("Required" in requirement and "Station" not in requirement
                and "Riot Police Extensions" not in requirement
                and "Fire Marshal's Offices" not in requirement
                and "Airport Extensions" not in requirement
                and "Foam Extensions" not in requirement
                and "Forestry Extensions" not in requirement
                and "Traffic Police Extensions" not in requirement
                and "Personnel" not in requirement
                and "Ambulances" not in requirement):
            if requirement == "Required Personnel Available":
                personnel_requirements = value.split('\n')
                for personnel_requirement in personnel_requirements:
                    number, personnel_type = personnel_requirement.split('x')
                    personnel_type = personnel_type.replace(number, '').strip()
                    if personnel_type == "Technical Rescuer":
                        pass
                    mission_data["personnel"][personnel_type] = int(number)
            else:
                vehicle = requirement.replace("Required ", "")
                number_of_vehicles = int(''.join([char for char in value if char.isdigit()]))
                if vehicle == "policehelicopter":
                    vehicle = "police helicopter"
                mission_data["vehicles"][vehicle] = number_of_vehicles
        elif requirement == "Max. Patients":
            num_patients = int(value)
            mission_data["vehicles"]["Ambulances"] = num_patients
            if num_patients >= 10:
                mission_data["vehicles"]["EMS Chief"] = 1
            if num_patients >= 15:
                mission_data["vehicles"]["EMS Mobile Command Unit"] = 1
        elif requirement == "Maximum Number of Prisoners":
            mission_data["prisoners"] = int(value)
        elif requirement == "Maximum amount of crashed cars":
            mission_data["crashed_cars"] = int(value)
        mission_data["average_credits"] = grab_average_credits(driver)
    return mission_data
