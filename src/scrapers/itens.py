"""Extração de itens do pedido."""
from playwright.sync_api import Page, FrameLocator

from ..config import IFRAME_CONTENT




# Seletores da tela de itens
SELETOR_TABELA_ITENS = "[id='pedidoForm:j_idt747Table']"
SELETOR_LINHAS_ITENS = f"{SELETOR_TABELA_ITENS} tbody tr.wmw-grid-tr"
SELETOR_PAGINA_ATIVA_ITENS = "[id='pedidoForm:j_idt747Pager'] .wmw-gp-activep"
SELETOR_PROXIMA_PAGINA_ITENS = "[id='pedidoForm:j_idt747Pagernext']"
SELETOR_BOTAO_PRELIMINAR = "[id='pedidoForm:btStepItemPedido']"
SELETOR_LINK_LISTA_PEDIDOS = "a:has-text('Lista de Pedido')"


def _get_frame(page: Page) -> FrameLocator:
    return page.locator(IFRAME_CONTENT).content_frame


def abrir_pedido(page: Page, id_edit_link: str) -> None:
    """
    Abre o pedido da linha especificada e garante que está na tela de itens.
    Lida com a tela preliminar que só aparece no primeiro pedido da sessão.
    """
    frame = _get_frame(page)
    frame.locator(f"[id='{id_edit_link}']").click()

    try:
        botao_preliminar = frame.locator(SELETOR_BOTAO_PRELIMINAR)
        botao_preliminar.wait_for(state="visible", timeout=8_000)
        print("  Tela preliminar detectada, clicando em 'Consultar Item'...")
        
        botao_preliminar.click(force=True)
        
        page.wait_for_timeout(1000) 
        
        if botao_preliminar.is_visible():
            botao_preliminar.press("Enter")
            page.wait_for_timeout(1000)

    except Exception:
        # Não apareceu tela preliminar — foi direto para a lista de itens
        pass

    try:
        frame.locator(SELETOR_LINHAS_ITENS).first.wait_for(
            state="attached", timeout=15_000
        )
    except Exception as e:
        print(f"  AVISO: Não conseguiu carregar a tabela de itens após a preliminar. Erro: {e}")
        if frame.locator(SELETOR_BOTAO_PRELIMINAR).is_visible():
            frame.locator(SELETOR_BOTAO_PRELIMINAR).click(force=True)
            frame.locator(SELETOR_LINHAS_ITENS).first.wait_for(
                state="attached", timeout=15_000
            )

def extrair_pagina_itens(page: Page) -> list[dict]:
    """Extrai todos os itens visíveis na página atual da tabela."""
    frame = _get_frame(page)
    frame.locator(SELETOR_LINHAS_ITENS).first.wait_for(state="attached", timeout=15_000)

    linhas = frame.locator(SELETOR_LINHAS_ITENS)
    total = linhas.count()

    itens = []
    for i in range(total):
        celulas = linhas.nth(i).locator("td")
        item = {
            "codigo": celulas.nth(0).inner_text().strip(),
            "descricao": celulas.nth(1).inner_text().strip(),
            "qtd": celulas.nth(2).inner_text().strip(),
            "valor_base": celulas.nth(3).inner_text().strip(),
            "pct_desconto": celulas.nth(4).inner_text().strip(),
            "liquido": celulas.nth(5).inner_text().strip(),
            "valor_com_tributos": celulas.nth(6).inner_text().strip(),
            "valor_com_st": celulas.nth(7).inner_text().strip(),
            "total_st": celulas.nth(8).inner_text().strip(),
            "total": celulas.nth(9).inner_text().strip(),
            "total_com_st": celulas.nth(10).inner_text().strip(),
            "total_com_tributos": celulas.nth(11).inner_text().strip(),
        }
        itens.append(item)

    return itens


def tem_proxima_pagina_itens(page: Page) -> bool:
    """Verifica se existe próxima página habilitada na tabela de itens."""
    frame = _get_frame(page)
    botao = frame.locator(SELETOR_PROXIMA_PAGINA_ITENS)
    if botao.count() == 0:
        return False
    classes = botao.get_attribute("class") or ""
    return "ui-state-disabled" not in classes


def avancar_pagina_itens(page: Page) -> None:
    """Avança para a próxima página de itens e espera a mudança."""
    frame = _get_frame(page)
    pagina_antes = frame.locator(SELETOR_PAGINA_ATIVA_ITENS).inner_text()
    frame.locator(SELETOR_PROXIMA_PAGINA_ITENS).click()
    frame.locator(SELETOR_PAGINA_ATIVA_ITENS).filter(
        has_not_text=pagina_antes
    ).wait_for(state="visible", timeout=10_000)


def extrair_todos_itens(page: Page) -> list[dict]:
    """Extrai todos os itens do pedido, paginando se necessário."""
    todos = []
    while True:
        todos.extend(extrair_pagina_itens(page))
        if not tem_proxima_pagina_itens(page):
            break
        avancar_pagina_itens(page)
    return todos


def voltar_para_lista(page: Page) -> None:
    """
    Volta da tela de itens/pedido para a lista de pedidos,
    usando o link direto 'Lista de Pedido'.
    """
    frame = _get_frame(page)
    frame.locator(SELETOR_LINK_LISTA_PEDIDOS).click()

    # Espera a tabela de pedidos reaparecer E popular
    frame.locator("[id='formContent:pedidoTableTable']").wait_for(
        state="attached", timeout=15_000
    )
    # Espera as linhas aparecerem
    frame.locator(
        "[id='formContent:pedidoTableTable'] tbody tr.wmw-grid-tr"
    ).first.wait_for(state="attached", timeout=15_000)