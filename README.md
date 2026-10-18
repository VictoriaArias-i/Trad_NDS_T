# Trad_NDS_T

Codigo para traducir un juego de DS


# Game Script Translation Suite (JP -> EN)

Herramienta de volcado, traducción automática con ajuste dinámico de bytes/formato e inyección de texto para la localización de videojuegos binarios.

---

## ⚠️ Aviso Legal / Legal Disclaimer

1. **Sin assets propietarios:** Este repositorio **NO contiene ni distribuye** archivos binarios protegidos por derechos de autor, ejecutable alguno ni imágenes ROM (`filedata.bin`).
2. **Uso personal y educativo:** Estas herramientas han sido creadas exclusivamente con fines de investigación, aprendizaje sobre estructuras de datos en videojuegos retro/consolas y preservación digital.
3. **Responsabilidad del usuario:** El usuario final es responsable de extraer sus propios archivos binarios a partir de sus copias de juego adquiridas legalmente.
4. **Propiedad intelectual:** Todas las marcas comerciales, nombres de personajes y contenidos de diálogo pertenecen a sus respectivos desarrolladores y distribuidores oficiales.

---

## 📋 Requisitos del Sistema

* **Python 3.8+**
* Conexión a Internet (para la traducción automática mediante la API de Google Translate).
* Módulo interno `juego_lib.py` (debe estar en el mismo directorio con las funciones de codificación, mapa de kanjis y tokens del juego).

---

## 🛠️ Flujo de Trabajo (Paso a Paso)

El pipeline de traducción se compone de tres pasos secuenciales:

```
filedata.bin ──► [ 1_volcar.py ] ──► guion.json ──► [ 2_traducir.py ] ──► guion_traducido.json ──► [ 3_inyectar.py ] ──► filedata_traducido.bin
```

---

### Paso 1: Volcado de texto
Extrae todos los mensajes del binario original (`filedata.bin`), decodifica los caracteres en japonés e identifica kanjis o códigos de control especiales.

```bash
python 1_volcar.py
```

* **Entrada:** `filedata.bin`
* **Salida:** `guion.json`
* **Resultado:** Muestra en consola estadísticas de textos únicos, ocurrencias e identificación de bloques pendientes de traducir o con kanjis faltantes.

---

### Paso 2: Traducción y ajuste automático de espacio
Traduce las frases de japonés a inglés ajustando el texto para que cumpla estrictamente con los límites de la pantalla del juego y el presupuesto de bytes original.

* **Reglas visuales y de espacio:**
  * Máximo 20 caracteres por línea (19 caracteres en la primera línea).
  * Máximo 3 líneas por página.
  * Límite estricto de bytes por página (el texto traducido no puede sobrepasar los bytes ocupados por la frase japonesa original).

#### Comandos de uso:

```bash
# Prueba inicial con 50 frases (recomendado antes de ejecutar todo)
python 2_traducir.py --limite 50

# Continuar con el resto de frases en tandas
python 2_traducir.py --limite 2000 --hilos 4 --pausa 0.5

# Modo simulado (sin conexión a Internet / para pruebas rápidas de formato)
python 2_traducir.py --simulado
```

#### Parámetros disponibles:
* `--limite`: Cantidad máxima de textos a traducir en la sesión actual.
* `--hilos`: Número de peticiones simultáneas (por defecto: `3`).
* `--pausa`: Tiempo de espera en segundos entre peticiones para evitar bloqueos por tasa de uso (por defecto: `0.6`).
* `--simulado`: Genera textos de prueba localmente sin conectarse a la red.

> **Nota:** Puedes detener la ejecución en cualquier momento con `Ctrl + C`. El progreso se guardará automáticamente en `guion_traducido.json` y continuará donde se quedó la próxima vez.

---

### Paso 3: Inyección y comprobación de integridad
Inyecta las traducciones validadas de vuelta en el archivo binario. Realiza verificaciones automáticas para asegurar que ningún puntero o byte ajeno al guion haya sido modificado.

```bash
python 3_inyectar.py
```

* **Entrada:** `filedata.bin` y `guion_traducido.json` (o `filedata_prueba.bin` si existe).
* **Salida:** 
  * `filedata_traducido.bin` (Archivo binario listo con la traducción).
  * `informe_traduccion.txt` (Lista detallada de textos que no pudieron inyectarse por exceso de tamaño).

---

## ✏️ Traducción Manual y Corrección de Errores

Si un texto en `guion_traducido.json` tiene el estado `"no_cabe"`, `"faltan_kanji"` o `"codigos_raros"`, puedes corregirlo manualmente siguiendo estos pasos:

1. Abre `guion_traducido.json` en un editor de código (VS Code, Notepad++, etc.).
2. Busca el mensaje por su `"id"` o por el texto original.
3. Inserta tu versión traducida dentro del campo `"en_manual"` respetando los saltos de línea `\n`:

```json
{
  "id": 4,
  "jp": [
    "ごめんね。\n今、忙しくて……"
  ],
  "presupuesto": [ 23 ],
  "en": [ "Sorry. I'm busy\nright now…" ],
  "en_manual": [ "Sorry, I am\nbusy right now." ],
  "estado": "manual"
}
```

4. Guarda el archivo y vuelve a ejecutar `python 3_inyectar.py`. La versión dentro de `"en_manual"` tendrá prioridad absoluta sobre la traducción automática.

---

## 📁 Estructura del Repositorio

* `1_volcar.py`: Script de extracción de diálogos a JSON.
* `2_traducir.py`: Script de traducción remota, simplificación de frases y formateo.
* `3_inyectar.py`: Script de reescritura en el binario e informe de desbordamientos.
* `guion.json`: Guion original extraído (generado por `1_volcar.py`).
* `guion_traducido.json`: Base de datos de traducciones, estado y manual overrides.
* `informe_traduccion.txt`: Registro de textos excedidos que requieren revisión manual.