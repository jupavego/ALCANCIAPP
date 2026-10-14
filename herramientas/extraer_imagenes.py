"""Prepara las imágenes predefinidas de IMGS/: fondo transparente, recortadas al dibujo y de tamaño moderado.
Salida: assets/imagenes/<id>.png

    python herramientas/extraer_imagenes.py         (necesita Pillow, numpy, scipy y rembg)

Cada imagen tiene un «modo»:
  alfa     -> ya viene con fondo transparente
  blanco   -> fondo blanco o gris claro liso: se quita solo lo que toca el borde (el blanco de adentro se conserva)
  rembg    -> el fondo es un cuadriculado «de mentira» o acuarela: se separa con rembg
"""
import pathlib

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "IMGS"
SALIDA = RAIZ / "assets" / "imagenes"
MAX_LADO = 640

# (id, nombre visible, archivo, modo)
IMAGENES = [
    ("ben10-logo", "Ben 10 · logo", "Ben_10_2005_logo.png", "alfa"),
    ("ben10-personaje", "Ben 10", "ben10-logo-png_seeklogo-330882.png", "blanco"),
    ("hello-kitty-mono", "Hello Kitty · moño", "png-transparent-hello-kitty-hello-kitty-japanese-bobtail-hello-kitty-ribbon-cartoon-flower-snout-thumbnail.png", "rembg"),
    ("hello-kitty-unicornio", "Hello Kitty · unicornio", "hello-kitty-logo-png_seeklogo-638031.png", "blanco"),
    ("hello-kitty-camara", "Hello Kitty · cámara", "images.png", "blanco"),
    ("goku-dbz", "Goku · Dragon Ball Z", "backgroundless-image-of-goku-with-the-dragon-ball-z-logo-free-png.webp", "alfa"),
    ("goku-ataque", "Goku · ataque", "images.jfif", "rembg"),
    ("goku-nube", "Goku niño · nube", "images (1).png", "blanco"),
    ("goku-nino", "Goku niño", "images (2).png", "blanco"),
    ("vegeta", "Vegeta", "images (3).png", "rembg"),
    ("peppa-hada", "Peppa Pig · hada", "0-3013_im225genes-de-personajes-amigos-de-peppa-pig-im225genes.png", "alfa"),
    ("peppa-osito", "Peppa Pig · osito", "peppa-pig-clipart-osito-miniatura.webp", "blanco-sin-marca"),
    ("peppa-fiesta", "Peppa Pig · fiesta", "e06c6a9ba9855c7df44d8bcd4eb4e36d.jpg", "blanco"),
    ("caillou", "Caillou", "images (1).jfif", "blanco"),
    ("caillou-gato", "Caillou y Gilbert", "images (2).jfif", "blanco"),
    ("principito-planeta", "El Principito · planeta", "images (3).jfif", "rembg"),
    ("principito-globos", "El Principito · pájaros", "76713392b3c8c75b42de92a2cdd069f2.jpg", "rembg"),
    ("principito-capa", "El Principito · capa", "png-clipart-prince-holding-sword-illustration-the-little-prince-musician-book-others-prince-fictional-character-thumbnail.png", "rembg"),
    ("principito-dibujo", "El Principito · dibujo", "png-transparent-the-little-prince-drawing-o-pequeno-principe-para-colorir-art-little-prince-food-prince-cartoon-thumbnail.png", "blanco"),
]


def quitar_blanco(im, tolerancia=34):
    rgb = np.asarray(im.convert("RGB")).astype(int)
    claro = (rgb.min(axis=2) > 255 - tolerancia) & ((rgb.max(axis=2) - rgb.min(axis=2)) < 26)
    etiquetas, _ = ndimage.label(claro)
    borde = np.unique(np.concatenate([etiquetas[0], etiquetas[-1], etiquetas[:, 0], etiquetas[:, -1]]))
    fondo = np.isin(etiquetas, borde[borde > 0])
    fondo = ndimage.binary_dilation(fondo, iterations=1) & (rgb.min(axis=2) > 200)
    alfa = Image.fromarray(((~fondo) * 255).astype(np.uint8)).filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(0.8))
    out = im.convert("RGBA")
    out.putalpha(alfa)
    return out


def quitar_marca(im):
    """La marca de agua está pegada al borde de abajo: se recorta esa franja."""
    ancho, alto = im.size
    return im.crop((0, 0, ancho, int(alto * 0.925)))


def main():
    from rembg import new_session, remove

    SALIDA.mkdir(parents=True, exist_ok=True)
    import sys
    solo = set(sys.argv[1:])
    sesion = None
    for ident, nombre, archivo, modo in IMAGENES:
        if solo and ident not in solo:
            continue
        im = Image.open(ORIGEN / archivo)
        if modo == "alfa":
            out = im.convert("RGBA")
        elif modo.startswith("blanco"):
            out = quitar_blanco(im)
            if modo == "blanco-sin-marca":
                out = quitar_marca(out)
        else:
            sesion = sesion or new_session()
            out = remove(im.convert("RGB"), session=sesion)
        caja = out.getbbox()
        if caja:
            out = out.crop(caja)
        out.thumbnail((MAX_LADO, MAX_LADO), Image.LANCZOS)
        ruta = SALIDA / f"{ident}.png"
        out.save(ruta, optimize=True)
        print(ident, out.size, round(ruta.stat().st_size / 1024), "KB", flush=True)


if __name__ == "__main__":
    main()
