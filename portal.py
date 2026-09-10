import re
import time

from selenium import webdriver
from selenium.common.exceptions import (
    NoAlertPresentException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def create_driver():

    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(options=options)


def wait_for(driver, timeout=15):
    return WebDriverWait(driver, timeout)


def find_math_captcha(driver):
    """
    Busca o container do CAPTCHA matemático visível na página.
    """

    try:
        elements = driver.find_elements(By.XPATH, "//*")
    except Exception:
        return None

    for element in elements:
        try:
            if not element.is_displayed():
                continue
        except Exception:
            continue

        text = (element.text or "").strip()

        if not text:
            continue

        if re.search(r"\d+\s*[+\-*/x÷]\s*\d+", text, re.IGNORECASE):
            return element

    return None


def extract_math_answer(captcha_text):
    """
    Extrai a operação matemática e retorna o resultado numérico.
    """

    match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*([+\-*/x÷])\s*(\d+(?:[.,]\d+)?)",
        captcha_text,
        re.IGNORECASE,
    )

    if match is None:
        raise ValueError(
            f"Não foi possível extrair uma expressão matemática de: {captcha_text!r}"
        )

    left = float(match.group(1).replace(",", "."))
    right = float(match.group(3).replace(",", "."))
    operator = match.group(2).lower()

    if operator == "x":
        operator = "*"
    elif operator == "÷":
        operator = "/"

    operation = f"{left}{operator}{right}"
    answer = eval(operation, {"__builtins__": {}}, {})

    if float(answer).is_integer():
        return int(answer)

    return answer


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


# Alertas, popup e captcha

def dismiss_browser_alert(driver):
    #função pra aceitar alertas nativos

    try:
        alert = driver.switch_to.alert
        alert.accept()
        return True
    except NoAlertPresentException:
        return False

def dismiss_popup(driver):
    

    close_locators = [
        (By.XPATH, '//button[normalize-space()="Fechar"]'),
        (By.XPATH, '//button[normalize-space()="OK"]'),
        (By.XPATH, '//button[normalize-space()="Entendi"]'),
        (By.CSS_SELECTOR, 'button[aria-label="Fechar"]'),
        (By.CSS_SELECTOR, ".modal button.close"),
    ]

    for locator in close_locators:
        elements = driver.find_elements(*locator)

        for element in elements:
            try:
                if not element.is_displayed():
                    continue

                if not element.is_enabled():
                    continue

                element.click()

                try:
                    wait_for(driver, 3).until(
                        EC.invisibility_of_element(element)
                    )
                except TimeoutException:
                    pass

                return True

            except StaleElementReferenceException:
                return True

    return False


def find_captcha_input(driver, container):
    input_locators = [
        (By.CSS_SELECTOR, 'input[name*="captcha" i]'),
        (By.CSS_SELECTOR, 'input[id*="captcha" i]'),
        (
            By.CSS_SELECTOR,
            'input[placeholder*="resposta" i]',
        ),
        (By.CSS_SELECTOR, 'input[type="number"]'),
    ]

    for locator in input_locators:
        elements = container.find_elements(*locator)

        for element in elements:
            try:
                if element.is_displayed():
                    return element
            except StaleElementReferenceException:
                continue

    return find_first_visible(
        driver,
        input_locators,
        timeout=3,
    )


def find_captcha_button(driver, container):
    button_locators = [
        (By.XPATH, './/button[normalize-space()="Validar"]'),
        (By.XPATH, './/button[normalize-space()="Confirmar"]'),
        (By.XPATH, './/button[normalize-space()="Continuar"]'),
        (By.XPATH, './/button[normalize-space()="Enviar"]'),
        (By.XPATH, './/button[normalize-space()="Responder"]'),
    ]

    for locator in button_locators:
        elements = container.find_elements(*locator)

        for element in elements:
            try:
                if element.is_displayed() and element.is_enabled():
                    return element
            except StaleElementReferenceException:
                continue

    page_button_locators = [
        (By.XPATH, '//button[normalize-space()="Validar"]'),
        (By.XPATH, '//button[normalize-space()="Confirmar"]'),
        (By.XPATH, '//button[normalize-space()="Continuar"]'),
        (By.XPATH, '//button[normalize-space()="Responder"]'),
    ]

    try:
        return find_first_visible(
            driver,
            page_button_locators,
            timeout=2,
        )
    except TimeoutException:
        return None


def solve_math_captcha(driver):
    container = find_math_captcha(driver)

    if container is None:
        return False

    captcha_text = container.text.strip()
    answer = extract_math_answer(captcha_text)

    answer_input = find_captcha_input(
        driver,
        container,
    )

    replace_input(answer_input, answer)

    confirm_button = find_captcha_button(
        driver,
        container,
    )

    if confirm_button:
        confirm_button.click()
    else:
        answer_input.send_keys(Keys.ENTER)

    print(
        f"CAPTCHA resolvido: "
        f"{captcha_text!r} = {answer}"
    )

    return True


def handle_math_captcha(driver, max_attempts=3):
    #resolve o captcha se visivel

    for attempt in range(1, max_attempts + 1):
        container = find_math_captcha(driver)

        if container is None:
            return False

        driver.save_screenshot(
            f"captcha-tentativa-{attempt}.png"
        )

        try:
            solve_math_captcha(driver)

            deadline = time.monotonic() + 5

            while time.monotonic() < deadline:
                if find_math_captcha(driver) is None:
                    return True

                time.sleep(0.2)

        except (
            NoSuchElementException,
            StaleElementReferenceException,
            TimeoutException,
            ValueError,
        ) as error:
            print(
                f"Falha no CAPTCHA, tentativa "
                f"{attempt}: {error}"
            )

    raise RuntimeError(
        "Não foi possível resolver o CAPTCHA matemático."
    )

