"""Recorta cada ícono de la hoja de iconografía (sin los rótulos de debajo) y le quita el fondo.

Uso (con el Python que tiene rembg):  python extraer_iconos.py
Salida: assets/iconos/<nombre>.png (fondo transparente, recortado al dibujo) y assets/iconos/_hoja.png (revisión).
"""
import pathlib

from PIL import Image
from rembg import new_session, remove

RAIZ = pathlib.Path(__file__).resolve().parent.parent
HOJA = RAIZ / "IMGS" / "Gemini_Generated_Image_y88ghjy88ghjy88g.jfif"
SALIDA = RAIZ / "assets" / "iconos"

# (nombre, caja x0, y0, x1, y1) sobre la hoja de 1024 x 1024; cada caja termina antes del rótulo
CAJAS = [
    ("sello",        430,  28, 594, 192),
    ("inicio",        62, 108, 232, 302),
    ("sobre-mi",     312, 140, 445, 300),
    ("galeria",      570, 118, 750, 306),
    ("encargos",     790, 132, 980, 306),
    ("alcancias",     58, 364, 240, 536),
    ("contacto",     286, 364, 520, 530),
    ("tienda",       566, 366, 774, 530),
    ("blog",         792, 358, 990, 526),
    ("guirnalda",     38, 682, 410, 772),
    ("divisor-busto", 38, 776, 410, 852),
    ("boton-celeste", 492, 668, 736, 726),
    ("boton-rosa",    492, 734, 736, 796),
    ("vinetas",      776, 676, 990, 772),
    ("etiquetas",    480, 856, 770, 990),
    ("marco-esquinas", 816, 830, 995, 995),
    ("vinetas-2",     92, 892, 360, 992),
]


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    hoja = Image.open(HOJA).convert("RGB")
    sesion = new_session()
    miniaturas = []
    for nombre, x0, y0, x1, y1 in CAJAS:
        recorte = hoja.crop((x0, y0, x1, y1)).resize(((x1 - x0) * 3, (y1 - y0) * 3), Image.LANCZOS)
        sin_fondo = remove(recorte, session=sesion, alpha_matting=False)
        caja = sin_fondo.getbbox()
        if caja:
            sin_fondo = sin_fondo.crop(caja)
        sin_fondo.save(SALIDA / f"{nombre}.png")
        miniaturas.append((nombre, sin_fondo))
        print(nombre, sin_fondo.size)
    # hoja de revisión sobre fondo crema
    ancho, x, y, fila_alto = 1600, 10, 10, 0
    lienzo = Image.new("RGB", (ancho, 1400), (253, 244, 230))
    for nombre, im in miniaturas:
        im = im.copy(); im.thumbnail((360, 260))
        if x + im.width > ancho:
            x, y, fila_alto = 10, y + fila_alto + 14, 0
        lienzo.paste(im, (x, y), im); x += im.width + 14; fila_alto = max(fila_alto, im.height)
    lienzo.crop((0, 0, ancho, y + fila_alto + 14)).save(SALIDA / "_hoja.png")


if __name__ == "__main__":
    main()
