from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard(is_admin=False):
    if is_admin:
        keyboard = [
            [InlineKeyboardButton("👑 Panel Admin", callback_data="admin_panel")],
            [InlineKeyboardButton("➕ Agregar Canal", callback_data="add_channel")],
            [InlineKeyboardButton("📋 Mis Canales", callback_data="my_channels")],
            [InlineKeyboardButton("ℹ️ Ayuda", callback_data="help")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("➕ Agregar Canal", callback_data="add_channel")],
            [InlineKeyboardButton("📋 Mis Canales", callback_data="my_channels")],
            [InlineKeyboardButton("ℹ️ Ayuda", callback_data="help")]
        ]
    return InlineKeyboardMarkup(keyboard)

def admin_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton("📌 Botoneras", callback_data="admin_button_sets")],
        [InlineKeyboardButton("📢 Mensaje Global", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📊 Estadísticas", callback_data="admin_stats")],
        [InlineKeyboardButton("⚙️ Ajustes", callback_data="admin_settings")],
        [InlineKeyboardButton("👥 Canales Pendientes", callback_data="pending_channels")],
        [InlineKeyboardButton("🔙 Menú Principal", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def button_sets_submenu():
    keyboard = [
        [InlineKeyboardButton("➕ Crear Botonera", callback_data="create_button_set")],
        [InlineKeyboardButton("✏️ Editar Botoneras", callback_data="edit_button_sets")],
        [InlineKeyboardButton("🔙 Atrás", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def edit_button_set_keyboard(button_set_id):
    keyboard = [
        [InlineKeyboardButton("🕐 Horario", callback_data=f"edit_horario_{button_set_id}")],
        [InlineKeyboardButton("🔄 Rotar Botones", callback_data=f"edit_rotate_{button_set_id}")],
        [InlineKeyboardButton("📅 Días de Envío", callback_data=f"edit_days_{button_set_id}")],
        [InlineKeyboardButton("🖼️ Medios", callback_data=f"edit_media_{button_set_id}")],
        [InlineKeyboardButton("🔘 Botones Extras", callback_data=f"edit_extras_{button_set_id}")],
        [InlineKeyboardButton("📝 Descripción", callback_data=f"edit_desc_{button_set_id}")],
        [InlineKeyboardButton("👥 Miembros", callback_data=f"edit_members_{button_set_id}")],
        [InlineKeyboardButton("📌 Fijar", callback_data=f"edit_pin_{button_set_id}")],
        [InlineKeyboardButton("❌ Eliminar", callback_data=f"delete_set_{button_set_id}")],
        [InlineKeyboardButton("🔙 Atrás", callback_data="edit_button_sets")]
    ]
    return InlineKeyboardMarkup(keyboard)

def approve_channel_keyboard(channel_id):
    keyboard = [
        [
            InlineKeyboardButton("✅ Aprobar", callback_data=f"approve_{channel_id}"),
            InlineKeyboardButton("❌ Rechazar", callback_data=f"reject_{channel_id}")
        ],
        [InlineKeyboardButton("👁️ Ver Info", callback_data=f"view_channel_{channel_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def button_sets_list_keyboard(button_sets, channel_id=None):
    keyboard = []
    for btn_set in button_sets:
        text = f"{btn_set.name} ({btn_set.min_members}-{btn_set.max_members} miembros)"
        if channel_id:
            callback_data = f"select_bs_{btn_set.id}_{channel_id}"
        else:
            callback_data = f"edit_bs_{btn_set.id}"
        keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton("🔙 Atrás", callback_data="admin_panel")])
    return InlineKeyboardMarkup(keyboard)

def yes_no_keyboard(action):
    keyboard = [
        [
            InlineKeyboardButton("✅ Sí", callback_data=f"{action}_yes"),
            InlineKeyboardButton("❌ No", callback_data=f"{action}_no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button(target="main_menu"):
    keyboard = [[InlineKeyboardButton("🔙 Atrás", callback_data=target)]]
    return InlineKeyboardMarkup(keyboard)
