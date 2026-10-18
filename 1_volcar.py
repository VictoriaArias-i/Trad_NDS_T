"""PASO 1: lee filedata.bin y crea guion.json con todos los mensajes del juego en japones legible.
Uso:  python 1_volcar.py"""
import json, collections
from juego_lib import *

d = open("filedata.bin", "rb").read()
kanji = cargar_kanji()
unicos = collections.OrderedDict()
total = 0
for m in mensajes(d, kanji):
    total += 1
    jp, desc, raro = [], [], False
    for _, largo, b in m["paginas"]:
        t, dd, r = decodificar(b, kanji)
        jp.append(t); desc += dd; raro = raro or r
    clave = json.dumps([jp, [p[1] for p in m["paginas"]]], ensure_ascii=False)
    e = unicos.setdefault(clave, {"jp": jp, "presupuesto": [p[1] for p in m["paginas"]],
                                  "ocurrencias": [], "kanji_faltantes": sorted(set("%04X" % c for c in desc)),
                                  "raro": raro, "en": None, "en_manual": [], "estado": "pendiente"})
    e["ocurrencias"].append(m["inicio"])
lista = list(unicos.values())
for i, e in enumerate(lista):
    e["id"] = i
    if e["kanji_faltantes"]: e["estado"] = "faltan_kanji"
    elif e["raro"]: e["estado"] = "codigos_raros"
json.dump(lista, open("guion.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

est = collections.Counter(e["estado"] for e in lista)
occ = collections.Counter()
for e in lista: occ[e["estado"]] += len(e["ocurrencias"])
print(f"Mensajes en el guion: {total}  |  textos distintos: {len(lista)}")
for k, v in est.most_common(): print(f"  {k:15} {v:6} textos  ({occ[k]} apariciones)")
print("-> guion.json creado. Los 'pendiente' son los que ya se pueden traducir.")
