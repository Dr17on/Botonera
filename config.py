import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """
    🔧 CONFIGURACIÓN DEL BOT
    En Replit: Secrets > Add new secret
    """
    
    # ============================================
    # 🔐 CREDENCIALES PRINCIPALES
    # ============================================
    
    # 1. TOKEN DEL BOT (obligatorio)
    # Obtener de @BotFather en Telegram
    BOT_TOKEN = os.getenv('BOT_TOKEN', '8416859105:AAHal-l6yiMWODNZPWUKc5guVBmnQupN39E')
    
    # 2. ID DE ADMINISTRADOR (obligatorio)
    # Tu ID de Telegram (obtener con @userinfobot)
    admin_ids_str = os.getenv('ADMIN_IDS', '6757087193')
    ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
    
    # 3. CREDENCIALES USERBOT (opcional)
    # Obtener de https://my.telegram.org
    API_ID = os.getenv('API_ID', '27253348')
    API_HASH = os.getenv('API_HASH', '46fb5c35a4ef622b37451514d0a7afe8')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER', '+528120029188')
    
    # ============================================
    # ⚙️ CONFIGURACIÓN TÉCNICA
    # ============================================
    
    # 4. BASE DE DATOS
    # Replit proporciona PostgreSQL gratuito
    # O usa SQLite para desarrollo
    if os.getenv('REPLIT_DB_URL'):
        # PostgreSQL de Replit
        DATABASE_URL = os.getenv('REPLIT_DB_URL')
    else:
        # SQLite local
        DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot.db')
    
    # 5. CONFIGURACIÓN GENERAL
    DEFAULT_TIMEZONE = os.getenv('DEFAULT_TIMEZONE', 'America/Mexico_City')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    PORT = int(os.getenv('PORT', 8080))
    
    # 6. URLS PARA REPLIT
    REPLIT_USERNAME = os.getenv('REPLIT_USERNAME', '')
    REPLIT_APP_NAME = os.getenv('REPLIT_APP_NAME', '')
    REPL_SLUG = os.getenv('REPL_SLUG', '')
    
    @classmethod
    def get_replit_url(cls):
        """Obtener URL del bot en Replit"""
        if cls.REPLIT_USERNAME and cls.REPLIT_APP_NAME:
            return f"https://{cls.REPLIT_APP_NAME}.{cls.REPLIT_USERNAME}.repl.co"
        elif cls.REPL_SLUG:
            return f"https://{cls.REPL_SLUG}.repl.co"
        return "https://tu-app.repl.co"
    
    @classmethod
    def validate(cls):
        """Validar configuración"""
        errors = []
        
        # Validar BOT_TOKEN
        if not cls.BOT_TOKEN or 'TU_BOT_TOKEN' in cls.BOT_TOKEN:
            errors.append("❌ BOT_TOKEN no configurado")
            logging.error("Configura BOT_TOKEN en Replit Secrets")
        
        # Validar ADMIN_IDS
        if not cls.ADMIN_IDS:
            errors.append("❌ ADMIN_IDS no configurado")
            logging.error("Configura ADMIN_IDS en Replit Secrets")
        
        # Mostrar advertencias para userbot
        if not all([cls.API_ID, cls.API_HASH, cls.PHONE_NUMBER]):
            logging.warning("⚠️ Userbot no configurado completamente")
            logging.warning("Algunas funciones estarán deshabilitadas")
        
        # Mostrar información de conexión
        logging.info("=" * 50)
        logging.info("🤖 BOT CONFIGURADO PARA REPLIT")
        logging.info(f"📁 DB: {cls.DATABASE_URL[:50]}...")
        logging.info(f"👑 Admin IDs: {cls.ADMIN_IDS}")
        logging.info(f"🌐 URL: {cls.get_replit_url()}")
        logging.info("=" * 50)
        
        if errors:
            raise ValueError("\n".join(errors))
        
        return True
