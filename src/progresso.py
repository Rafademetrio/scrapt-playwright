"""Gerencia o estado de progresso da extração entre execuções."""
import json
from pathlib import Path


def carregar_progresso(caminho: str = "progresso.json") -> dict:
    """Retorna o progresso salvo, ou um estado inicial se não existir."""
    arquivo = Path(caminho)
    if not arquivo.exists():
        return {
            "ultima_pagina": 1,
            "ultimo_id_processado": None,
            "pedidos_ja_extraidos": [],
        }
    with open(arquivo, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_progresso(progresso: dict, caminho: str = "progresso.json") -> None:
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(progresso, f, ensure_ascii=False, indent=2)


def resetar_progresso(caminho: str = "progresso.json") -> None:
    arquivo = Path(caminho)
    if arquivo.exists():
        arquivo.unlink()
    print("Progresso resetado.")


def extrair_indice_do_id(id_edit_link: str) -> int:
    """
    Extrai o índice numérico de um ID como 'formContent:pedidoTable:45:editLink'.
    Retorna 45 (ou -1 se não conseguir parsear).
    """
    if not id_edit_link:
        return -1
    try:
        # Divide por ':' → ['formContent', 'pedidoTable', '45', 'editLink']
        partes = id_edit_link.split(":")
        if len(partes) >= 3:
            return int(partes[2])
    except (ValueError, IndexError):
        pass
    return -1