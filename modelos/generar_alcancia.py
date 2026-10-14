"""Alcancía base (cerdito de barro) para un simulador web de personalización.

Se ejecuta DENTRO de Blender (MCP o pestaña Scripting):
    exec(open(r"C:\Users\jo\Desktop\JP\ALCANCIAPP\modelos\generar_alcancia.py", encoding="utf-8").read())
Genera los tres tamaños y exporta un GLB y plantillas UV por tamaño en SALIDA.

Medidas (cm): largo nariz-cola x alto. Ancho del cuerpo = 0.86 x largo.
Piezas con nombre fijo: cuerpo (con patas y hocico fundidos), oreja_izq, oreja_der, cola. Cada una tiene su
propio material y su propio mapa UV 0-1. El cuerpo usa UV equirrectangular: costura en la
espalda, polos arriba (ranura) y abajo (base); el estiramiento está solo en esos polos.
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector
from mathutils.kdtree import KDTree

SALIDA = r"C:\Users\jo\Desktop\JP\ALCANCIAPP\modelos"
TAMANOS = {"s": (14, 10), "m": (16, 13), "l": (18, 15)}
COLOR_BARRO = (0.62, 0.27, 0.13, 1.0)


def limpiar():
    for o in list(bpy.data.objects):
        if o.type == "MESH":
            bpy.data.objects.remove(o, do_unlink=True)
    for coleccion in (bpy.data.meshes, bpy.data.materials):
        for x in list(coleccion):
            if x.users == 0:
                coleccion.remove(x)


def nuevo(nombre, bm):
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.collection.objects.link(ob)
    return ob


def esfera_bm(bm, rx, ry, rz, loc=(0, 0, 0), seg=48, rings=32):
    bmesh.ops.create_uvsphere(
        bm, u_segments=seg, v_segments=rings, radius=1.0, calc_uvs=True,
        matrix=Matrix.Translation(loc) @ Matrix.Diagonal((rx, ry, rz, 1)),
    )


def booleana(ob, cortador, operacion="DIFFERENCE"):
    m = ob.modifiers.new("b", "BOOLEAN")
    m.operation = operacion
    m.object = cortador
    m.solver = "EXACT"
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cortador, do_unlink=True)


def cilindro_y(nombre, r1, r2, largo, loc, seg=32):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r1, radius2=r2, depth=largo,
        matrix=Matrix.Translation(loc) @ Euler((-math.pi / 2, 0, 0)).to_matrix().to_4x4(),
    )
    return nuevo(nombre, bm)


def uv_esferico(ob, centro):
    """UV equirrectangular con la costura en la espalda (-Y)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        datos = []
        for l in f.loops:
            p = l.vert.co - centro
            v = 0.5 + math.asin(max(-1, min(1, p.z / max(p.length, 1e-9)))) / math.pi
            if math.hypot(p.x, p.y) < 1e-5:
                datos.append(["polo", None, v])
                continue
            ang = math.atan2(p.x, p.y)
            tipo = "costura" if abs(abs(ang) - math.pi) < 1e-4 else "normal"
            datos.append([tipo, 0.5 + ang / (2 * math.pi), v])
        normales = [d[1] for d in datos if d[0] == "normal"]
        cruza = bool(normales) and max(normales) - min(normales) > 0.5
        if cruza:
            normales = [u + 1.0 if u < 0.5 else u for u in normales]
        lado_alto = (sum(normales) / len(normales) > 0.5) if normales else True
        vals = []
        for d in datos:
            if d[0] == "normal":
                vals.append(d[1] + 1.0 if cruza and d[1] < 0.5 else d[1])
            elif d[0] == "costura":
                vals.append(1.0 if lado_alto else 0.0)
            else:
                vals.append(None)
        base = [x for x in vals if x is not None]
        prom = sum(base) / len(base) if base else 0.5
        # una cara que sigue cruzando es de la ranura (zona sin decorar): se colapsa
        malo = max(base) - min(base) > 0.2 or max(base) > 1.0001 if base else False
        for l, u, d in zip(f.loops, vals, datos):
            uu = prom if u is None else u
            if malo:
                uu = sum(x % 1.0 for x in base) / len(base)
            l[uvl].uv = (min(1.0, max(0.0, uu)), d[2])
    bm.to_mesh(ob.data)
    bm.free()


def uv_proyectado(ob):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")


def material(ob):
    m = bpy.data.materials.new("mat_" + ob.name)
    m.use_nodes = True
    n = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = COLOR_BARRO
    n.inputs["Roughness"].default_value = 0.85
    n.inputs["Metallic"].default_value = 0.0
    ob.data.materials.clear()
    ob.data.materials.append(m)


def smin(a, b, k):
    """Unión suave de dos campos de distancia (el empalme sale de aquí, sin escalones)."""
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


def superficie_nets(D, origen, h):
    """Extrae la superficie D=0 de un campo de distancia en rejilla (surface nets): malla de cuadriláteros."""
    inside = D < 0
    nx, ny, nz = D.shape
    mapa = -np.ones((nx - 1, ny - 1, nz - 1), dtype=np.int64)
    c = [inside[i:nx - 1 + i, j:ny - 1 + j, k:nz - 1 + k] for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    todo = np.logical_and.reduce(c)
    alguno = np.logical_or.reduce(c)
    activo = alguno & ~todo
    n = int(activo.sum())
    mapa[activo] = np.arange(n)
    suma = np.zeros((n, 3))
    cuenta = np.zeros(n)
    quads = []
    for a in range(3):
        b, c2 = (a + 1) % 3, (a + 2) % 3
        sl_p = [slice(0, nx), slice(0, ny), slice(0, nz)]
        sl_q = list(sl_p)
        sl_p[a] = slice(0, D.shape[a] - 1)
        sl_q[a] = slice(1, D.shape[a])
        dp, dq = D[tuple(sl_p)], D[tuple(sl_q)]
        cambia = (dp < 0) != (dq < 0)
        ii = np.argwhere(cambia)
        if len(ii) == 0:
            continue
        d0 = dp[cambia]
        d1 = dq[cambia]
        t = d0 / (d0 - d1)
        pos = ii.astype(float)
        pos[:, a] += t
        pos = pos * h + origen
        validas = np.ones(len(ii), dtype=bool)
        ids = []
        for (db, dc) in ((-1, -1), (0, -1), (0, 0), (-1, 0)):
            idx = ii.copy()
            idx[:, b] += db
            idx[:, c2] += dc
            ok = (idx[:, 0] >= 0) & (idx[:, 1] >= 0) & (idx[:, 2] >= 0) &                  (idx[:, 0] < nx - 1) & (idx[:, 1] < ny - 1) & (idx[:, 2] < nz - 1)
            validas &= ok
            idx = np.clip(idx, 0, np.array([nx - 2, ny - 2, nz - 2]))
            ids.append(mapa[idx[:, 0], idx[:, 1], idx[:, 2]])
        ids = np.stack(ids, axis=1)
        validas &= (ids >= 0).all(axis=1)
        for col in range(4):
            np.add.at(suma, ids[validas, col], pos[validas])
            np.add.at(cuenta, ids[validas, col], 1.0)
        q = ids[validas]
        sentido = (dp < 0)[cambia][validas]
        q = np.where(sentido[:, None], q[:, ::-1], q)
        quads.append(q)
    vertices = suma / np.maximum(cuenta, 1.0)[:, None]
    return vertices, np.concatenate(quads) if quads else np.zeros((0, 4), dtype=np.int64)


def suavizar_taubin(verts, quads, pares=12, lam=0.5, mu=-0.53):
    """Quita el escalonado de la rejilla sin encoger la pieza (Taubin) sobre la malla de cuadriláteros."""
    e = np.concatenate([quads[:, [0, 1]], quads[:, [1, 2]], quads[:, [2, 3]], quads[:, [3, 0]]])
    e = np.unique(np.sort(e, axis=1), axis=0)
    a, b = e[:, 0], e[:, 1]
    grado = np.bincount(np.concatenate([a, b]), minlength=len(verts)).astype(float)
    grado[grado == 0] = 1.0
    for _ in range(pares):
        for factor in (lam, mu):
            suma = np.zeros_like(verts)
            np.add.at(suma, a, verts[b])
            np.add.at(suma, b, verts[a])
            verts = verts + factor * (suma / grado[:, None] - verts)
    return verts


def cuerpo_implicito(A, H, rx, ry, rz, centro, caras_objetivo=6500):
    """Cuerpo, patas y hocico como UN solo campo de distancia con uniones suaves: el empalme de las
    patas y del hocico con el óvalo sale continuo, sin escalones. Se extrae la malla y se simplifica."""
    h = 0.0007 * H / 0.13
    x0, x1 = -(rx + 0.006), rx + 0.006
    y0, y1 = centro.y - ry - 0.006, 0.50 * A + 0.006
    z0, z1 = -0.003, centro.z + rz + 0.004
    xs = np.arange(x0, x1, h); ys = np.arange(y0, y1, h); zs = np.arange(z0, z1, h)
    X, Y, Z = np.meshgrid(xs.astype(np.float32), ys.astype(np.float32), zs.astype(np.float32), indexing="ij")

    # cuerpo: elipsoide en huevo (más angosto hacia la cola); distancia aproximada
    t = np.clip((centro.y - Y) / ry, 0.0, 1.0)
    Xp = X / (1 - 0.20 * t * t)
    p = np.stack([Xp, Y - centro.y, Z - centro.z])
    r = np.array([rx, ry, rz], dtype=np.float32).reshape(3, 1, 1, 1)
    k0 = np.sqrt(((p / r) ** 2).sum(axis=0))
    k1 = np.sqrt(((p / (r * r)) ** 2).sum(axis=0))
    D = k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)
    del p, k0, k1, t, Xp

    # patas: ensanchamiento continuo desde la base plana; se funden con empalme suave
    k_pata = 0.010 * H / 0.13
    for px in (-1, 1):
        for py in (0.14 * A, -0.16 * A):
            x = px * 0.38 * rx
            r_max = 0.150 * H
            while True:
                z_techo, ok = 0.0, True
                for a in range(16):
                    ang = a * math.pi / 8
                    xx, yy = x + r_max * math.cos(ang), py + 1.1 * r_max * math.sin(ang)
                    q = 1 - (xx / rx) ** 2 - ((yy - centro.y) / ry) ** 2
                    ok = ok and q > 0.04
                    z_techo = max(z_techo, centro.z - rz * math.sqrt(max(q, 0.0)))
                if ok:
                    break
                r_max *= 0.93
            z_techo += 0.04 * H
            r0 = 0.092 * H
            u = np.clip(Z / z_techo, 0.0, 1.0)
            radio = r0 + (r_max - r0) * u ** 1.7
            rho = np.sqrt((X - x) ** 2 + ((Y - py) / 1.1) ** 2)
            lado = rho - radio
            pata = -smin(-lado, Z, 0.003)                 # base plana con el borde apenas redondeado
            pata = np.maximum(pata, Z - z_techo)
            D = smin(D, pata, k_pata)
            del u, radio, rho, lado, pata

    # hocico: disco chato de borde marcado (redondeo de 1,5 mm), unión suave y corta
    zh = 0.485 * H
    y_c, largo = 0.362 * A, 0.18 * A     # el disco entra bien en el cuerpo; solo asoma la punta
    ro = np.sqrt(X ** 2 + (Z - zh) ** 2)
    f = np.clip((Y - (y_c - largo / 2)) / largo, 0.0, 1.0)
    radio_h = 0.170 * H + (0.1305 * H - 0.170 * H) * f   # 10 % más pequeño
    rr = 0.0012
    q1 = ro - radio_h + rr
    q2 = np.abs(Y - y_c) - largo / 2 + rr
    disco = np.sqrt(np.maximum(q1, 0) ** 2 + np.maximum(q2, 0) ** 2) + np.minimum(np.maximum(q1, q2), 0) - rr
    D = smin(D, disco, 0.0012 * H / 0.13)   # unión casi en arista: ángulo marcado
    del ro, f, radio_h, q1, q2, disco

    # ranura de monedas: fina y de largo moderado, en el centro del lomo (corte limpio en el campo)
    y_cola = centro.y - ry
    ran_ini, ran_fin = y_cola + 0.25 * 2 * ry, y_cola + 0.53 * 2 * ry
    qx = np.abs(X) - 0.0014 * A / 0.16
    qy = np.abs(Y - (ran_ini + ran_fin) / 2) - (ran_fin - ran_ini) / 2
    ranura = np.maximum(np.maximum(qx, qy), (centro.z + rz - 0.018 * H / 0.13) - Z)
    D = np.maximum(D, -ranura)
    del qx, qy, ranura
    del X, Y, Z
    D[0, :, :] = D[-1, :, :] = D[:, 0, :] = D[:, -1, :] = D[:, :, 0] = D[:, :, -1] = 1.0
    verts, quads = superficie_nets(D, np.array([xs[0], ys[0], zs[0]]), h)
    del D
    verts = suavizar_taubin(verts, quads)
    bm = bmesh.new()
    bv = [bm.verts.new(v) for v in verts]
    for q in quads:
        try:
            bm.faces.new([bv[i] for i in q])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    cuerpo = nuevo("cuerpo", bm)

    bpy.context.view_layer.objects.active = cuerpo
    m = cuerpo.modifiers.new("simplificar", "DECIMATE")
    m.ratio = min(1.0, caras_objetivo / max(1, len(cuerpo.data.polygons)))
    bpy.ops.object.modifier_apply(modifier=m.name)
    bm = bmesh.new()
    bm.from_mesh(cuerpo.data)
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                           plane_co=(0, 0, 0), plane_no=(1, 0, 0), dist=1e-6)
    bm.to_mesh(cuerpo.data)
    bm.free()
    return cuerpo


def empalmar(ob, A, H, sobre_cuerpo, caras_objetivo=4500):
    """Funde patas y hocico con el cuerpo: rehace la malla uniforme (voxel), suaviza solo junto a la
    unión (un empalme tipo barro, más ancho en las patas y corto en el hocico, para que el disco del
    hocico conserve su borde), simplifica y corta la malla en x=0 para dejar la costura UV."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    patas, hocico = [], []
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(35):
            for x in e.verts:
                if sobre_cuerpo(x.co):                      # solo la línea donde el cono corta al cuerpo
                    (hocico if x.co.y > 0.31 * A else patas).append(x.co.copy())
    bm.free()

    ob.data.remesh_voxel_size = 0.0007 * H / 0.13
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.voxel_remesh()
    m0 = ob.modifiers.new("previa", "DECIMATE")      # malla más liviana antes de suavizar (rápido)
    m0.ratio = min(1.0, 22000 / max(1, len(ob.data.polygons)))
    bpy.ops.object.modifier_apply(modifier=m0.name)

    def arbol(puntos):
        kd = KDTree(max(1, len(puntos)))
        for i, c in enumerate(puntos):
            kd.insert(c, i)
        kd.balance()
        return kd if puntos else None

    zonas = [(arbol(patas), 0.30 * H), (arbol(hocico), 0.045 * H)]
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    R = {}
    for v in bm.verts:
        if v.co.z < 0.02 * H:
            continue
        w = 0.0
        for kd, d in zonas:
            if kd is None:
                continue
            dist = kd.find(v.co)[2]
            if dist < d:
                w = max(w, (1 - dist / d) ** 0.8)
        if v.co.y < 0.31 * A:      # las patas: no tocar la parte de abajo del pie (z bajo)
            w *= max(0.0, min(1.0, (v.co.z - 0.03 * H) / (0.07 * H)))
        if w > 0:
            R[v] = w

    def paso(factor):
        nuevo_co = {}
        for v, w in R.items():
            vec = [e.other_vert(v).co for e in v.link_edges]
            if vec:
                nuevo_co[v] = v.co.lerp(sum(vec, Vector()) / len(vec), factor * w)
        for v, co in nuevo_co.items():
            v.co = co

    for _ in range(80):           # suavizado Taubin: alisa sin encoger la pieza
        paso(0.55)
        paso(-0.58)
    for v in bm.verts:
        if v.co.z < 0.015 * H:
            v.co.z = 0.0              # bases de las patas bien planas
    bm.to_mesh(ob.data)
    bm.free()

    m = ob.modifiers.new("simplificar", "DECIMATE")
    m.ratio = min(1.0, caras_objetivo / max(1, len(ob.data.polygons)))
    bpy.ops.object.modifier_apply(modifier=m.name)

    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                           plane_co=(0, 0, 0), plane_no=(1, 0, 0), dist=1e-6)
    bm.to_mesh(ob.data)
    bm.free()


def generar(A_cm, B_cm):
    limpiar()
    A, H = A_cm / 100.0, B_cm / 100.0
    # cuerpo en huevo: más largo que ancho y más angosto hacia la cola
    rx, ry, rz = 0.36 * A, 0.430 * A, 0.40 * H
    centro = Vector((0, -0.02 * A, 0.47 * H))
    cuerpo = cuerpo_implicito(A, H, rx, ry, rz, centro)

    def altura_cuerpo(x, y):
        q = 1 - (x / rx) ** 2 - ((y - centro.y) / ry) ** 2
        return centro.z + rz * math.sqrt(max(q, 0.0))

    # (la ranura de monedas ya viene cortada en el cuerpo implícito)

    # orejas: medio domo apoyado sobre la cabeza; cara plana hacia el frente, curva hacia la cola
    for nom, sx in (("oreja_izq", -1), ("oreja_der", 1)):
        bm = bmesh.new()
        rz_o = 0.20 * H
        esfera_bm(bm, 0.165 * H, 0.11 * H, rz_o, seg=32, rings=20)
        for v in bm.verts:
            if v.co.y > 0:
                v.co.y = 0.0
            v.co.x *= 1 - 0.30 * max(0.0, v.co.z / rz_o) ** 2   # punta ancha y redondeada
        bmesh.ops.rotate(bm, cent=(0, 0, 0), verts=bm.verts,
                         matrix=Euler((math.radians(-22), math.radians(sx * 16), 0)).to_matrix())
        ox, oy = sx * 0.26 * (2 * rx), centro.y - ry + 0.66 * 2 * ry   # cara plana al 66 % del largo
        bmesh.ops.translate(bm, vec=(ox, oy, altura_cuerpo(ox, oy) - 0.03 * H), verts=bm.verts)
        nuevo(nom, bm)

    # cola: un tubito (cilindro redondeado) ceñido al cuerpo: va en vertical por la parte trasera y
    # se curva hacia un lado, pegado al contorno del óvalo, con la punta apenas levantada
    radio_c = 0.021 * H
    a0, a1 = math.radians(34), math.radians(12)           # recorre la espalda en vertical, de arriba hacia abajo
    b0, b1 = math.radians(0), math.radians(8)             # y se va desviando hacia un lado
    N, SEG = 20, 18
    centros, normales = [], []
    for n in range(N + 1):
        sn = n / N
        be = b0 + (b1 - b0) * sn ** 1.3
        al = a0 + (a1 - a0) * sn
        rxe = rx * (1 - 0.20 * (math.cos(al) * math.cos(be)) ** 2)      # el óvalo se angosta hacia la cola
        px_ = rxe * math.cos(al) * math.sin(be)
        py_ = centro.y - ry * math.cos(al) * math.cos(be)
        pz_ = centro.z + rz * math.sin(al)
        g = Vector((px_ / rxe ** 2, (py_ - centro.y) / ry ** 2, (pz_ - centro.z) / rz ** 2)).normalized()
        suave = min(1.0, sn / 0.25)
        desp = radio_c * (-0.9 + 1.0 * suave * suave * (3 - 2 * suave)) + radio_c * 1.2 * max(0.0, sn - 0.7) ** 2 / 0.09
        centros.append(Vector((px_, py_, pz_)) + g * desp)
        normales.append(g)
    bm = bmesh.new()
    anillos = []
    for n, c in enumerate(centros):
        T = (centros[min(N, n + 1)] - centros[max(0, n - 1)]).normalized()
        B = T.cross(normales[n]).normalized()                # en el plano del contorno, perpendicular al tubito
        M = B.cross(T).normalized()
        sn = n / N
        k = 1.0 if sn < 0.85 else math.sqrt(max(0.0, 1 - ((sn - 0.85) / 0.15) ** 2)) * 0.96 + 0.04   # punta redonda
        anillos.append([bm.verts.new(c + (B * math.cos(2 * math.pi * t / SEG) +
                                          M * math.sin(2 * math.pi * t / SEG)) * radio_c * k)
                        for t in range(SEG)])
    for a, b in zip(anillos, anillos[1:]):
        for t in range(SEG):
            bm.faces.new((a[t], a[(t + 1) % SEG], b[(t + 1) % SEG], b[t]))
    bm.faces.new(list(reversed(anillos[0])))
    bm.faces.new(anillos[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    nuevo("cola", bm)

    partes = [o for o in bpy.data.objects if o.type == "MESH"]
    for o in partes:
        for p in o.data.polygons:
            p.use_smooth = True
    uv_esferico(cuerpo, centro)
    for o in partes:
        if o.name != "cuerpo":
            uv_proyectado(o)
        material(o)
    # el hocico mira a -Y de Blender = +Z de glTF (el frente estándar del visor)
    for o in partes:
        o.rotation_euler = (0, 0, math.pi)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return partes


def exportar(sufijo):
    ruta = os.path.join(SALIDA, "alcancia_%s.glb" % sufijo)
    bpy.ops.object.select_all(action="DESELECT")
    for o in bpy.data.objects:
        if o.type == "MESH":
            o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=ruta, export_format="GLB", use_selection=True,
                              export_apply=True, export_yup=True)
    # plantillas UV, una por pieza
    for o in [o for o in bpy.data.objects if o.type == "MESH"]:
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.export_layout(filepath=os.path.join(SALIDA, "uv_%s_%s.png" % (sufijo, o.name)),
                                 size=(1024, 1024), opacity=0.25)
        bpy.ops.object.mode_set(mode="OBJECT")
    return ruta


def todo():
    os.makedirs(SALIDA, exist_ok=True)
    for sufijo, (a, b) in TAMANOS.items():
        generar(a, b)
        print(sufijo, exportar(sufijo), os.path.getsize(os.path.join(SALIDA, "alcancia_%s.glb" % sufijo)), "bytes")
    generar(*TAMANOS["m"])  # deja el mediano en la escena


todo()
