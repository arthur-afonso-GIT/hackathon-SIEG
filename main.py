from config import BASE_URL, validate_config
from portal import (
    create_driver,
    dismiss_popup,
    handle_math_captcha,
)


def main():
    validate_config()
    driver = create_driver()

    try:
        print("Abrindo o portal...")
        driver.get(BASE_URL)

        dismiss_popup(driver)
        handle_math_captcha(driver)

        print("Portal aberto com sucesso.")
        print(f"URL atual: {driver.current_url}")

        input(
            "Faça o login manualmente e pressione Enter "
            "quando estiver na página /app..."
        )

        dismiss_popup(driver)
        handle_math_captcha(driver)

        if "/app" not in driver.current_url:
            raise RuntimeError(
                "O navegador não chegou à página /app."
            )

        print("Página /app confirmada.")
        input("Pressione Enter para encerrar...")

    except Exception as error:
        print(f"Erro durante a execução: {error}")
        driver.save_screenshot("erro.png")

        with open(
            "erro.html",
            "w",
            encoding="utf-8",
        ) as file:
            file.write(driver.page_source)

        raise

    finally:
        driver.quit()
        print("Navegador encerrado.")


if __name__ == "__main__":
    main()