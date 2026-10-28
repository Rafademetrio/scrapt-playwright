# scrap-playwright

Automação de coleta de pedidos de um portal web usando Python + Playwright,
com persistência em CSV e controle de progresso.

## O que faz

- Faz login automatizado no portal (reaproveitando sessão salva)
- Coleta pedidos do mês/dia
- Salva os dados em CSV (`pedidos_mes_ano.csv`)
- Mantém estado de progresso para retomar coletas interrompidas

## Requisitos

- Python 3.12+
- Playwright

## Instalação

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install