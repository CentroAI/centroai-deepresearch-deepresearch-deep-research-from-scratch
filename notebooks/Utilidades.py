import ipywidgets as widgets
from IPython.display import display, HTML
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# Texto que contiene la solución y que se oculta/muestra al pulsar el botón
sol1 = '''
# -----------------------------------------------
# TOOL: info_pais
# -----------------------------------------------
@tool
def info_pais(pais: str, dato: str) -> str:
    """
    Devuelve información básica sobre un país.

    Args:
        pais: Nombre del país en minúsculas (ej: 'españa', 'japon').
        dato: Tipo de dato a consultar: 'capital', 'idioma' o 'continente'.

    Returns:
        El dato solicitado sobre el país.
    """

    paises = {
        "españa":    {"capital": "Madrid",         "idioma": "Español",   "continente": "Europa"},
        "francia":   {"capital": "París",           "idioma": "Francés",   "continente": "Europa"},
        "alemania":  {"capital": "Berlín",          "idioma": "Alemán",    "continente": "Europa"},
        "italia":    {"capital": "Roma",            "idioma": "Italiano",  "continente": "Europa"},
        "portugal":  {"capital": "Lisboa",          "idioma": "Portugués", "continente": "Europa"},
        "mexico":    {"capital": "Ciudad de México","idioma": "Español",   "continente": "América"},
        "argentina": {"capital": "Buenos Aires",    "idioma": "Español",   "continente": "América"},
        "japon":     {"capital": "Tokio",           "idioma": "Japonés",   "continente": "Asia"},
        "china":     {"capital": "Pekín",           "idioma": "Chino mandarín", "continente": "Asia"},
        "canada":    {"capital": "Ottawa",          "idioma": "Inglés y Francés", "continente": "América"},
    }

    pais = pais.lower()
    dato = dato.lower()

    if pais not in paises:
        return f"No tengo información sobre '{pais}'. Países disponibles: {', '.join(paises.keys())}."

    if dato not in {"capital", "idioma", "continente"}:
        return "Dato no válido. Consulta disponibles: 'capital', 'idioma' o 'continente'."

    return f"El {dato} de {pais.capitalize()} es: {paises[pais][dato]}."
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