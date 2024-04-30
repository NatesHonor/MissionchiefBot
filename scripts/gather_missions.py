import time
from selenium.webdriver.common.by import By


def total_number_of_missions(driver):
    driver.get("https://www.missionchief.com/")
    time.sleep(1)
    css_selector = 'div.mission_panel_red'
    div_elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
    print(f"# of Missions found: {len(div_elements)}")

    time.sleep(3)
    mission_numbers = []
    for div in div_elements:
        href = div.find_element(By.TAG_NAME, 'a').get_attribute("href")
        mission_number = href.split("/")[-1].split("?")[0]
        mission_numbers.append(mission_number)
        print(f"All found Mission Numbers: {mission_number}")
    return mission_numbers
