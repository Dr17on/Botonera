from telegram import Update, ParseMode
from telegram.ext import CallbackContext, ConversationHandler
import logging
from config import Config
import database
import keyboards

logger = logging.getLogger(__name__)

async def admin_broadcast(update: Update, context: CallbackContext):
    """Enviar mensaje global"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in Config.ADMIN_IDS:
        await query.edit_message_text("❌ Acceso denegado.")
        return
    
    await query.edit_message_text(
        "📢 **Mensaje Global**\n\n"
        "Envía el mensaje para todos los usuarios.\n"
        "Escribe /cancel para cancelar.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['broadcasting'] = True
    return 'WAITING_BROADCAST'

async def process_broadcast(update: Update, context: CallbackContext):
    """Procesar broadcast"""
    from database import User
    
    if update.message.text == '/cancel':
        await update.message.reply_text("❌ Cancelado.")
        context.user_data.pop('broadcasting', None)
        return ConversationHandler.END
    
    db = database.get_session()
    users = db.query(User).all()
    
    message = await update.message.reply_text(f"📤 Enviando a {len(users)} usuarios...")
    
    sent = 0
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user.user_id,
                text=update.message.text,
                parse_mode=ParseMode.MARKDOWN
            )
            sent += 1
        except:
            pass
    
    await message.edit_text(f"✅ Enviado a {sent}/{len(users)} usuarios.")
    
    context.user_data.pop('broadcasting', None)
    db.close()
    return ConversationHandler.END
