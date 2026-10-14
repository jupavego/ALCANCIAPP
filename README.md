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

## Catálogo de modelos

La sección «Catálogo» muestra 8 diseños listos (Clásica de barro, Rosa con lunares, Menta y corazones, Celeste a rayas,
Floral, Noche de estrellas, Hincha de Nacional y Con tu nombre). Las fotos se generan solas con el mismo visor 3D al abrir
la página. «Personalizar» carga el modelo en el visor; «Pedir este» abre WhatsApp con el mensaje listo. Para agregar o
cambiar modelos: lista `PRESETS` en `src/visor_plantilla.html`.

## Comodidades del visor

- **Deshacer / rehacer** (botones ↶ ↷ o Ctrl + Z / Ctrl + Y) y **Supr** para quitar el detalle elegido.
- **Guardado automático** en el navegador: al volver a abrir la página se retoma el último diseño.
- **Guardar diseño / Abrir diseño** (archivo `.json`) y **Empezar de nuevo**.

## Personajes e ilustraciones

En la pestaña «Imágenes», debajo de los escudos, hay 19 personajes (Ben 10, Hello Kitty, Dragon Ball, Peppa Pig, Caillou y
El Principito) tomados de `IMGS/` y limpiados con `herramientas/extraer_imagenes.py` (quedan en `assets/imagenes/`).
Se descargan en un archivo aparte (`assets/imagenes-listas.js`) la primera vez que se abre la pestaña.
**Son personajes con derechos de autor**: para vender productos con ellos hace falta licencia o permiso de sus dueños.

La imagen que se está colocando usa la misma barra de edición que los íconos (tamaño, giro, vuelta alrededor y
arriba/abajo), con «Pegar aquí» y «Cancelar».

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
