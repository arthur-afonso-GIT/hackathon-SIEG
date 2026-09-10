import time
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium import webdriver

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(options=options)


def wait_for(driver, timeout=15):
    return WebDriverWait(driver, timeout)

def find_first_visible(driver, locators, timeout=10):

    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        for locator in locators:
            elements = driver.find_elements(*locator)

            for element in elements:
                try:
                    if element.is_displayed():
                        return element
                except StaleElementReferenceException:
                    continue

        time.sleep(0.2)

    raise TimeoutException(
        f"Nenhum elemento visível encontrado: {locators}"
    )

def replace_input(element, value):

    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(str(value))