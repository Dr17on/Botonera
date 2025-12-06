import logging
from config import Config

logger = logging.getLogger(__name__)

class UserBotManager:
    def __init__(self):
        self.is_connected = False
    
    async def initialize(self):
        """Inicializar userbot"""
        try:
            if Config.API_ID and Config.API_HASH and Config.PHONE_NUMBER:
                logger.info("🤖 Userbot configurado")
                self.is_connected = True
                return True
            else:
                logger.warning("⚠️ Userbot no configurado")
                return False
        except:
            return False
