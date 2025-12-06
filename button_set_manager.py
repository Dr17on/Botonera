from datetime import datetime
import logging
from telegram import InlineKeyboardMarkup, ParseMode
import database

logger = logging.getLogger(__name__)

class ButtonSetScheduler:
    def __init__(self, bot):
        self.bot = bot
        logger.info("⏰ Scheduler inicializado")
    
    async def send_button_set_to_channels(self, button_set_id):
        """Enviar botonera a canales"""
        from database import ButtonSet, Channel
        
        db = database.get_session()
        button_set = db.query(ButtonSet).get(button_set_id)
        
        if not button_set or not button_set.is_active:
            db.close()
            return
        
        channels = db.query(Channel).filter(
            Channel.is_approved == True,
            Channel.is_active == True
        ).all()
        
        for channel in channels:
            try:
                # Crear mensaje simple
                text = f"📢 **{button_set.name}**\n\n{button_set.description or ''}"
                
                await self.bot.send_message(
                    chat_id=channel.channel_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN
                )
                
            except Exception as e:
                logger.error(f"Error enviando a {channel.channel_id}: {e}")
        
        button_set.last_sent = datetime.utcnow()
        db.commit()
        db.close()
