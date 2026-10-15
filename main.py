"""Ponto de entrada: reaproveita sessão se estiver válida, senão pede login."""
import os
from playwright.sync_api import sync_playwright

from src.config import AUTH_STATE, URL_MENU
from src.navegacao import ir_para_pedidos_com_data
from src.scrapers.pedidos import extrair_pagina_atual


def sessao_valida(page) -> bool:
    """Verifica se a sessão salva ainda está logada."""
    page.goto(URL_MENU)
    # Se a URL redirecionar para tela de login, não está logado
    # Ajuste o critério conforme o comportamento real do sistema
    return "login" not in page.url.lower() and page.locator("#options").count() > 0


def fazer_login(page) -> None:
    """Espera o usuário logar manualmente."""
    if "login" not in page.url.lower():
        page.goto(URL_MENU)
    print("Sessão expirada. Faça o login manualmente no navegador.")
    print("Quando estiver logado, pressione ENTER aqui.")
    input()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        # Se o auth_state.json existe, tenta reaproveitar
        if os.path.exists(AUTH_STATE):
            context = browser.new_context(storage_state=AUTH_STATE)
        else:
            context = browser.new_context()

        page = context.new_page()

        if not sessao_valida(page):
            fazer_login(page)
            context.storage_state(path=AUTH_STATE)
            print(f"Sessão renovada em {AUTH_STATE}")

        # Automação
        ir_para_pedidos_com_data(page, mes=1, ano=2026)
        
        frame_loc = page.locator("#contentFrame").content_frame
        frame = page.frame(url=lambda u: "listRelPedido" in u)
        print("URL:", frame.url if frame else "frame não encontrado")
        print("Tabela count:", frame_loc.locator("#formContent\\:pedidoTableTable").count())
        print("Linhas count:", frame_loc.locator("#formContent\\:pedidoTableTable tbody tr.wmw-grid-tr").count())
        print("Primeiros 2000 chars:", frame.content()[:2000] if frame else "N/A")

        pedidos = extrair_pagina_atual(page)
        print(f"Total na página: {len(pedidos)}")
        for p in pedidos[:3]:  # mostra os 3 primeiros
            print(p)
        page.pause()
        browser.close()


if __name__ == "__main__":
    main()