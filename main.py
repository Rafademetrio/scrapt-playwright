"""Ponto de entrada: reaproveita sessão se estiver válida, senão pede login."""
import os
from playwright.sync_api import sync_playwright

from src.config import AUTH_STATE, URL_MENU
from src.navegacao import ir_para_pedidos_com_data
from login import fazer_login_automatico, fazer_login_manual
from src.progresso import (
    carregar_progresso,
    salvar_progresso,
    extrair_indice_do_id,
)
from src.scrapers.pedidos import (
    extrair_pagina_atual,
    tem_proxima_pagina,
    avancar_pagina,
    ir_para_pagina_pedidos,
)
from src.scrapers.itens import (
    abrir_pedido,
    voltar_para_lista,
    extrair_todos_itens,
)
from src.scrapers.salvar import salvar_pedidos_csv, carregar_csv_para_dicts


def sessao_valida(page) -> bool:
    """Verifica se a sessão salva ainda está logada."""
    page.goto(URL_MENU)
    return "login" not in page.url.lower() and page.locator("#options").count() > 0



def processar_pedido(page, pedido: dict) -> None:
    """
    Abre o pedido, extrai os itens e volta pra lista.
    Em caso de erro, registra no dict mas não interrompe o fluxo.
    """
    print(f"\nAbrindo pedido {pedido['numero_pedido']}...")
    try:
        abrir_pedido(page, pedido["id_edit_link"])
        pedido["itens"] = extrair_todos_itens(page)
        print(f"  {len(pedido['itens'])} itens extraídos")
    except Exception as e:
        print(f"  ERRO ao processar pedido: {e}")
        pedido["itens"] = []
        pedido["erro"] = str(e)

    # Sempre tenta voltar pra lista
    try:
        voltar_para_lista(page)
    except Exception as e:
        print(f"  ERRO ao voltar pra lista: {e}")
        # Recuperação agressiva: navega de novo pra tela de pedidos
        print("  Tentando recuperação: navegando de novo para pedidos...")
        try:
            ir_para_pedidos_com_data(page, mes=1, ano=2026)
        except Exception as e2:
            print(f"  ERRO na recuperação: {e2}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        if os.path.exists(AUTH_STATE):
            context = browser.new_context(storage_state=AUTH_STATE)
        else:
            context = browser.new_context()

        page = context.new_page()

        if not sessao_valida(page):
            print("Sessão inválida ou inexistente. Tentando login automático...")
            
            try:
                fazer_login_automatico(page)
                print("Login automático bem-sucedido.")
            except Exception as e:
                print(f"⚠️  Login automático falhou: {e}")
                print("Caindo para o login manual...")
                fazer_login_manual(page)
            
            context.storage_state(path=AUTH_STATE)
            print(f"Sessão renovada em {AUTH_STATE}")
        else:
            print("Sessão reaproveitada do auth_state.json.")

        # Navega para a tela de pedidos com filtro de janeiro/2026
        ir_para_pedidos_com_data(page, mes=1, ano=2026)

        # Carrega progresso de execuções anteriores
        progresso = carregar_progresso()
        pagina_retomada = progresso["ultima_pagina"]
        indice_retomada = extrair_indice_do_id(progresso["ultimo_id_processado"])
        pedidos_ja_extraidos = set(progresso["pedidos_ja_extraidos"])

        print(f"\n=== Estado ===")
        print(f"Página de retomada: {pagina_retomada}")
        print(f"Último índice processado: {indice_retomada}")
        print(f"Pedidos já extraídos anteriormente: {len(pedidos_ja_extraidos)}")

        # Carrega pedidos já extraídos no CSV (pra não perder nada)
        todos_pedidos = []
        if pedidos_ja_extraidos:
            todos_pedidos = carregar_csv_para_dicts("pedidos_jan_2026.csv")
            print(f"CSV carregado com {len(todos_pedidos)} pedidos")

        # Pula direto para a página de retomada
        if pagina_retomada > 1:
            print(f"\nPulando direto para a página {pagina_retomada}...")
            ir_para_pagina_pedidos(page, pagina_retomada)

        pagina_atual = pagina_retomada
        primeira_pagina_processada = True

        while True:
            pedidos_pagina = extrair_pagina_atual(page)
            print(f"\n=== Página {pagina_atual} ({len(pedidos_pagina)} pedidos) ===")

            for pedido in pedidos_pagina:
                indice_pedido = extrair_indice_do_id(pedido["id_edit_link"])

                # Na primeira página após retomada, pula os já processados
                if primeira_pagina_processada and indice_pedido <= indice_retomada:
                    print(f"  {pedido['numero_pedido']} (índice {indice_pedido}) já processado, pulando")
                    continue

                # Segurança extra: pula por número de pedido
                if pedido["numero_pedido"] in pedidos_ja_extraidos:
                    print(f"  {pedido['numero_pedido']} já extraído, pulando")
                    continue

                # Processa o pedido
                processar_pedido(page, pedido)
                todos_pedidos.append(pedido)
                pedidos_ja_extraidos.add(pedido["numero_pedido"])

                # Salva progresso e CSV APÓS cada pedido
                progresso["ultima_pagina"] = pagina_atual
                progresso["ultimo_id_processado"] = pedido["id_edit_link"]
                progresso["pedidos_ja_extraidos"] = list(pedidos_ja_extraidos)
                salvar_progresso(progresso)
                salvar_pedidos_csv(todos_pedidos, "pedidos_jan_2026.csv")

            primeira_pagina_processada = False
            pagina_atual += 1

            if not tem_proxima_pagina(page):
                print("\nÚltima página processada.")
                break

            avancar_pagina(page)

        # Relatório final
        print(f"\n=== Extração completa ===")
        print(f"Total de pedidos: {len(todos_pedidos)}")

        falhas = [p for p in todos_pedidos if p.get("erro")]
        if falhas:
            print(f"\n⚠️  {len(falhas)} pedidos falharam:")
            for p in falhas:
                print(f"  - {p['numero_pedido']}: {p['erro']}")
            print("\nPara re-processar, apague esses pedidos do progresso.json")
            print("e remova-os de 'pedidos_ja_extraidos'.")

        salvar_pedidos_csv(todos_pedidos, "pedidos_jan_2026.csv")
        print(f"\nCSV final salvo em pedidos_jan_2026.csv")

        page.pause()
        browser.close()


if __name__ == "__main__":
    main()