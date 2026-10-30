from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
from playwright.sync_api import Page

load_dotenv()

def fazer_login_manual(page: Page) -> None:
    """Abre a tela de login e espera o usuário logar manualmente (fallback)."""
    page.goto("http://35.237.167.233:8081/jahu/menu.faces")
    
    print("Faça o login manualmente no navegador que já está aberto.")
    print("Quando estiver logado, volte aqui e pressione ENTER no terminal.")
    input()
    
    # Verifica se realmente logou (boa prática)
    page.locator("#options").wait_for(state="visible", timeout=60_000)
    print("Login manual confirmado.")
    
def fazer_login_automatico(page: Page) -> None:
    usuario = os.getenv("PORTAL_USER")
    senha = os.getenv("PORTAL_PASS")
    if not usuario or not senha:
        raise ValueError("As variáveis PORTAL_USER e PORTAL_PASS não foram encontradas no .env")
    
    page.goto("http://35.237.167.233:8081/jahu/menu.faces")

    page.locator("#j_username").fill(usuario)
    page.locator("#j_password").fill(senha)

    page.locator("#btnEntrar").click()
    
    page.locator("#options").wait_for(state="visible", timeout=15_000)
    print("Login realizado com sucesso.")