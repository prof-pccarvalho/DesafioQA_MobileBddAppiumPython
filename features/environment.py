# features/environment.py (adicionar no topo)
import logging
import os

def before_all(context):
    # Configura nível de logging padrão para DEBUG quando executar behave localmente
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    # Opcional: também ajusta nivel para logger do módulo pages.product_page
    logging.getLogger("pages.product_page").setLevel(logging.DEBUG)

def after_scenario(context, scenario):
    """
    <summary>
    Hook executado após cada cenário do Behave. Se existir um driver no contexto, encerra a sessão.
    </summary>
    <param name="context">Contexto do Behave possivelmente contendo context.driver</param>
    <param name="scenario">Cenário que foi executado</param>
    <returns>None</returns>
    """
    # Verifica se o contexto tem atributo 'driver' e se ele não é None
    if hasattr(context, "driver") and context.driver:
        try:
            # Tenta encerrar a sessão de forma ordenada
            context.driver.quit()
        except Exception:
            # Em caso de erro no quit, não propaga para não mascarar o resultado do cenário
            # Poderia adicionar logging aqui para investigação (ex: context.log)
            pass
