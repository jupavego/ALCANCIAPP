"""Íconos sueltos sacados de los grupos de la hoja (alcancías, contacto)."""
import pathlib

from PIL import Image
from rembg import new_session, remove

RAIZ = pathlib.Path(__file__).resolve().parent.parent
HOJA = RAIZ / "IMGS" / "Gemini_Generated_Image_y88ghjy88ghjy88g.jfif"
SALIDA = RAIZ / "assets" / "iconos"
CAJAS = [("cerdito", 60, 364, 152, 452), ("casita", 152, 362, 240, 452), ("cohete", 62, 456, 142, 534),
         ("corazon", 154, 456, 236, 534), ("sobre", 326, 476, 420, 528), ("telefono", 288, 466, 330, 530),
         ("pluma", 398, 396, 468, 528)]
hoja = Image.open(HOJA).convert("RGB")
sesion = new_session()
for nombre, x0, y0, x1, y1 in CAJAS:
    r = hoja.crop((x0, y0, x1, y1)).resize(((x1 - x0) * 4, (y1 - y0) * 4), Image.LANCZOS)
    s = remove(r, session=sesion)
    b = s.getbbox()
    s = s.crop(b) if b else s
    s.save(SALIDA / f"{nombre}.png"); print(nombre, s.size, flush=True)
