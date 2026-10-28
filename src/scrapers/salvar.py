"""Persistência dos dados extraídos em CSV."""
import csv
from pathlib import Path

# Colunas na ordem em que vão aparecer no CSV
CAMPOS = [
    "numero_pedido",
    "cod_cliente",
    "razao_social",
    "representante",
    "data_emissao",
    "hora_emissao",
    "status",
    "origem",
    "valor_total_pedido",
    "item_codigo",
    "item_descricao",
    "item_qtd",
    "item_valor_base",
    "item_pct_desconto",
    "item_liquido",
    "item_valor_com_tributos",
    "item_valor_com_st",
    "item_total_st",
    "item_total",
    "item_total_com_st",
    "item_total_com_tributos",
]



def salvar_pedidos_csv(pedidos: list[dict], caminho: str) -> None:
    """
    Salva pedidos e seus itens num CSV achatado.

    Cada item vira uma linha, repetindo os dados do pedido. Se um pedido
    não tiver itens, ele é salvo com uma linha em que os campos de item
    ficam vazios (assim o pedido não desaparece do arquivo).
    """
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS)
        writer.writeheader()

        for pedido in pedidos:
            itens = pedido.get("itens") or [{}]  # garante pelo menos 1 linha

            for item in itens:
                linha = {
                    "numero_pedido": pedido.get("numero_pedido", ""),
                    "cod_cliente": pedido.get("cod_cliente", ""),
                    "razao_social": pedido.get("razao_social", ""),
                    "representante": pedido.get("representante", ""),
                    "data_emissao": pedido.get("data_emissao", ""),
                    "hora_emissao": pedido.get("hora_emissao", ""),
                    "status": pedido.get("status", ""),
                    "origem": pedido.get("origem", ""),
                    "valor_total_pedido": pedido.get("valor_total", ""),
                    "item_codigo": item.get("codigo", ""),
                    "item_descricao": item.get("descricao", ""),
                    "item_qtd": item.get("qtd", ""),
                    "item_valor_base": item.get("valor_base", ""),
                    "item_pct_desconto": item.get("pct_desconto", ""),
                    "item_liquido": item.get("liquido", ""),
                    "item_valor_com_tributos": item.get("valor_com_tributos", ""),
                    "item_valor_com_st": item.get("valor_com_st", ""),
                    "item_total_st": item.get("total_st", ""),
                    "item_total": item.get("total", ""),
                    "item_total_com_st": item.get("total_com_st", ""),
                    "item_total_com_tributos": item.get("total_com_tributos", ""),
                }
                writer.writerow(linha)

    print(f"Salvos {len(pedidos)} pedidos em {caminho}")
    

def carregar_csv_para_dicts(caminho: str) -> list[dict]:
    """
    Carrega um CSV gerado por salvar_pedidos_csv de volta para a estrutura
    de pedidos (lista de dicts, cada um com 'itens' aninhado).

    Reconstrói o agrupamento por numero_pedido. Retorna lista vazia
    se o arquivo não existir.
    """
    if not Path(caminho).exists():
        return []

    pedidos_por_numero: dict[str, dict] = {}

    with open(caminho, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for linha in reader:
            numero = linha["numero_pedido"]

            # Se é a primeira vez que vemos esse pedido, cria o dict base
            if numero not in pedidos_por_numero:
                pedidos_por_numero[numero] = {
                    "numero_pedido": numero,
                    "cod_cliente": linha["cod_cliente"],
                    "razao_social": linha["razao_social"],
                    "representante": linha["representante"],
                    "data_emissao": linha["data_emissao"],
                    "hora_emissao": linha["hora_emissao"],
                    "status": linha["status"],
                    "origem": linha["origem"],
                    "valor_total": linha["valor_total_pedido"],
                    "itens": [],
                }

            # Se a linha tem dados de item, adiciona à lista de itens do pedido
            if linha["item_codigo"]:
                pedidos_por_numero[numero]["itens"].append({
                    "codigo": linha["item_codigo"],
                    "descricao": linha["item_descricao"],
                    "qtd": linha["item_qtd"],
                    "total": linha["item_total"],
                    # Mantém só os campos que o salvamento gravou.
                    # Se depois expandir as colunas, é só adicionar aqui.
                })

    # Preserva a ordem em que os pedidos aparecem no CSV (Python 3.7+ mantém)
    return list(pedidos_por_numero.values())