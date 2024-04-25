from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import configparser


def login():
    config = configparser.ConfigParser()
    config.read('config.ini')
    username = config['credentials']['username']
    password = config['credentials']['password']

    headless = config.getboolean('client', 'headless', fallback=False)

    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://www.missionchief.com/users/sign_in")

    login_field = driver.find_element(By.ID, "user_email")
    password_field = driver.find_element(By.ID, "user_password")

    login_field.send_keys(username)
    password_field.send_keys(password)

    sign_in_button = driver.find_element(By.NAME, "commit")
    sign_in_button.click()

    return driver
