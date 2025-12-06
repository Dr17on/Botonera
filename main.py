#!/usr/bin/env python3
"""
🤖 BOT DE BOTONERAS AUTOMÁTICAS
Versión adaptada para GitHub + Replit
"""

import asyncio
import logging
import sys
import os
import signal
from threading import Thread
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler
)
from keep_alive import keep_alive  # Para Replit

# Importar módulos del bot
from config import Config
import database
import keyboards
import handlers
import admin_handlers
from button_set_manager import ButtonSetScheduler

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL.upper()),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Aplicación Flask para mantener vivo el bot en Replit
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "telegram-bot-buttoneras",
        "version": "1.0.0",
        "platform": "replit",
        "github": "https://github.com/tuusuario/telegram-bot-buttoneras"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/stats')
def stats():
    from database import get_session, User, Channel
    db = get_session()
    try:
        total_users = db.query(User).count()
        total_channels = db.query(Channel).filter_by(is_approved=True).count()
        return jsonify({
            "users": total_users,
            "channels": total_channels,
            "bot": f"@{Config.BOT_TOKEN.split(':')[0]}"
        })
    finally:
        db.close()

def run_flask():
    """Ejecutar servidor Flask"""
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

# Handlers principales
async def start(update: Update, context):
    """Comando /start"""
    user = update.effective_user
    
    # Inicializar base de datos
    database.init_database()
    db_session = database.get_session()
    
    # Registrar usuario
    from database import User
    existing_user = db_session.query(User).filter_by(user_id=user.id).first()
    
    if not existing_user:
        new_user = User(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        db_session.add(new_user)
        db_session.commit()
        logger.info(f"👤 Nuevo usuario: {user.id} (@{user.username})")
    
    # Mensaje de bienvenida
    welcome_text = """
🤖 **BOT DE BOTONERAS AUTOMÁTICAS**
✨ *Versión Replit + GitHub*

¡Bienvenido! Con este bot puedes:
✅ Agregar tus canales a botoneras automáticas
✅ Aumentar la visibilidad de tu contenido
✅ Conectar con más audiencia

🔧 **Funciones disponibles:**
• Agregar canales nuevos
• Solicitar aprobación automática
• Unirse a botoneras existentes
• Panel de administración

📌 **Comandos rápidos:**
/start - Menú principal
/help - Ayuda detallada
/mychannels - Ver tus canales
/addchannel - Agregar un canal
/stats - Estadísticas del bot

👑 **Admin:** @TikTokSMMPanel
    """
    
    is_admin = user.id in Config.ADMIN_IDS
    
    if is_admin:
        welcome_text += "\n\n🎯 **Tienes acceso al panel de administrador**"
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=keyboards.main_menu_keyboard(is_admin),
        parse_mode='HTML'
    )
    
    db_session.close()

async def help_command(update: Update, context):
    """Comando /help"""
    help_text = f"""
📚 **GUÍA COMPLETA DEL BOT**

🤔 **¿Qué hace este bot?**
Este bot automatiza la creación y gestión de botoneras para canales de Telegram.

🚀 **¿Cómo empezar?**
1. Agrega @{context.bot.username} como administrador de tu canal
2. Otorga los siguientes permisos:
   • ✅ Enviar mensajes
   • ✅ Editar mensajes
   • ✅ Fijar mensajes
   • ✅ Invitar usuarios
3. Envía el enlace de tu canal
4. Espera la aprobación del admin
5. ¡Listo! Tu canal aparecerá en las botoneras

⚡ **Funciones para usuarios:**
• Agregar múltiples canales
• Ver estadísticas de cada canal
• Solicitar nuevas botoneras
• Notificaciones de aprobación

👑 **Funciones para administradores:**
• Crear/editar botoneras
• Aprobar/rechazar canales
• Enviar mensajes globales
• Ver estadísticas detalladas
• Configurar userbot automático

🔧 **Comandos disponibles:**
/start - Menú principal
/help - Esta guía
/mychannels - Tus canales
/addchannel - Agregar canal
/stats - Estadísticas
/settings - Configuración (admin)

🆘 **Soporte:** @TikTokSMMPanel
    """
    await update.message.reply_text(help_text, parse_mode='HTML')

async def mychannels_command(update: Update, context):
    """Comando /mychannels"""
    from database import Channel
    
    user_id = update.effective_user.id
    db_session = database.get_session()
    
    channels = db_session.query(Channel).filter_by(owner_id=user_id).all()
    
    if not channels:
        await update.message.reply_text(
            "📭 **No tienes canales registrados**\n\n"
            "Usa /addchannel para agregar tu primer canal.",
            parse_mode='HTML'
        )
    else:
        text = "📢 **TUS CANALES**\n\n"
        for i, channel in enumerate(channels, 1):
            status = "✅ Aprobado" if channel.is_approved else "⏳ Pendiente"
            text += f"**{i}. {channel.channel_title}**\n"
            text += f"   👥 Miembros: {channel.members_count:,}\n"
            text += f"   📊 Estado: {status}\n"
            if channel.channel_username:
                text += f"   🔗 @{channel.channel_username}\n"
            text += f"   📅 Agregado: {channel.added_date.strftime('%d/%m/%Y')}\n\n"
        
        await update.message.reply_text(text, parse_mode='HTML')
    
    db_session.close()

async def addchannel_command(update: Update, context):
    """Comando /addchannel"""
    await update.message.reply_text(
        f"📝 **AGREGAR NUEVO CANAL**\n\n"
        f"**Paso 1:** Agrega @{context.bot.username} como administrador\n"
        f"**Paso 2:** Otorga todos los permisos de mensaje\n"
        f"**Paso 3:** Envía el enlace de tu canal\n\n"
        f"📌 **Formatos aceptados:**\n"
        f"• @username\n"
        f"• https://t.me/username\n"
        f"• https://telegram.me/username\n\n"
        f"⚠️ **Permisos requeridos:**\n"
        f"✅ Enviar mensajes\n✅ Editar mensajes\n✅ Fijar mensajes\n✅ Invitar usuarios",
        parse_mode='HTML'
    )

async def stats_command(update: Update, context):
    """Comando /stats"""
    from database import User, Channel, ButtonSet
    
    user_id = update.effective_user.id
    is_admin = user_id in Config.ADMIN_IDS
    
    db_session = database.get_session()
    
    total_users = db_session.query(User).count()
    total_channels = db_session.query(Channel).filter_by(is_approved=True).count()
    pending_channels = db_session.query(Channel).filter_by(is_approved=False).count()
    total_button_sets = db_session.query(ButtonSet).filter_by(is_active=True).count()
    
    stats_text = f"""
📊 **ESTADÍSTICAS DEL BOT**

👥 **Usuarios totales:** {total_users:,}
📢 **Canales aprobados:** {total_channels:,}
⏳ **Canales pendientes:** {pending_channels:,}
📌 **Botoneras activas:** {total_button_sets:,}

🤖 **Bot:** @{context.bot.username}
🌐 **Plataforma:** Replit + GitHub
    """
    
    if is_admin:
        stats_text += f"\n👑 **ID Admin:** {user_id}"
    
    await update.message.reply_text(stats_text, parse_mode='HTML')
    db_session.close()

async def settings_command(update: Update, context):
    """Comando /settings (solo admin)"""
    user_id = update.effective_user.id
    
    if user_id not in Config.ADMIN_IDS:
        await update.message.reply_text(
            "❌ **Acceso denegado**\n\n"
            "Solo los administradores pueden acceder a esta configuración.",
            parse_mode='HTML'
        )
        return
    
    await update.message.reply_text(
        "⚙️ **PANEL DE CONFIGURACIÓN**\n\n"
        "Selecciona una opción:",
        reply_markup=keyboards.admin_panel_keyboard(),
        parse_mode='HTML'
    )

def setup_application():
    """Configurar aplicación del bot"""
    logger.info("🔄 Inicializando aplicación del bot...")
    
    # Validar configuración
    Config.validate()
    
    # Crear aplicación
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Agregar handlers de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("mychannels", mychannels_command))
    application.add_handler(CommandHandler("addchannel", addchannel_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("settings", settings_command))
    
    # Handler para callbacks
    application.add_handler(CallbackQueryHandler(handlers.handle_callback))
    
    # Handler para mensajes de texto
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handlers.handle_text_message
    ))
    
    logger.info("✅ Aplicación configurada correctamente")
    logger.info(f"🤖 Bot: @{Config.BOT_TOKEN.split(':')[0]}")
    logger.info(f"👑 Admin: {Config.ADMIN_IDS}")
    
    return application

async def shutdown(signal, loop, application):
    """Manejar apagado limpio"""
    logger.info(f"Recibida señal {signal.name}...")
    
    # Detener el bot
    if application:
        await application.shutdown()
        await application.updater.stop()
        await application.stop()
    
    # Cancelar todas las tareas
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    
    logger.info("Cancelando tareas pendientes...")
    await asyncio.gather(*tasks, return_exceptions=True)
    
    loop.stop()
    logger.info("👋 Bot apagado correctamente")

def main():
    """Función principal"""
    logger.info("🚀 INICIANDO BOT DE BOTONERAS AUTOMÁTICAS")
    logger.info("=" * 50)
    
    try:
        # Validar configuración
        Config.validate()
        
        # Inicializar base de datos
        database.init_database()
        logger.info("💾 Base de datos inicializada")
        
        # Iniciar servidor Flask en segundo plano (para Replit)
        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info(f"🌐 Servidor Flask iniciado en puerto {Config.PORT}")
        
        # Configurar señal para apagado limpio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Crear aplicación
        application = setup_application()
        
        # Configurar manejadores de señales
        signals = (signal.SIGTERM, signal.SIGINT)
        for s in signals:
            loop.add_signal_handler(
                s, 
                lambda s=s: asyncio.create_task(shutdown(s, loop, application))
            )
        
        # Iniciar polling
        logger.info("🔄 Iniciando polling del bot...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
        
    except Exception as e:
        logger.error(f"❌ ERROR CRÍTICO: {str(e)}")
        logger.exception("Detalles del error:")
        sys.exit(1)

if __name__ == "__main__":
    main()
