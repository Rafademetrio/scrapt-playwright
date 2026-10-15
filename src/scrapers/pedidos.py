"""Extração de dados da lista de pedidos."""
from playwright.sync_api import Page, FrameLocator

from ..config import (
    IFRAME_CONTENT,
    SELETOR_TABELA_PEDIDOS,
    SELETOR_PAGINA_ATIVA,
    SELETOR_PROXIMA_PAGINA,
)


def _get_frame(page: Page) -> FrameLocator:
    return page.locator(IFRAME_CONTENT).content_frame


def extrair_pagina_atual(page: Page) -> list[dict]:
    """Extrai todos os pedidos visíveis na página atual da tabela."""
    frame = _get_frame(page)
    frame.locator(SELETOR_TABELA_PEDIDOS).wait_for(state="visible")

    pedidos = []
    #linhas = frame.locator(f"{SELETOR_TABELA_PEDIDOS} tbody tr.wmw-grid-tr")
    linhas = frame.locator('//*[@id="formContent:pedidoTableTable"]//tr[starts-with(@class, "wmw-grid-tr")]')
    total = linhas.count()

    for i in range(total):
        celulas = linhas.nth(i).locator("td")
        pedido = {
            "indice_linha": i,
            "numero_pedido": celulas.nth(1).inner_text().strip(),
            "cod_cliente": celulas.nth(2).inner_text().strip(),
            "razao_social": celulas.nth(3).inner_text().strip(),
            "representante": celulas.nth(4).inner_text().strip(),
            "data_emissao": celulas.nth(5).inner_text().strip(),
            "hora_emissao": celulas.nth(6).inner_text().strip(),
            "status": celulas.nth(7).inner_text().strip(),
            "origem": celulas.nth(8).inner_text().strip(),
            "valor_total": celulas.nth(9).inner_text().strip(),
        }
        pedidos.append(pedido)

    return pedidos


def tem_proxima_pagina(page: Page) -> bool:
    """Verifica se existe próxima página habilitada."""
    frame = _get_frame(page)
    botao = frame.locator(SELETOR_PROXIMA_PAGINA)
    if botao.count() == 0:
        return False
    classes = botao.get_attribute("class") or ""
    return "ui-state-disabled" not in classes


def avancar_pagina(page: Page) -> None:
    """Avança para a próxima página e espera a mudança."""
    frame = _get_frame(page)
    pagina_antes = frame.locator(SELETOR_PAGINA_ATIVA).inner_text()
    frame.locator(SELETOR_PROXIMA_PAGINA).click()
    frame.locator(SELETOR_PAGINA_ATIVA).filter(
        has_not_text=pagina_antes
    ).wait_for(state="visible", timeout=10_000)