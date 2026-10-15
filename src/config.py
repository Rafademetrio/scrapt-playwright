"""Constantes e configurações centralizadas do projeto."""
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_STATE = str(BASE_DIR / "auth_state.json")

# URLs
URL_MENU = "http://35.237.167.233:8081/jahu/menu.faces"

# Seletores do menu principal (fora do iframe)
MENU_PEDIDOS = "Pedidos"
MENU_ITEM_PEDIDOS = "Pedidos"

# Seletores do iframe de pedidos
IFRAME_CONTENT = "#contentFrame"
SELETOR_TABELA_PEDIDOS = "[id='formContent:pedidoTableTable']"
SELETOR_PAGINA_ATIVA = ".wmw-gp-activep"
SELETOR_PROXIMA_PAGINA = "#formContent\\:pedidoTablePagernext"
SELETOR_STATUS = "#formConsulta\\:cdStatusPedido"
SELETOR_DATA_INICIAL = "#formConsulta\\:dtEmissaoInicialFilter"
SELETOR_DATA_FINAL = "#formConsulta\\:dtEmissaoFinalFilter"

# Valores de status disponíveis
STATUS_FATURADO = "5"
STATUS_TODOS = ""