"""PASO 3: mete en el juego las traducciones de guion_traducido.json.
- Parte de filedata_prueba.bin si existe (el que crea parche_prueba.py con tus traducciones manuales),
  y SOLO toca mensajes que sigan en japones original. Nunca pisa lo ya traducido.
- Escribe filedata_traducido.bin (mismo tamano que el original). El original no se toca.
Uso:  python 3_inyectar.py"""
import json, os, collections
from juego_lib import *

orig = open("filedata.bin", "rb").read()
base = "filedata_prueba.bin" if os.path.exists("filedata_prueba.bin") else "filedata.bin"
cur = bytearray(open(base, "rb").read())
assert len(cur) == len(orig)
print("Parto de:", base)
kanji = cargar_kanji()
msgs = {m["inicio"]: m for m in mensajes(orig, kanji)}
guion = json.load(open("guion_traducido.json", encoding="utf-8"))

cont = collections.Counter(); informe = []
for e in guion:
    paginas = e["en_manual"] or (e["en"] if e["estado"] == "ok" else None)
    if not paginas:
        if e["estado"] == "no_cabe": informe.append(e)
        continue
    if len(paginas) != len(e["presupuesto"]): cont["paginas_no_coinciden"] += 1; continue
    partes, fallo = [], None
    for i, (p, pres) in enumerate(zip(paginas, e["presupuesto"])):
        b = bytes_en(limpiar_en(p))
        if len(b) > pres: fallo = f"pagina {i+1}: {len(b)} bytes > {pres}"; break
        partes.append(b.ljust(pres, b" "))
    if fallo: cont["no_cabe"] += 1; informe.append(e); continue
    nuevo = b"\x1f".join(partes)
    for off in e["ocurrencias"]:
        m = msgs.get(off)
        if not m or [p[1] for p in m["paginas"]] != e["presupuesto"]: cont["no_coincide_con_original"] += 1; continue
        if bytes(cur[off: off + len(m["span"])]) != m["span"]: cont["ya_traducido_antes"] += 1; continue
        assert len(nuevo) == len(m["span"])
        cur[off: off + len(nuevo)] = nuevo
        cont["mensajes_traducidos"] += 1

# --- comprobaciones de seguridad ---
assert len(cur) == len(orig)
fuera = sum(1 for i in range(0, BLOQUE[0]) if cur[i] != orig[i]) + sum(1 for i in range(BLOQUE[1], len(orig)) if cur[i] != orig[i])
rotos = 0
for off, m in msgs.items():
    f = off + len(m["span"])
    if cur[f:f + 2] != orig[f:f + 2]: rotos += 1                     # el fin de mensaje debe seguir igual
    cortes = [t[2] for t in tokens(bytes(cur[off: off + len(m["span"])])) if t[0] == "C" and t[1] == PAG]
    cortes0 = [t[2] for t in tokens(m["span"]) if t[0] == "C" and t[1] == PAG]
    if cortes != cortes0 and bytes(cur[off: off + len(m["span"])]) != m["span"]: rotos += 1   # paginas alineadas
open("filedata_traducido.bin", "wb").write(cur)

print("\nRESULTADO"); [print(f"  {k:28} {v}") for k, v in cont.items()]
print(f"  bytes cambiados fuera del guion: {fuera}   |   mensajes con fin/paginas danados: {rotos}")
assert fuera == 0 and rotos == 0, "ALGO SALIO MAL: no uses este archivo"
informe.sort(key=lambda e: -(e.get("en_largo") or 0))
with open("informe_traduccion.txt", "w", encoding="utf-8") as f:
    f.write("TRADUCCIONES QUE NO CABEN (corrigelas en guion_traducido.json -> en_manual)\n\n")
    for e in informe[:500]:
        f.write(f"id {e['id']}  espacio {e['presupuesto']}  sobran {e.get('en_largo')} bytes\n  JP: {' / '.join(e['jp'])}\n  EN: {e['en']}\n\n")
print("-> filedata_traducido.bin listo.  Informe de las que no caben: informe_traduccion.txt")
