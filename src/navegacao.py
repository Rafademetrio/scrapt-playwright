from datetime import date, timedelta

from .utils import preencher_data

from playwright.sync_api import Page

def ir_para_pedidos_com_data(page: Page, mes: int, ano: int, status: str = "5") -> None:
    """
    Navega até a tela de pedidos e aplica os filtros.
    
    Args:
        mes: mês de emissão (1-12)
        ano: ano de emissão (ex: 2026)
        status: código do status. "5" = Faturado (padrão), "" = todos
    """
    menu_principal = page.get_by_role("link", name="Pedidos").first
    menu_principal.hover()
    submenu_pedidos = page.get_by_role("menuitem", name="Pedidos", exact=True).get_by_role("link")
    submenu_pedidos.wait_for(state="visible", timeout=5000)
    submenu_pedidos.click()

    frame = page.locator("#contentFrame").content_frame

    # 2. Data inicial = primeiro dia do mês
    data_inicial = f"01/{mes:02d}/{ano}"
    preencher_data(frame, "#formConsulta\\:dtEmissaoInicialFilter", data_inicial)

    # 3. Data final = último dia do mês
    if mes == 12:
        proximo_mes, proximo_ano = 1, ano + 1
    else:
        proximo_mes, proximo_ano = mes + 1, ano
    # Truque: pega o último dia do mês subtraindo 1 dia do próximo mês
    
    ultimo_dia = date(proximo_ano, proximo_mes, 1) - timedelta(days=1)
    data_final = ultimo_dia.strftime("%d/%m/%Y")
    preencher_data(frame, "#formConsulta\\:dtEmissaoFinalFilter", data_final)    

    # 4. Seleciona o status
    frame.locator("#formConsulta\\:cdStatusPedido").select_option(status)

    # 5. Pesquisa
    frame.get_by_role("button", name="Pesquisar").click()

    # 6. Espera a tabela de resultados carregar
    frame.locator("#formContent\\:pedidoTableTable").wait_for(state="visible")