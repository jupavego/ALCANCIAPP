# ALCANCIAPP · Tienda MEI (Arte hecho con pasión)

Sitio de un pequeño negocio de alcancías personalizadas, decoración para el hogar y artículos religiosos
(Barbosa, Antioquia). Hoy tiene el **diseñador 3D de alcancías**, la sección de encargos por WhatsApp y el contacto.

## Abrir el sitio

Doble clic en `index.html` (necesita internet para Three.js y las tipografías de Google).

## Imágenes sobre la alcancía

1. En «5 · Tus imágenes» se sube una imagen (queda guardada en la biblioteca de esa sesión).
2. Al pasar el cursor por la alcancía aparece la imagen **solo dentro de la alcancía**; fuera del cuerpo no se ve.
3. **Rueda del ratón**: más grande o más pequeña. **Flechas ← →**: inclinarla (con Shift, más fino). **Clic**: pegarla. **Esc**: cancelar.
4. Ya pegada, se puede mover, girar o agrandar desde los controles, copiar al otro lado o quitar.

## Escudos de equipos

En la pestaña «Imágenes» hay un submódulo con 9 escudos (Medellín, América, Bucaramanga, Cali, Junior, Nacional,
Once Caldas, Millonarios y Santa Fe). Se usan igual que una imagen subida. Salen de `IMGS/escudos_hoja.png`
(`herramientas/extraer_escudos.py`) y quedan en `assets/escudos/`. **Son marcas registradas de los clubes**: antes de
vender productos con ellos conviene confirmar la licencia o el permiso de cada club.

## Carpetas

| Carpeta | Qué hay |
| --- | --- |
| `index.html` | El sitio armado (un solo archivo con los tres modelos 3D incrustados). **No se edita a mano.** |
| `src/visor_plantilla.html` | Código fuente del sitio (HTML, CSS y JavaScript). Aquí se hacen los cambios. |
| `modelos/` | `alcancia_s/m/l.glb` (14×10, 16×13 y 18×15 cm) y `generar_alcancia.py`, el script de Blender que los crea. |
| `assets/iconos/` | Íconos recortados de la hoja de iconografía, con fondo transparente y sin los rótulos de debajo. |
| `IMGS/` | Imágenes originales (la hoja de iconografía). |
| `herramientas/` | `construir_sitio.py` arma `index.html`; `extraer_iconos.py` y `extraer_extra.py` recortan los íconos. |

## Flujo de trabajo

1. Cambiar `src/visor_plantilla.html`.
2. `py herramientas/construir_sitio.py` para regenerar `index.html`.
3. Si cambia la forma de la alcancía: abrir Blender, ejecutar `modelos/generar_alcancia.py` y volver al paso 2.

## Datos del negocio

- Marca: MEI · Arte hecho con pasión · By @saloisaza20
- Alcancías personalizadas · Decoración para el hogar · Artículos religiosos y más
- Barbosa, Antioquia
- WhatsApp: https://wa.link/suq7f9
- Instagram: https://www.instagram.com/mei_arteypasion/ (el sello usa @mei_arteypasion; la firma «By @saloisaza20» viene de los datos de contacto)
- Facebook: https://www.facebook.com/profile.php?id=100079029660173

## Pendiente (no hecho)

- Galería, tienda con precios y carrito, blog/consejos y «Sobre mí» (los íconos ya están en `assets/iconos/`).
- Pagos y envíos: hoy el pedido se cierra por WhatsApp; el botón copia el resumen del diseño y abre el chat.
- Foto del diseño adjunta al pedido (hoy se descarga aparte).
- Revisar que el usuario de Instagram del sello (@mei_arteypasion) y el de contacto (@saloisaza20) sean el mismo negocio.
