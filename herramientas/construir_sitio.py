"""Arma el sitio a partir de src/visor_plantilla.html:

  index.html                  la página (un solo archivo) con los tres modelos 3D y los escudos incrustados
  assets/imagenes-listas.js   los personajes e ilustraciones de assets/imagenes/ (se descargan al abrir esa pestaña)

    py herramientas/construir_sitio.py

Los modelos y los escudos se incrustan en la página para que el navegador pueda pegarlos en la textura sin
bloqueos; los demás íconos se enlazan por ruta relativa (assets/…).
"""
import base64
import json
import pathlib

raiz = pathlib.Path(__file__).resolve().parent.parent


def data_url(ruta):
    return "data:image/png;base64," + base64.b64encode(ruta.read_bytes()).decode("ascii")


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
        lista.append({"id": ident, "nombre": nombre, "url": data_url(png)})
html = html.replace("__ESCUDOS__", json.dumps(lista, ensure_ascii=False))
(raiz / "index.html").write_text(html, encoding="utf-8")

# personajes e ilustraciones (mismo orden y nombres que en extraer_imagenes.py)
GRUPOS = [
    ("Ben 10", [("ben10-logo", "Logo"), ("ben10-personaje", "Ben")]),
    ("Hello Kitty", [("hello-kitty-mono", "Moño"), ("hello-kitty-unicornio", "Unicornio"), ("hello-kitty-camara", "Cámara")]),
    ("Dragon Ball", [("goku-dbz", "Goku y logo"), ("goku-ataque", "Goku ataque"), ("goku-nube", "Goku niño y nube"),
                     ("goku-nino", "Goku niño"), ("vegeta", "Vegeta")]),
    ("Peppa Pig", [("peppa-hada", "Hada"), ("peppa-osito", "Con osito"), ("peppa-fiesta", "Fiesta")]),
    ("Caillou", [("caillou", "Caillou"), ("caillou-gato", "Con Gilbert")]),
    ("El Principito", [("principito-capa", "Capa"), ("principito-dibujo", "Dibujo"), ("principito-globos", "Pájaros"),
                       ("principito-planeta", "Planeta")]),
]
grupos = []
for grupo, items in GRUPOS:
    salida = []
    for ident, nombre in items:
        png = raiz / "assets" / "imagenes" / f"{ident}.png"
        if png.exists():
            salida.append({"id": ident, "nombre": f"{grupo} · {nombre}", "corto": nombre, "url": data_url(png)})
    if salida:
        grupos.append({"grupo": grupo, "items": salida})
(raiz / "assets" / "imagenes-listas.js").write_text(
    "window.IMAGENES_LISTAS = " + json.dumps(grupos, ensure_ascii=False) + ";\n", encoding="utf-8")

print("listo: index.html", round(len(html) / 1e6, 2), "MB,", len(lista), "escudos;",
      "imagenes-listas.js", round((raiz / "assets" / "imagenes-listas.js").stat().st_size / 1e6, 2), "MB,",
      sum(len(g["items"]) for g in grupos), "imágenes")
