from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Troque pela URL de login do seu sistema
    page.goto("http://35.237.167.233:8081/jahu/menu.faces")


    print("Faça o login manualmente no navegador que abriu.")
    print("Quando estiver logado, volte aqui e pressione ENTER.")
    input()

    # Salva cookies + localStorage da sessão autenticada
    context.storage_state(path="auth_state.json")
    print("Sessão salva em auth_state.json")

    browser.close()