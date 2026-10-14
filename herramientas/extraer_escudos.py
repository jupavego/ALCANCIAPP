"""Recorta los 9 escudos de IMGS/escudos_hoja.png y les quita el fondo blanco (solo el que toca el borde,
así el blanco de adentro de cada escudo se conserva). Salida: assets/escudos/<id>.png

    python herramientas/extraer_escudos.py        (necesita numpy, scipy y Pillow)
"""
import pathlib

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

RAIZ = pathlib.Path(__file__).resolve().parent.parent
HOJA = RAIZ / "IMGS" / "escudos_hoja.png"
SALIDA = RAIZ / "assets" / "escudos"

FILAS = [(23, 153), (184, 319), (349, 477)]
COLUMNAS = [(1, 124), (152, 274), (297, 410)]
NOMBRES = [
    ("dim", "Independiente Medellín"), ("america", "América de Cali"), ("bucaramanga", "Atlético Bucaramanga"),
    ("cali", "Deportivo Cali"), ("junior", "Junior"), ("nacional", "Atlético Nacional"),
    ("once-caldas", "Once Caldas"), ("millonarios", "Millonarios"), ("santa-fe", "Independiente Santa Fe"),
]
ESCALA = 4   # la hoja es pequeña: se amplía para que el borde quede suave al pegarlo en la alcancía


def quitar_fondo(im):
    rgb = np.asarray(im.convert("RGB")).astype(int)
    casi_blanco = rgb.min(axis=2) > 238
    etiquetas, _ = ndimage.label(casi_blanco)
    borde = np.unique(np.concatenate([etiquetas[0], etiquetas[-1], etiquetas[:, 0], etiquetas[:, -1]]))
    fondo = np.isin(etiquetas, borde[borde > 0])
    fondo = ndimage.binary_dilation(fondo, iterations=1) & (rgb.min(axis=2) > 200)
    alfa = Image.fromarray(((~fondo) * 255).astype(np.uint8))
    out = im.convert("RGBA")
    out.putalpha(alfa)
    return out


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    hoja = Image.open(HOJA).convert("RGB")
    k = 0
    for (y0, y1) in FILAS:
        for (x0, x1) in COLUMNAS:
            ident, _nombre = NOMBRES[k]; k += 1
            rec = hoja.crop((max(0, x0 - 4), max(0, y0 - 4), min(hoja.width, x1 + 5), min(hoja.height, y1 + 5)))
            rec = quitar_fondo(rec)
            caja = rec.getbbox()
            rec = rec.crop(caja)
            grande = rec.resize((rec.width * ESCALA, rec.height * ESCALA), Image.LANCZOS)
            r, g, b, a = grande.split()
            a = a.filter(ImageFilter.GaussianBlur(1.6)).point(lambda v: 255 if v > 150 else int(v * 255 / 150))
            grande = Image.merge("RGBA", (r, g, b, a))
            grande.save(SALIDA / f"{ident}.png", optimize=True)
            print(ident, grande.size, round((SALIDA / f"{ident}.png").stat().st_size / 1024), "KB")


if __name__ == "__main__":
    main()
