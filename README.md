# Game Script Translation Suite (JP -> EN / ES) - Nintendo DS

Herramienta completa de volcado, traducción automática con ajuste dinámico de bytes/formato e inyección de texto para proyectos de localización de videojuegos de Nintendo DS.

---

## ⚠️ Aviso Legal / Legal Disclaimer

1. **Sin assets propietarios:** Este repositorio **NO contiene ni distribuye** archivos binarios protegidos por derechos de autor, ejecutables ni imágenes ROM (`.nds` o `filedata.bin`).
2. **Uso personal y educativo:** Estas herramientas han sido creadas exclusivamente con fines de investigación, aprendizaje sobre estructuras de datos en videojuegos y preservación digital.
3. **Responsabilidad del usuario:** El usuario final es responsable de extraer sus propios archivos binarios a partir de sus copias de juego adquiridas legalmente.
4. **Propiedad intelectual:** Todas las marcas comerciales, nombres de personajes y contenidos de diálogo pertenecen a sus respectivos desarrolladores y distribuidores oficiales.

---

## 🧰 Herramientas y Requisitos Previos

Para utilizar este pipeline de traducción necesitarás el siguiente software:

* **Python 3.8+**: Intérprete necesario para ejecutar los scripts de automatización (`1_volcar.py`, `2_traducir.py`, `3_inyectar.py`).
* **Tinke** *(o Tinke v0.9+ / NDS Editor)*:
  * Programa fundamental para explorar e inspeccionar el sistema de archivos interno de las ROMs de Nintendo DS (`.nds`).
  * Se utiliza para extraer los archivos binarios originales del juego y para volver a empaquetar la ROM con los textos traducidos.
* **Notepad++** *(o Visual Studio Code)*:
  * Editor recomendado para revisar y corregir manualmente los archivos JSON (`guion_traducido.json` o `kanji_codigos.json`) sin corromper la codificación de caracteres en UTF-8.
* **Copia Legal del Juego (ROM `.nds`)**:
  * Necesaria para extraer el archivo binario contenedor de los diálogos.

---

## 📂 Preparación: Obtención de `filedata.bin`

Dado que este repositorio no aloja datos con derechos de autor, debes extraer el archivo original de texto siguiendo estos pasos:

1. Abre el programa **Tinke**.
2. Carga tu copia legal de la ROM del juego (`.nds`).
3. Navega por el árbol de archivos interno de la ROM (usualmente en la carpeta `data/` o directorio similar según el juego).
4. Localiza el archivo binario que almacena el guion de textos (en este proyecto denominado `filedata.bin`).
5. Extrae el archivo y colócalo directamente en la carpeta raíz de este repositorio.

---

## 🔤 Mapa de Kanjis (`kanji_codigos.json`)

Muchos videojuegos de consolas portátiles no utilizan codificaciones de texto estándar (como UTF-8 o Shift-JIS puras), sino **tablas de caracteres e índices numéricos propietarios** para renderizar los Kanjis en pantalla.

### ¿Cómo se construyó la tabla de este proyecto?
1. **Capturas de pantalla:** Se tomaron capturas durante la ejecución del juego con diálogos en japonés.
2. **Reconocimiento óptico (OCR):** Se procesaron las imágenes mediante Google Translate y herramientas de OCR para identificar con precisión el Kanji mostrado.
3. **Mapeo correlativo por IA:** Se correlacionaron los valores hexadecimales leídos en el binario por el motor gráfico con los caracteres japoneses correspondientes, generando una tabla de equivalencias JSON.

### 💡 Importante para otros desarrolladores / ROMs
* El archivo **`kanji_codigos.json`** incluido sirve como **ejemplo funcional** enfocado en el juego y revisión analizada durante el desarrollo.
* Si estás trabajando en una versión, revisión o juego diferente, **deberás crear tu propio archivo `kanji_codigos.json`** utilizando la misma estructura clave-valor:

```json
{
  "0200": "亜",
  "020C": "怖",
  "0216": "扱"
}
```
*Donde la clave (`"0200"`) representa el código Hexadecimal de 2 bytes leido en el binario y el valor (`"亜"`) es el carácter UTF-8 correspondiente.*

---

## 🛠️ Flujo de Trabajo (Pipeline Paso a Paso)

El flujo de traducción consta de tres fases secuenciales:

```
[ ROM (.nds) ]
      │ (Extracción mediante Tinke)
      ▼
filedata.bin ──► [ 1_volcar.py ] ──► guion.json ──► [ 2_traducir.py ] ──► guion_traducido.json ──► [ 3_inyectar.py ] ──► filedata_traducido.bin
                                                                                                                          │ (Re-inyección mediante Tinke)
                                                                                                                          ▼
                                                                                                                    [ ROM Traducida ]
```

### Paso 1: Volcado de texto
Extrae todos los mensajes de `filedata.bin`, decodifica los caracteres en japonés empleando `kanji_codigos.json` e identifica códigos de control especiales.

```bash
python 1_volcar.py
```
* **Entrada:** `filedata.bin`, `kanji_codigos.json`
* **Salida:** `guion.json`

### Paso 2: Traducción y ajuste automático de espacio
Traduce las frases ajustando dinámicamente el texto para no sobrepasar los límites físicos de la pantalla ni el presupuesto de bytes original.

* **Reglas de formato visual:**
  * Máximo 20 caracteres por línea (19 en la primera línea).
  * Máximo 3 líneas por página.
  * Presupuesto estricto de bytes por página para evitar desbordar secciones de memoria.

```bash
# Prueba rápida con 50 frases
python 2_traducir.py --limite 50

# Traducción en tandas con pausas de seguridad
python 2_traducir.py --limite 2000 --hilos 4 --pausa 0.5

# Modo simulado (para pruebas de formato sin conexión a API)
python 2_traducir.py --simulado
```

### Paso 3: Inyección y verificación
Reescribe las traducciones en el archivo binario comprobando punteros y la integridad de los datos.

```bash
python 3_inyectar.py
```
* **Entrada:** `filedata.bin`, `guion_traducido.json`
* **Salida:** `filedata_traducido.bin` y `informe_traduccion.txt` (registro de desbordamientos).

---

## ✏️ Corrección y Traducción Manual

Si una frase requiere un ajuste fino o excede el espacio disponible (marcada como `"no_cabe"` o `"faltan_kanji"`):

1. Abre `guion_traducido.json` con Notepad++ o VS Code.
2. Busca el registro por su `"id"`.
3. Escribe tu texto corregido en el campo `"en_manual"` respetando los saltos de línea `\n`:

```json
{
  "id": 4,
  "jp": [ "ごめんね。\n今、忙しくて……" ],
  "presupuesto": [ 23 ],
  "en": [ "Sorry. I'm busy\nright now…" ],
  "en_manual": [ "Sorry, I am\nbusy right now." ],
  "estado": "manual"
}
```
4. Guarda el archivo y ejecuta nuevamente `python 3_inyectar.py`. El campo `"en_manual"` siempre tendrá prioridad sobre la traducción automática.

---

## 📁 Estructura del Repositorio

```
Trad_NDS_T/
├── 1_volcar.py          # Script de extracción de diálogos binarios a JSON
├── 2_traducir.py        # Script de traducción remota y formateo dinámico
├── 3_inyectar.py        # Script de inyección en el binario y verificación
├── kanji_codigos.json   # Tabla de mapeo Hex/Kanji (Archivo de ejemplo)
├── config.json          # Configuración de parámetros y rutas
├── requirements.txt     # Dependencias de Python necesarias
├── .gitignore           # Exclusión de archivos binarios y temporales
└── README.md            # Documentación general del proyecto
```