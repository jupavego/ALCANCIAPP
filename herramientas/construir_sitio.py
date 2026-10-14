"""Arma index.html (un solo archivo) a partir de src/visor_plantilla.html + los tres GLB de modelos/
y los escudos de assets/escudos/.

    py herramientas/construir_sitio.py
Los modelos y los escudos se incrustan en la página (así el navegador puede pegarlos en la textura sin
bloqueos); los demás íconos se enlazan por ruta relativa (assets/…).
"""
import base64
import json
import pathlib

raiz = pathlib.Path(__file__).resolve().parent.parent
html = (raiz / "src" / "visor_plantilla.html").read_text(encoding="utf-8")

for clave in ("s", "m", "l"):
    glb = (raiz / "modelos" / f"alcancia_{clave}.glb").read_bytes()
    html = html.replace(f"__GLB_{clave.upper()}__", base64.b64encode(glb).decode("ascii"))

ESCUDOS = [  # mismo orden que en extraer_escudos.py
    ("dim", "Independiente Medellín"), ("america", "América de Cali"), ("bucaramanga", "Atlético Bucaramanga"),
    ("cali", "Deportivo Cali"), ("junior", "Junior"), ("nacional", "Atlético Nacional"),
    ("once-caldas", "Once Caldas"), ("millonarios", "Millonarios"), ("santa-fe", "Independiente Santa Fe"),
]
lista = []
for ident, nombre in ESCUDOS:
    png = raiz / "assets" / "escudos" / f"{ident}.png"
    if png.exists():
        lista.append({"id": ident, "nombre": nombre,
                      "url": "data:image/png;base64," + base64.b64encode(png.read_bytes()).decode("ascii")})
html = html.replace("__ESCUDOS__", json.dumps(lista, ensure_ascii=False))

(raiz / "index.html").write_text(html, encoding="utf-8")
print("listo:", raiz / "index.html", round(len(html) / 1e6, 2), "MB,", len(lista), "escudos")
