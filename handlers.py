from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import logging
import re
from config import Config
import database
import keyboards

logger = logging.getLogger(__name__)

async def handle_callback(update: Update, context: CallbackContext):
    """Manejar callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    logger.info(f"📞 Callback: {data} de {user_id}")
    
    # Menú principal
    if data == "main_menu":
        is_admin = user_id in Config.ADMIN_IDS
        await query.edit_message_text(
            "🏠 **Menú Principal**\n\nSelecciona una opción:",
            reply_markup=keyboards.main_menu_keyboard(is_admin),
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Panel admin
    elif data == "admin_panel":
        if user_id not in Config.ADMIN_IDS:
            await query.edit_message_text("❌ Acceso denegado.")
            return
        
        await query.edit_message_text(
            "👑 **Panel de Administrador**\n\nSelecciona una opción:",
            reply_markup=keyboards.admin_panel_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Agregar canal
    elif data == "add_channel":
        await query.edit_message_text(
            f"📝 **Para agregar un canal:**\n\n"
            f"1. Agrega @{context.bot.username} como admin\n"
            f"2. Otorga todos los permisos\n"
            f"3. Envía el enlace aquí\n\n"
            f"📌 Formatos: @username o https://t.me/username",
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Mis canales
    elif data == "my_channels":
        from database import Channel
        
        db = database.get_session()
        channels = db.query(Channel).filter_by(owner_id=user_id).all()
        
        if not channels:
            await query.edit_message_text(
                "📭 No tienes canales registrados.",
                reply_markup=keyboards.back_button()
            )
        else:
            text = "📢 **Tus Canales:**\n\n"
            for i, channel in enumerate(channels, 1):
                status = "✅ Aprobado" if channel.is_approved else "⏳ Pendiente"
                text += f"{i}. **{channel.channel_title}**\n"
                text += f"   👥 {channel.members_count} miembros\n"
                text += f"   📊 {status}\n\n"
            
            await query.edit_message_text(
                text,
                reply_markup=keyboards.back_button(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        db.close()
    
    # Ayuda
    elif data == "help":
        help_text = """
📚 **Ayuda del Bot**

🤖 **Funciones principales:**
• Agregar canales a botoneras
• Gestionar múltiples canales
• Panel de administración

🔧 **Cómo usar:**
1. Agrega el bot como admin
2. Envía enlace de tu canal
3. Espera aprobación
4. Selecciona botoneras

👑 **Admin:** @TikTokSMMPanel
"""
        await query.edit_message_text(
            help_text,
            reply_markup=keyboards.back_button(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Botoneras admin
    elif data == "admin_button_sets":
        if user_id not in Config.ADMIN_IDS:
            await query.edit_message_text("❌ Acceso denegado.")
            return
        
        await query.edit_message_text(
            "📌 **Gestión de Botoneras**\n\nSelecciona:",
            reply_markup=keyboards.button_sets_submenu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Crear botonera
    elif data == "create_button_set":
        if user_id not in Config.ADMIN_IDS:
            await query.edit_message_text("❌ Acceso denegado.")
            return
        
        await query.edit_message_text(
            "🚧 **Función en desarrollo**\n\n"
            "Próximamente podrás crear botoneras aquí.",
            reply_markup=keyboards.back_button("admin_button_sets"),
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Estadísticas admin
    elif data == "admin_stats":
        if user_id not in Config.ADMIN_IDS:
            await query.edit_message_text("❌ Acceso denegado.")
            return
        
        from database import User, Channel, ButtonSet
        
        db = database.get_session()
        
        total_users = db.query(User).count()
        total_channels = db.query(Channel).filter_by(is_approved=True).count()
        total_button_sets = db.query(ButtonSet).filter_by(is_active=True).count()
        pending_channels = db.query(Channel).filter_by(is_approved=False).count()
        
        stats_text = f"""
📊 **Estadísticas Admin**

👥 Usuarios: {total_users}
📢 Canales aprobados: {total_channels}
⏳ Pendientes: {pending_channels}
📌 Botoneras: {total_button_sets}

🌐 Plataforma: Replit
"""
        
        await query.edit_message_text(
            stats_text,
            reply_markup=keyboards.back_button("admin_panel"),
            parse_mode=ParseMode.MARKDOWN
        )
        
        db.close()
    
    # Ajustes admin
    elif data == "admin_settings":
        if user_id not in Config.ADMIN_IDS:
            await query.edit_message_text("❌ Acceso denegado.")
            return
        
        from database import AdminSettings
        
        db = database.get_session()
        settings = db.query(AdminSettings).first()
        
        settings_text = f"""
⚙️ **Ajustes del Bot**

🌐 Zona: {settings.timezone if settings else 'UTC'}
🤖 Userbot: {'✅' if Config.API_ID else '❌'}
📱 Teléfono: {Config.PHONE_NUMBER[:10] if Config.PHONE_NUMBER else 'No'}
"""
        
        await query.edit_message_text(
            settings_text,
            reply_markup=keyboards.back_button("admin_panel"),
            parse_mode=ParseMode.MARKDOWN
        )
        
        db.close()
    
    # Canales pendientes
    elif data == "pending_channels":
        if user_id not in Config.ADMIN_IDS:
            await query.edit_message_text("❌ Acceso denegado.")
            return
        
        from database import Channel
        
        db = database.get_session()
        channels = db.query(Channel).filter_by(is_approved=False).all()
        
        if not channels:
            await query.edit_message_text(
                "✅ No hay canales pendientes.",
                reply_markup=keyboards.back_button("admin_panel")
            )
        else:
            text = "⏳ **Canales Pendientes:**\n\n"
            for i, channel in enumerate(channels, 1):
                text += f"{i}. **{channel.channel_title}**\n"
                text += f"   👥 {channel.members_count} miembros\n\n"
            
            await query.edit_message_text(
                text,
                reply_markup=keyboards.back_button("admin_panel"),
                parse_mode=ParseMode.MARKDOWN
            )
        
        db.close()
    
    # Aprobar canal
    elif data.startswith("approve_"):
        if user_id not in Config.ADMIN_IDS:
            await query.edit_message_text("❌ Acceso denegado.")
            return
        
        channel_id = int(data.split("_")[1])
        
        from database import Channel
        from datetime import datetime
        
        db = database.get_session()
        channel = db.query(Channel).get(channel_id)
        
        if channel:
            channel.is_approved = True
            channel.approved_date = datetime.utcnow()
            db.commit()
            
            # Notificar al dueño
            try:
                await context.bot.send_message(
                    chat_id=channel.owner_id,
                    text=f"✅ **Canal aprobado!**\n\n"
                         f"**{channel.channel_title}**\n"
                         f"Ahora aparecerá en las botoneras.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
            
            await query.edit_message_text(
                f"✅ **Canal aprobado:** {channel.channel_title}",
                reply_markup=keyboards.back_button("pending_channels"),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                "❌ Canal no encontrado.",
                reply_markup=keyboards.back_button("pending_channels")
            )
        
        db.close()
    
    else:
        await query.edit_message_text(
            "⚠️ Función en desarrollo.",
            reply_markup=keyboards.back_button()
        )

async def handle_text_message(update: Update, context: CallbackContext):
    """Manejar mensajes de texto"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Verificar si es enlace de canal
    if re.match(r'(@\w+|https?://t\.me/\w+|https?://telegram\.me/\w+)', text):
        await process_channel_link(update, context, text)
    else:
        await update.message.reply_text(
            f"📝 Envía el enlace de tu canal.\n\n"
            f"Formatos aceptados:\n"
            f"• @username\n"
            f"• https://t.me/username\n\n"
            f"Primero agrega @{context.bot.username} como administrador.",
            parse_mode=ParseMode.MARKDOWN
        )

async def process_channel_link(update: Update, context: CallbackContext, link: str):
    """Procesar enlace de canal"""
    # Extraer username
    username = link.replace('https://t.me/', '')\
                   .replace('https://telegram.me/', '')\
                   .replace('@', '')\
                   .split('/')[0]
    
    user_id = update.effective_user.id
    
    from database import Channel
    from datetime import datetime
    
    db = database.get_session()
    
    # Verificar si ya existe
    existing = db.query(Channel).filter_by(channel_username=username).first()
    
    if existing:
        await update.message.reply_text(
            f"⚠️ **Canal ya registrado**\n\n"
            f"**{existing.channel_title}**\n"
            f"Estado: {'✅ Aprobado' if existing.is_approved else '⏳ Pendiente'}",
            parse_mode=ParseMode.MARKDOWN
        )
        db.close()
        return
    
    # Crear nuevo canal
    new_channel = Channel(
        channel_username=username,
        channel_title=f"@{username}",
        owner_id=user_id,
        added_date=datetime.utcnow()
    )
    
    db.add(new_channel)
    db.commit()
    channel_id = new_channel.id
    
    # Notificar al admin
    is_admin = user_id in Config.ADMIN_IDS
    
    if not is_admin:
        try:
            for admin_id in Config.ADMIN_IDS:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"📨 **Nuevo canal pendiente**\n\n"
                         f"**Canal:** @{username}\n"
                         f"**Dueño:** {user_id}\n"
                         f"**Fecha:** {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}",
                    reply_markup=keyboards.approve_channel_keyboard(channel_id),
                    parse_mode=ParseMode.MARKDOWN
                )
        except:
            pass
    
    await update.message.reply_text(
        f"✅ **Canal registrado**\n\n"
        f"**@{username}** ha sido añadido a la lista.\n\n"
        f"📊 **Estado:** {'✅ Aprobado automáticamente' if is_admin else '⏳ Pendiente de aprobación'}\n\n"
        f"El administrador revisará tu solicitud pronto.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    db.close()
