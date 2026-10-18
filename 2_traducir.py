"""PASO 2: traduce guion.json -> guion_traducido.json (japones -> ingles) ajustando cada frase
al espacio real del juego: max 20 letras por linea (19 en la 1a linea), max 3 lineas por pagina,
y que quepa en los bytes del japones original. Necesita internet (usa Google Translate).

Uso:
   python 2_traducir.py --limite 50          prueba con 50 textos (hazlo primero)
   python 2_traducir.py --limite 2000        traduce 2000 mas (sigue donde se quedo)
   python 2_traducir.py --simulado           prueba SIN internet (traduccion falsa)
   Opciones: --hilos 3 (peticiones a la vez)  --pausa 0.6 (segundos entre peticiones)
Se puede cortar con Ctrl+C: guarda el progreso y la proxima vez continua.
Para corregir a mano una frase: abre guion_traducido.json, busca el texto y escribe tu version
en "en_manual" (una cadena por pagina, con \\n entre lineas). Tiene prioridad sobre la automatica."""
import json, re, sys, os, time, argparse, urllib.parse, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from juego_lib import limpiar_en, bytes_en

ap = argparse.ArgumentParser()
ap.add_argument("--limite", type=int, default=50)
ap.add_argument("--hilos", type=int, default=3)
ap.add_argument("--pausa", type=float, default=0.6)
ap.add_argument("--simulado", action="store_true")
a = ap.parse_args()

SAL = "guion_traducido.json"
def clave(e): return json.dumps([e["jp"], e["presupuesto"]], ensure_ascii=False)

# --- cargar guion nuevo y arrastrar lo ya traducido ---
nuevo = json.load(open("guion.json", encoding="utf-8"))
viejo = {}
if os.path.exists(SAL):
    for e in json.load(open(SAL, encoding="utf-8")): viejo[clave(e)] = e
for e in nuevo:
    o = viejo.get(clave(e))
    if o:
        for k in ("en", "en_manual"): e[k] = o.get(k, e[k])
        if o.get("estado") in ("ok", "no_cabe", "manual"): e["estado"] = o["estado"]
        e["en_largo"] = o.get("en_largo")

# --- traduccion ---
def mt(texto, id_):
    if a.simulado:
        return ("Sample line %d, just a test of the fitting system." % id_)[: max(6, len(texto))]
    q = urllib.parse.quote(texto)
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=ja&tl=en&dt=t&q={q}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for intento in range(3):
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                res = json.loads(r.read().decode("utf-8"))
            return "".join(p[0] for p in res[0] if p and p[0])
        except Exception:
            time.sleep(2 + intento * 3)
    return None

# --- ajuste de ancho / bytes ---
def envolver(t, primera):
    pal, lin, act = t.split(), [], ""
    for p in pal:
        lim = primera if not lin else 20
        if len(p) > 20: return None
        if not act: act = p
        elif len(act) + 1 + len(p) <= lim: act += " " + p
        else: lin.append(act); act = p
    if act: lin.append(act)
    if not lin: return None
    if len(lin[0]) > primera or len(lin) > 3: return None
    return "\n".join(lin)

REDUCCIONES = [
    (r"\b(do not)\b", "don't"), (r"\b(I am)\b", "I'm"), (r"\b(you are)\b", "you're"), (r"\b(it is)\b", "it's"),
    (r"\b(that is)\b", "that's"), (r"\b(cannot|can not)\b", "can't"), (r"\b(I will)\b", "I'll"), (r"\b(I have)\b", "I've"),
    (r"^(Well|Oh|Hey|Um|Uh|Yeah|Yes|So|Now|Okay|OK|Hmm|Anyway)[,.!]?\s+", ""),
    (r"\b(really|very|just|quite|actually|also)\s+", ""), (r"\b(a little|a bit)\b", "a bit"),
    (r"\b(because)\b", "cause"), (r"\b(the)\s+(?=\w)", ""),
]
def ajustar(t, presupuesto, primera):
    t = limpiar_en(re.sub(r"\s+", " ", t)).strip()
    for pat, rep in [(None, None)] + REDUCCIONES:
        if pat: t = re.sub(pat, rep, t, flags=re.I).strip()
        env = envolver(t, primera)
        if env and len(bytes_en(env)) <= presupuesto: return env, True
    return (envolver(t, primera) or t), False

def traducir_entrada(e):
    paginas, ok, largo = [], True, 0
    for i, (jp, pres) in enumerate(zip(e["jp"], e["presupuesto"])):
        src = jp.replace("\n", "").replace("…", "...").replace("～", "~")
        r = mt(src, e["id"])
        if r is None: return None
        txt, fit = ajustar(r, pres, 19 if i == 0 else 20)
        paginas.append(txt); ok = ok and fit
        largo = max(largo, len(bytes_en(txt)) - pres)
    return paginas, ok, largo

pend = [e for e in nuevo if e["estado"] == "pendiente" and not e["en_manual"] and e["en"] is None]
trabajo = pend[: a.limite]
print(f"Textos traducibles sin traducir: {len(pend)}. En esta tanda: {len(trabajo)}"
      f"{' (SIMULADO)' if a.simulado else ''}. Ctrl+C para parar y guardar.")

def guardar():
    json.dump(nuevo, open(SAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

hechos = 0
try:
    with ThreadPoolExecutor(max_workers=max(1, a.hilos)) as ex:
        futs = {}
        for e in trabajo:
            futs[ex.submit(lambda x=e: (time.sleep(a.pausa), traducir_entrada(x))[1])] = e
        for f in as_completed(futs):
            e = futs[f]; r = f.result()
            if r is None: continue
            e["en"], ok, largo = r
            e["estado"] = "ok" if ok else "no_cabe"
            e["en_largo"] = None if ok else largo
            hechos += 1
            if hechos % 25 == 0: guardar(); print(f"  {hechos}/{len(trabajo)}")
except KeyboardInterrupt:
    print("Interrumpido: guardando...")
for e in nuevo:                                  # lo escrito a mano cuenta como manual
    if e["en_manual"]: e["estado"] = "manual"
guardar()
import collections
c = collections.Counter(e["estado"] for e in nuevo)
print("\nRESULTADO:", dict(c))
print("  ok = cabe en el juego | no_cabe = la traduccion es mas larga que el espacio (sale en el informe)")
print("-> guion_traducido.json guardado.")
