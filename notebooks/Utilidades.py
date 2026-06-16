import ipywidgets as widgets
from IPython.display import display, HTML
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# Texto que contiene la solución y que se oculta/muestra al pulsar el botón
sol1 = '''
# -----------------------------------------------
# TOOL: consulta_clima
# -----------------------------------------------

import requests

@tool
def clima(ciudad: str) -> str:
    """Consulta el clima actual para una ciudad."""
    
    url = f"https://wttr.in/{ciudad}?format=3"
    
    response = requests.get(url)
    
    return response.text
'''

# Botón para gestionar la visibilidad de las soluciones

def mostrar_boton_solucion(solution):
    if solution == 1: # controlamos la solución a mostrar en cada momento
        solcode= sol1
    btn = widgets.Button(description="Ver solución", button_style="warning")
    out = widgets.Output()
    visible = {"valor": False}  # diccionario para poder modificarlo desde el closure

    def toggle_solution(b):
        visible["valor"] = not visible["valor"]
        with out:
            out.clear_output()
            if visible["valor"]:
                btn.description = "Ocultar solución"
                btn.button_style = "danger"
                formatter = HtmlFormatter(style="monokai")
                css = formatter.get_style_defs('.highlight')
                highlighted = highlight(solcode, PythonLexer(), formatter)
                display(HTML(f"<style>{css}</style>{highlighted}"))
            else:
                btn.description = "Ver solución"
                btn.button_style = "warning"

    btn.on_click(toggle_solution)
    display(btn, out)