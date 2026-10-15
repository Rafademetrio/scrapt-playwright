def preencher_data(frame, seletor: str, valor: str) -> None:
    """
    Seta o valor direto no campo, dispara input e change, e aperta Delete
    para forçar o mask a recalcular a formatação.
    """
    campo = frame.locator(seletor)
    campo.click()
    # Seta o valor completo de uma vez, sem digitação
    campo.evaluate(f"(el) => {{ el.value = '{valor}'; }}")
    # Dispara os eventos que o JSF/mask escuta
    campo.evaluate("""
        (el) => {
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
    """)
    # Aperta Delete — isso força o mask a "recalcular" a formatação,
    # exatamente como você fez manualmente
    campo.press("Delete")
    campo.press("Tab")
