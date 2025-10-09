import os
import re
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler, CommandHandler
import pytesseract
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils import BotDispatcher, TesseractValidator, DateDetector

# ==================== CONFIGURACIÓN ====================
load_dotenv()

# Coloca aquí tu token de Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Coloca aquí el ID de tu Google Sheet
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# Nombre de la hoja dentro del Google Sheet
SHEET_NAME = os.getenv("SHEET_NAME", "Registro")

# Archivo de credenciales de Google
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, os.getenv('CREDENTIALS_FILE'))

TESSERACT_PATH = os.getenv('TESSERACT_PATH')

# Configurar ruta de Tesseract si está especificada
if TESSERACT_PATH and TESSERACT_PATH.strip():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


class ColumnasSheet:
    TIMESTAMP = 0
    FECHA = 1
    COMERCIO = 2
    CATEGORIA = 3
    MONTO = 4
    FORMAS_PAGO = 5

CATEGORIAS_LIST = [
    "🛒 Supermercado",
    "🏥 Salud",
    "⛽ Gasolina",
    "🍽️ Comidas fuera de casa",
    "🎮 Entretenimiento",
    "🏠 Hogar",
    "🚗 Transporte"
]

FORMAS_PAGO_LIST = [
    "Efectivo",
    "Tarjeta de débito",
    "Tarjeta de crédito",
    "Yappy",
    "Otro"
]

# Estados para la conversación
ESPERANDO_CONFIRMACION = 1
ESPERANDO_NUEVO_DATO = 2

# Diccionario para almacenar datos temporales de cada usuario
datos_usuario = {}

# =======================================================

# Configurar Google Sheets
def conectar_google_sheets():
    """Conecta con Google Sheets y retorna la hoja de cálculo"""
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)

    # Abrir la hoja de cálculo por ID
    sheet = client.open_by_key(GOOGLE_SHEET_ID)
    worksheet = sheet.worksheet(SHEET_NAME)

    return worksheet

# Extraer información de la factura usando OCR
def extraer_datos_factura(imagen_path):
    """
    Extrae texto de la imagen y busca fecha, comercio y monto
    """
    try:
        # Abrir imagen
        img = Image.open(imagen_path)

        # Extraer texto con Tesseract (español)
        texto = pytesseract.image_to_string(img, lang='spa')

        print(f"Texto extraído:\n{texto}\n")  # Para debug

        # Buscar fecha (formatos: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY)
        checker = DateDetector()
        fecha = checker.extract_date(texto)
        print(f"Fecha detectada: {fecha}")

        # Buscar monto (formatos: $XX.XX, XX.XX, $XX,XX)
        # Busca números con 2 decimales, opcionalmente con $ al inicio
        monto_match = re.search(r'\$?\s*(\d{1,}[.,]\d{2})\b', texto)
        monto = monto_match.group(1) if monto_match else "No detectado"

        # Extraer nombre del comercio (primera línea con texto significativo)
        lineas = [l.strip() for l in texto.split('\n') if l.strip()]
        comercio = lineas[0] if lineas else "No detectado"

        # Limpiar el nombre del comercio (máximo 50 caracteres)
        comercio = comercio[:50]

        return fecha, comercio, monto

    except Exception as e:
        print(f"Error al procesar imagen: {e}")
        return "Error", "Error", "Error"

# Guardar en Google Sheets


def guardar_en_sheets(worksheet, fecha, comercio, monto, categoria, formas_pago):
    """Agrega una nueva fila con los datos de la factura"""
    try:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Agregar nueva fila
        fila = [''] * 6
        fila[ColumnasSheet.FECHA] = fecha
        fila[ColumnasSheet.COMERCIO] = comercio
        fila[ColumnasSheet.CATEGORIA] = categoria
        fila[ColumnasSheet.FORMAS_PAGO] = formas_pago
        fila[ColumnasSheet.MONTO] = float(monto)
        fila[ColumnasSheet.TIMESTAMP] = timestamp
        worksheet.append_row(fila, value_input_option='USER_ENTERED')

        return True
    except Exception as e:
        print(f"Error al guardar en Google Sheets: {e}")
        return False

# Crear teclado de confirmación


def crear_teclado_confirmacion():
    """Crea botones de Sí/No"""
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Sí, guardar", callback_data="confirmar_si"),
            InlineKeyboardButton("❌ No, editar", callback_data="confirmar_no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def crear_teclado_continuar():
    """Crea botón para continuar"""
    keyboard = [
        [
            InlineKeyboardButton(
                "➡️ Si, Continuar", callback_data="continuar"),
            InlineKeyboardButton("❌ No, editar", callback_data="confirmar_no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Crear teclado de categorías


def crear_teclado_categorias():
    """Crea botones para seleccionar la categoría"""
    keyboard = []
    for categoria in CATEGORIAS_LIST:
        keyboard.append([InlineKeyboardButton(
            categoria, callback_data=f"cat_{categoria}")])
    return InlineKeyboardMarkup(keyboard)

# Crear teclado de formas de pago


def crear_teclado_formas_pago():
    """Crea botones para seleccionar la forma de pago"""
    keyboard = []
    for forma in FORMAS_PAGO_LIST:
        keyboard.append([InlineKeyboardButton(
            forma, callback_data=f"fp_{forma}")])
    return InlineKeyboardMarkup(keyboard)

# Crear teclado de selección de campo


def crear_teclado_campos():
    """Crea botones para seleccionar qué campo editar"""
    keyboard = [
        [InlineKeyboardButton("📅 Fecha", callback_data="editar_fecha")],
        [InlineKeyboardButton("🏪 Comercio", callback_data="editar_comercio")],
        [InlineKeyboardButton("💰 Monto", callback_data="editar_monto")],
        [InlineKeyboardButton(
            "🏷️ Categoría", callback_data="editar_categoria")],
        [InlineKeyboardButton(
            "💳 Forma de pago", callback_data="editar_forma_pago")],
        [InlineKeyboardButton("🔙 Cancelar", callback_data="cancelar")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Manejador de imágenes


async def manejar_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Se ejecuta cuando alguien envía una foto al grupo/chat
    """
    try:
        user_id = update.effective_user.id

        # Obtener la foto de mejor calidad
        foto = update.message.photo[-1]

        # Descargar la foto
        archivo = await foto.get_file()
        tmp_dir = os.path.join(BASE_DIR, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        imagen_path = os.path.join(tmp_dir, f"factura_{foto.file_id}.jpg")
        await archivo.download_to_drive(imagen_path)

        # Enviar mensaje de "procesando"
        mensaje_procesando = await update.message.reply_text("⏳ Procesando factura...")

        # Extraer datos con OCR
        fecha, comercio, monto = extraer_datos_factura(imagen_path)

        # Guardar datos temporalmente para este usuario
        datos_usuario[user_id] = {
            'fecha': fecha,
            'comercio': comercio,
            'monto': monto,
            'categoria': None,
            'formas_pago': None,
            'imagen_path': imagen_path
        }
        # Verificar si no se detecto la fecha
        if fecha == "No detectada":
            datos_usuario[user_id]['editando'] = 'fecha'
            await mensaje_procesando.edit_text(
                "📅 No se pudo detectar la fecha en la factura.\n\nPor favor, escribe la fecha (formato: DD/MM/YYYY):"
            )
            return
        print(
            f"Datos extraídos - Fecha: {fecha}, Comercio: {comercio}, Monto: {monto}")

        # Mostrar datos extraídos y pedir confirmación
        mensaje = f"""📋 Datos extraídos de la factura:
📅 Fecha: {fecha}
🏪 Comercio: {comercio}
💰 Monto: ${monto}

¿Los datos son correctos?"""

        await mensaje_procesando.edit_text(
            mensaje,
            reply_markup=crear_teclado_continuar()
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar la factura: {str(e)}")
        print(f"Error completo: {e}")

# Manejador de botones
async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja las respuestas de los botones"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    # Verificar que el usuario tenga datos guardados
    if user_id not in datos_usuario:
        await query.edit_message_text("❌ No hay datos de factura. Envía una foto nuevamente.")
        return

    datos = datos_usuario[user_id]

    # Selección de categoría
    if query.data.startswith("cat_"):
        categoria_seleccionada = query.data[4:]
        datos_usuario[user_id]['categoria'] = categoria_seleccionada

        # Mostrar confirmacion con todos los datos
        mensaje = f"""🏷️ Categoría: **{categoria_seleccionada}**
¿Es correcto?"""

        await query.edit_message_text(
            mensaje,
            reply_markup=crear_teclado_continuar()
        )
        return

    # Selección de forma de pago
    if query.data.startswith("fp_"):
        forma_pago_seleccionada = query.data[3:]
        datos_usuario[user_id]['formas_pago'] = forma_pago_seleccionada

        # Mostrar confirmacion con todos los datos
        mensaje = f"""💳 Forma de pago: {forma_pago_seleccionada}
¿Es correcto?"""
        await query.edit_message_text(
            mensaje,
            reply_markup=crear_teclado_continuar()
        )
        return
    # Continuar
    if query.data == "continuar":
        if datos['categoria'] is None:
            await query.edit_message_text(
                "🏷️ Selecciona la categoría:",
                reply_markup=crear_teclado_categorias()
            )
            return
        elif datos['formas_pago'] is None:
            await query.edit_message_text(
                "💳 Selecciona la forma de pago:",
                reply_markup=crear_teclado_formas_pago()
            )
            return
        else:
            # Mostrar datos actualizados y pedir confirmación nuevamente
            mensaje = f"""📋 Datos actualizados:
📅 Fecha: {datos['fecha']}
🏪 Comercio: {datos['comercio']}
💰 Monto: ${datos['monto']}
🏷️ Categoría: {datos.get('categoria', 'No seleccionada')}
💳 Forma de pago: {datos.get('formas_pago', 'No seleccionada')}

¿Los datos son correctos?"""
            await query.edit_message_text(
                mensaje,
                reply_markup=crear_teclado_confirmacion()
            )
            return

    # CONFIRMACIÓN: Usuario dice SÍ
    if query.data == "confirmar_si":
        # Conectar con Google Sheets y guardar
        try:
            worksheet = conectar_google_sheets()
            if guardar_en_sheets(worksheet, datos['fecha'], datos['comercio'], datos['monto'], datos['categoria'], datos['formas_pago']):
                await query.edit_message_text(
                    f"""✅ ¡Factura guardada exitosamente!

📅 Fecha: {datos['fecha']}
🏪 Comercio: {datos['comercio']}
💰 Monto: ${datos['monto']}
🏷️ Categoría: {datos['categoria']}
💳 Forma de pago: {datos['formas_pago']}"""
                )
            else:
                await query.edit_message_text("❌ Error al guardar en Google Sheets.")

            # Limpiar imagen temporal
            if os.path.exists(datos['imagen_path']):
                os.remove(datos['imagen_path'])

            # Limpiar datos del usuario
            del datos_usuario[user_id]

        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")

    # CONFIRMACIÓN: Usuario dice NO
    elif query.data == "confirmar_no":
        await query.edit_message_text(
            "¿Qué dato deseas cambiar?",
            reply_markup=crear_teclado_campos()
        )

    # EDITAR FECHA
    elif query.data == "editar_fecha":
        datos_usuario[user_id]['editando'] = 'fecha'
        await query.edit_message_text(
            f"📅 Fecha actual: {datos['fecha']}\n\nEscribe la nueva fecha (formato: DD/MM/YYYY):"
        )

    # EDITAR COMERCIO
    elif query.data == "editar_comercio":
        datos_usuario[user_id]['editando'] = 'comercio'
        await query.edit_message_text(
            f"🏪 Comercio actual: {datos['comercio']}\n\nEscribe el nuevo nombre del comercio:"
        )

    # EDITAR MONTO
    elif query.data == "editar_monto":
        datos_usuario[user_id]['editando'] = 'monto'
        await query.edit_message_text(
            f"💰 Monto actual: ${datos['monto']}\n\nEscribe el nuevo monto (solo números, ej: 45.50):"
        )

    # EDITAR CATEGORÍA
    elif query.data == "editar_categoria":
        await query.edit_message_text(
            "🏷️ Selecciona la nueva categoría:",
            reply_markup=crear_teclado_categorias()
        )

    # EDITAR FORMA DE PAGO
    elif query.data == "editar_forma_pago":
        await query.edit_message_text(
            "💳 Selecciona la nueva forma de pago:",
            reply_markup=crear_teclado_formas_pago()
        )

    # CANCELAR
    elif query.data == "cancelar":
        # Limpiar imagen temporal
        if os.path.exists(datos['imagen_path']):
            os.remove(datos['imagen_path'])

        del datos_usuario[user_id]
        await query.edit_message_text("❌ Operación cancelada.")

# Manejador de texto - Lee los mensajes del chat de telegram
async def manejar_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe el nuevo dato que el usuario quiere cambiar"""
    user_id = update.effective_user.id
    texto = update.message.text.strip()

    # 👋 --- SALUDO ---
    if texto.lower() == "hola":
        await BotDispatcher.responder_hola(update, context)
        return

    # Verificar que el usuario esté en proceso de edición
    if user_id not in datos_usuario or 'editando' not in datos_usuario[user_id]:
        return  # Ignorar mensaje si no está editando

    datos = datos_usuario[user_id]
    campo_editando = datos['editando']
    nuevo_valor = update.message.text.strip()

    # Actualizar el campo correspondiente
    if campo_editando == 'fecha':
        datos['fecha'] = nuevo_valor
    elif campo_editando == 'comercio':
        datos['comercio'] = nuevo_valor
    elif campo_editando == 'monto':
        # Limpiar el monto (quitar símbolos)
        nuevo_valor = nuevo_valor.replace('$', '').replace(',', '.').strip()
        datos['monto'] = nuevo_valor

    # Eliminar el flag de edición
    del datos['editando']

    campos_faltantes = []
    if datos['comercio'] == "No detectado":
        campos_faltantes.append('comercio')
    if datos['monto'] == "No detectado":
        campos_faltantes.append('monto')
    if campos_faltantes and campo_editando == 'fecha':
        proximo_campo = campos_faltantes[0].lower()
        datos['editando'] = proximo_campo
        await update.message.reply_text(
            f"{'🏪' if proximo_campo == 'comercio' else '💰'} Tampoco se detectó el {proximo_campo}.\n\nPor favor, escríbelo:"
        )
        return
    if datos['categoria'] is None or datos['formas_pago'] is None:
        if datos['categoria'] is None:
            await update.message.reply_text(
                "🏷️ Selecciona la categoría:",
                reply_markup=crear_teclado_categorias()
            )
            return
        elif datos['formas_pago'] is None:
            await update.message.reply_text(
                "💳 Selecciona la forma de pago:",
                reply_markup=crear_teclado_formas_pago()
            )
            return
        return

    # Mostrar datos actualizados y pedir confirmación nuevamente
    mensaje = f"""📋 Datos actualizados:

📅 Fecha: {datos['fecha']}
🏪 Comercio: {datos['comercio']}
💰 Monto: ${datos['monto']}
🏷️ Categoría: {datos.get('categoria', 'No seleccionada')}
💳 Forma de pago: {datos.get('formas_pago', 'No seleccionada')}

¿Los datos son correctos?"""

    await update.message.reply_text(
        mensaje,
        reply_markup=crear_teclado_confirmacion()
    )

# Función principal


def main():
    """Iniciar el bot"""
    print("🤖 Iniciando bot de facturas...")

    # Verificar que el token esté configurado
    if not TELEGRAM_TOKEN:
        print("❌ ERROR: Debes configurar tu TELEGRAM_TOKEN")
        return

    if not GOOGLE_SHEET_ID:
        print("❌ ERROR: Debes configurar tu GOOGLE_SHEET_ID")
        return

    if not CREDENTIALS_FILE:
        print("❌ ERROR: Debes configurar tu archivo de credenciales de Google (CREDENTIALS_FILE)")
        return

    if not TESSERACT_PATH:
        print("❌ ERROR: Debes configurar la ruta al ejecutable de Tesseract-OCR (TESSERACT_PATH)")
        return

    # Verificar Tesseract
    TesseractValidator.verificar_tesseract()

    # Crear la aplicación
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Agregar manejadores
    app.add_handler(MessageHandler(filters.PHOTO, manejar_foto))
    app.add_handler(CallbackQueryHandler(manejar_botones))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, manejar_texto))

    print("✅ Bot iniciado correctamente")
    print("📸 Esperando fotos de facturas...")
    print("Presiona Ctrl+C para detener el bot\n")

    # Iniciar el bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
