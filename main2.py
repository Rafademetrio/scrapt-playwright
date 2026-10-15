from playwright.sync_api import sync_playwright
from src.navegacao import ir_para_pedidos_com_data

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth_state.json")
    page = context.new_page()

    # Já entra logado direto na página de pedidos
    page.goto("http://35.237.167.233:8081/jahu/menu.faces")

    

    ir_para_pedidos_com_data(page, 1, 2026)
    print('pedidos')
    # Daqui em diante entra a lógica dos iframes e paginação
    page.pause()  # abre o Inspector pra você inspecionar e testar seletores

    browser.close()