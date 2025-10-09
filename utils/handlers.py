"""Handlers para el bot de Telegram"""

from telegram import Update
from telegram.ext import ContextTypes
from .responses import MENSAJE_HOLA


class BotDispatcher:
    """Clase para manejar mensajes del bot de Telegram"""

    @staticmethod
    async def responder_hola(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Responde cuando el usuario dice 'hola'.
        Útil para validar que el bot está funcionando correctamente.

        Args:
            update: Objeto Update de Telegram
            context: Contexto de la conversación
        """
        texto = update.message.text.lower()

        if texto == "hola":
            nombre = update.effective_user.first_name
            await update.message.reply_text(MENSAJE_HOLA.format(nombre=nombre))
