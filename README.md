# 🤖 Bot de Telegram para Registro de Facturas

Bot automatizado de Telegram que extrae información de facturas mediante OCR y las registra automáticamente en Google Sheets.

## 📋 Descripción

Este bot permite a usuarios en un grupo de Telegram enviar fotos de facturas y automáticamente:
- 📸 Procesa la imagen con OCR (Tesseract)
- 🔍 Extrae: Fecha, Comercio y Monto
- 🏷️ Solicita categorización de la factura
- ✅ Pide confirmación antes de guardar
- ✏️ Permite editar cualquier dato extraído
- 📊 Guarda todo en Google Sheets automáticamente

### ✨ Características principales

- ✅ **100% Gratuito** - Sin costos de API
- 🤝 **Multiusuario** - Funciona en grupos de Telegram
- 🔄 **Confirmación interactiva** - Botones para confirmar/editar datos
- 🏷️ **Categorización** - Clasifica gastos por tipo
- 📊 **Integración con Google Sheets** - Registro centralizado
- 🌍 **Idioma español** - OCR optimizado para español

---

## 🛠️ Requisitos del Sistema

### Software necesario:
- **Python 3.8+**
- **Tesseract OCR**
- **Git** (opcional, para clonar el repositorio)
- **Cuenta de Telegram**
- **Cuenta de Google**

---

## 📦 Instalación

### 1️⃣ Instalar Tesseract OCR

#### **Windows:**
1. Descarga el instalador desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Ejecuta el instalador
3. Durante la instalación:
   - ✅ Marca instalar **idioma español (spa)**
   - ✅ Anota la ruta de instalación (ejemplo: `C:\Program Files\Tesseract-OCR`)
4. Agrega Tesseract al PATH:
   - Busca "Variables de entorno" en Windows
   - Edita la variable `Path`
   - Agrega la ruta de Tesseract

#### **Linux (Ubuntu/Debian/Raspberry Pi):**
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-spa
```

#### **Verificar instalación:**
```bash
tesseract --version
tesseract --list-langs  # Debe mostrar 'spa'
```

---

### 2️⃣ Crear Bot de Telegram

1. Abre Telegram y busca **@BotFather**
2. Envía el comando: `/newbot`
3. Sigue las instrucciones:
   - Elige un nombre para tu bot
   - Elige un username (debe terminar en 'bot')
4. **Guarda el token** que te proporciona (ejemplo: `123456789:ABCdefGHI...`)
5. Desactiva Privacy Mode:
   - Envía: `/mybots`
   - Selecciona tu bot
   - **Bot Settings** → **Group Privacy** → **Turn off**
6. Agrega el bot a tu grupo de Telegram

---

### 3️⃣ Configurar Google Sheets API

#### **Crear proyecto en Google Cloud:**
1. Ve a: https://console.cloud.google.com/
2. Crea un nuevo proyecto (ejemplo: "Bot Registrador")
3. Habilita **Google Sheets API**:
   - Menú → **APIs y servicios** → **Biblioteca**
   - Busca "Google Sheets API"
   - Clic en **Habilitar**

#### **Crear cuenta de servicio:**
1. Ve a **APIs y servicios** → **Credenciales**
2. Clic en **Crear credenciales** → **Cuenta de servicio**
3. Asigna un nombre (ejemplo: "bot-telegram")
4. Rol: **Editor**
5. Clic en **Listo**
6. En la lista de cuentas, clic en la que creaste
7. Pestaña **Claves** → **Agregar clave** → **Crear clave nueva**
8. Selecciona tipo **JSON** → **Crear**
9. Se descargará un archivo JSON → **Guárdalo como `credenciales.json`**

#### **Crear y compartir Google Sheet:**

__Nota: Tambien funciona con una hoja de cálculo ya creada__

1. Ve a https://sheets.google.com
2. Crea una nueva hoja de cálculo
3. En la primera fila, agrega estos encabezados:
   ```
   A1: Timestamp
   B1: Fecha
   C1: Comercio
   D1: Categoría
   E1: Monto
   ```
4. Copia el **ID** de la hoja desde la URL:
   ```
   https://docs.google.com/spreadsheets/d/ESTE_ES_EL_ID/edit
   ```
5. Abre el archivo `credenciales.json` y copia el email del campo `client_email`
6. En tu Google Sheet, clic en **Compartir**
7. Pega el email y dale permisos de **Editor**

---

### 4️⃣ Instalar el Bot

#### **Clonar o descargar este proyecto:**
```bash
# Opción 1: Con git
git clone https://github.com/inusui/telegram-bot-expense-record.git

cd telegram-bot-expense-record

# Opción 2: Descargar ZIP y extraer
```

#### **Crear entorno virtual:**
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows (CMD):
venv\Scripts\activate.bat

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Git Bash:
source venv/Scripts/activate

# Linux:
source venv/bin/activate
```

#### **Instalar dependencias:**
```bash
# Opción 1
pip install python-telegram-bot pytesseract Pillow gspread oauth2client

# Opción 2
pip install -r requirements.txt
```

### Configurar variables de entorno:

1. Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

---

### 5️⃣ Configurar el Bot

1. Copia el archivo `credenciales.json` a la carpeta del proyecto

2. Abre el archivo `bot.py` y configura:

```python
# Token de Telegram
TELEGRAM_TOKEN = "TU_TOKEN_AQUI"  # Pega tu token aquí

# ID de Google Sheet
GOOGLE_SHEET_ID = "TU_SHEET_ID_AQUI"  # Pega el ID aquí

# Nombre de la hoja
SHEET_NAME = "Registro"  # O el nombre que uses

TESSERACT_PATH = r'C:\Users\...\Tesseract-OCR\tesseract.exe'

CREDENTIALS_FILE=credenciales.json
```

3. **Estructura de carpeta final:**
```
.
├── config/
   ├── __init__.py
   └── constants.py
├── tmp/
├── utils/
   ├── __init__.py
   ├── date_detector.py
   ├── headlers.py
   ├── responses.py
   └── tesseract_validator.py
├── venv/
├── bot.py
├── credenciales.json
├── requirements.txt
└── README.md
```

---

## 🚀 Uso

### Iniciar el bot:

Windows
```bash
# Asegúrate de tener el entorno virtual activado (debes ver "(venv)")
python bot.py
```

Ubuntu
```bash
sudo -u bots /opt/bots/venv/bin/python /opt/bots/bot.py
```
__donde bots es un usuario de sistema, esto lo hice por seguridad.__

Deberías ver:
```
🤖 Iniciando bot de facturas...
✅ Bot iniciado correctamente
📸 Esperando fotos de facturas...
Presiona Ctrl+C para detener el bot
```

---

### Flujo de uso:

1. **Enviar factura:**
   - Toma una foto de una factura
   - Envíala al grupo donde está el bot

2. **Proceso automático:**
   ```
   Usuario envía foto
        ↓
   Bot procesa con OCR
        ↓
   Bot muestra datos extraídos:
   "📋 Datos extraídos:
    📅 Fecha: 15/01/2025
    🏪 Comercio: Supermercado XYZ
    💰 Monto: $45.50"
        ↓
   Bot pregunta categoría con botones:
   [🛒 Supermercado]
   [🏥 Salud]
   [⛽ Gasolina]
   [🍽️ Comidas fuera de casa]
   [🎮 Entretenimiento]
        ↓
   Bot pide confirmación:
   "¿Los datos son correctos?"
   [✅ Sí, guardar] [❌ No, editar]
        ↓
   Si OK → Guarda en Google Sheets
   Si NO → Permite editar cada campo
   ```

3. **Editar datos (si es necesario):**
   - Presiona **[❌ No, editar]**
   - Selecciona qué campo cambiar
   - Escribe el nuevo valor
   - Confirma nuevamente

4. **Verificar en Google Sheets:**
   - Abre tu hoja de cálculo
   - Verás una nueva fila con todos los datos

---

## 🏷️ Categorías Disponibles

El bot incluye estas categorías por defecto:
- 🛒 **Supermercado**
- 🏥 **Salud**
- ⛽ **Gasolina**
- 🍽️ **Comidas fuera de casa**
- 🎮 **Entretenimiento**

### Personalizar categorías:

Edita la lista en `bot.py` (línea ~44):
```python
CATEGORIAS = [
    "🛒 Supermercado",
    "🏥 Salud",
    "⛽ Gasolina",
    "🍽️ Comidas fuera de casa",
    "🎮 Entretenimiento",
    "🏠 Hogar",
    "🚗 Transporte"
]
```


## Formas de pago Disponibles

El bot incluye estas formas de pago disponibles
-   Efectivo
-   Tarjeta de débito
-   Tarjeta de crédito
-   Yappy
-   Otro
_Edita la lista en `bot.py` (línea ~54):_

---

## ⚙️ Configuración Avanzada

### Ejecutar en Raspberry Pi 24/7:

1. **Instalar dependencias:**
```bash
sudo apt update
sudo apt install python3-pip tesseract-ocr tesseract-ocr-spa
```

2. **Instalar el bot** (seguir pasos anteriores)

3. **Crear servicio systemd** (para auto-inicio):
```bash
sudo nano /etc/systemd/system/bot-facturas.service
```

Contenido:
```ini
[Unit]
Description=Bot de Telegram
After=network.target

[Service]
Type=simple
User=bots
Group=bots
WorkingDirectory=/opt/bots

# Ruta al python del venv y al script
ExecStart=/opt/bots/venv/bin/python /opt/bots/bot.py

# Reiniciar automáticamente si falla
Restart=always
RestartSec=10

# Logs
StandardOutput=journal
StandardError=journal

# Seguridad adicional
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
NoNewPrivileges=true
ReadWritePaths=/opt/bots

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl enable bot-facturas
sudo systemctl start bot-facturas
sudo systemctl status bot-facturas
```

---

## 🔧 Solución de Problemas

### El bot no responde en el grupo:
- ✅ Verifica que desactivaste **Privacy Mode** en @BotFather
- ✅ Asegúrate de que el bot no está restringido en el grupo
- ✅ Prueba en un chat privado primero con un `hola`

### Error de OCR o no detecta texto:
- ✅ Verifica que Tesseract está instalado: `tesseract --version`
- ✅ Confirma que el idioma español está disponible: `tesseract --list-langs`
- ✅ Asegúrate de que la ruta en `bot.py` es correcta (Windows)

### Error al conectar con Google Sheets:
- ✅ Verifica que `credenciales.json` está en la carpeta correcta
- ✅ Confirma que compartiste la hoja con el email de la cuenta de servicio
- ✅ Verifica que el ID de la hoja es correcto
- ✅ Verifica que le diste permiso a bots para ver el archivo.

---

## 📊 Estructura de Datos en Google Sheets

| Timestamp           | Fecha      | Comercio         | Categoría    | Monto |
| ------------------- | ---------- | ---------------- | ------------ | ----- |
| 07/10/2025 14:30:22 | 07/10/2025 | Supermercado XYZ | Supermercado | 45.50 |
---

## 👨‍💻 Autor

[inusui](https://github.com/inusui)

Desarrollado para automatizar el registro de gastos. <h6> 
Realmente me aburri de escribir en un formulario </h6>

---

**¡Disfruta automatizando tus finanzas!** 💰✨