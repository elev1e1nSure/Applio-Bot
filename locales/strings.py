"""
Localization strings for the bot.
Supports English (EN) and Russian (RU).
"""
from typing import Dict

# Language codes
LANG_EN = "en"
LANG_RU = "ru"

# Available languages
AVAILABLE_LANGUAGES = {
    LANG_EN: "English",
    LANG_RU: "Русский"
}

# String dictionaries
STRINGS: Dict[str, Dict[str, str]] = {
    LANG_EN: {
        # Welcome and start
        "welcome": "👋 <b>Welcome to Applio Bot!</b>\n\n"
                   "This bot allows you to submit applications. "
                   "Use /apply to start the application process.\n\n"
                   "Use /language to change your language settings.",
        "start_instructions": "📋 <b>How to use:</b>\n\n"
                              "1. Use /apply to submit a new application\n"
                              "2. Use /language to change language\n"
                              "3. Wait for admin review\n\n"
                              "Your application will be reviewed by an administrator.",
        
        # Language selection
        "language_selected": "✅ Language changed to English",
        "select_language": "🌐 <b>Select your language:</b>",
        "language_changed": "✅ Language has been changed successfully!",
        
        # Application process
        "apply_start": "<b>📝 Application Submission</b>\n\n"
                       "Thank you for deciding to submit an application!\n\n"
                       "You will go through 3 quick steps to provide the necessary information.\n\n"
                       "➡️ Please prepare the following:\n\n"
                       "1. Your Full Name\n"
                       "2. Contact Information (Email/Phone)\n"
                       "3. Purpose of the Request\n\n"
                       "To start, please enter your name below.",
        "step_2_of_3": "<b>📝 Step 2 of 3</b>\n\n"
                       "Thank you! Now please provide your contact information.\n\n"
                       "➡️ Please enter your <b>contact information</b>:\n"
                       "(Email, Phone, or Telegram username)\n\n"
                       "💡 <i>Or click the button below to use your Telegram account.</i>",
        "step_3_of_3": "<b>📝 Step 3 of 3</b>\n\n"
                       "Almost done! Please describe the purpose of your request.\n\n"
                       "➡️ Please enter the <b>purpose</b> of your application:",
        "enter_name": "👤 Please enter your <b>name</b>:",
        "enter_contact": "📞 Please enter your <b>contact information</b> (phone, email, or Telegram username):",
        "enter_purpose": "📄 Please describe the <b>purpose</b> of your application:",
        "application_received": "✅ <b>Application Received!</b>\n\n"
                                "Your application has been submitted successfully. "
                                "An administrator will review it shortly.\n\n"
                                "You will be notified once a decision is made.",
        "application_cancelled": "❌ Application submission cancelled.",
        "cooldown_active": "⏳ <b>Please wait</b>\n\n"
                           "You can submit a new application in {seconds} seconds.\n"
                           "This is to prevent spam.",
        
        # Errors
        "error_occurred": "❌ An error occurred. Please try again.",
        "invalid_input": "⚠️ Invalid input. Please try again.",
        "error_name_format": "⚠️ Please enter your full name (letters, spaces, hyphen).",
        "error_contact_format": "⚠️ Please provide a valid email, phone number, or Telegram username.",
        "error_purpose_format": "⚠️ Please provide a more detailed purpose (at least 10 characters).",
        "cancel": "Cancel",
        "back": "Back",
        
        # Admin notifications
        "application_approved": "✅ <b>Your application has been approved!</b>\n\n"
                                "Thank you for your submission.",
        "application_rejected": "❌ <b>Your application has been rejected.</b>\n\n"
                                "If you have questions, please contact the administrator.",
        
        # Admin panel
        "access_denied": "❌ Access denied. This command is only available for administrators.",
        "admin_panel_title": "🔐 <b>Admin Panel</b>\n\nSelect an action:",
        "admin_error": "❌ An error occurred while opening admin panel. Please try again.",
        "admin_stats_error": "❌ An error occurred while fetching statistics. Please try again.",
        "invalid_language": "Invalid language",
        "app_not_found": "Application not found.",
        "app_already_processed": "Application already processed.",
        "admin_panel_closed": "Admin panel closed.",
        "no_pending_apps": "📋 <b>No Pending Applications</b>\n\nAll applications have been reviewed.",
        "app_approved_title": "✅ <b>Application #{id} Approved</b>",
        "app_rejected_title": "❌ <b>Application #{id} Rejected</b>",
        "new_application_title": "📋 <b>New Application #{id}</b>",
        "user_notified": "User has been notified.",
        "bot_statistics": "📊 <b>Bot Statistics</b>",
        "users_overview": "👥 <b>Users Overview</b>",
        "total_registered_users": "Total registered users:",
        "applications_overview": "📋 <b>Applications Overview</b>",
        "total_applications_submitted": "Total applications submitted:",
        "status_breakdown": "<b>Application Status Breakdown:</b>",
        "pending_review": "⏳ Pending review:",
        "approved": "✅ Approved:",
        "rejected": "❌ Rejected:",
        "field_name": "Name",
        "field_contact": "Contact",
        "field_purpose": "Purpose",
        "field_submitted": "Submitted",
        "total_pending": "Total pending",
        
        # Admin buttons
        "btn_new_applications": "📋 New Applications",
        "btn_show_stats": "📊 Show Stats",
        "btn_exit": "❌ Exit",
        "btn_approve": "✅ Approve",
        "btn_reject": "❌ Reject",
        "btn_back_to_list": "🔙 Back to List",
        "btn_back_to_menu": "🔙 Back to Menu",
        
        # User buttons
        "btn_continue_telegram": "📱 Continue with Telegram",
        
        # Admin welcome
        "admin_welcome": "🔐 <b>Admin Notice</b>\n\n"
                         "You have administrator privileges.\n"
                         "Use /admin to open the admin panel.",
        
        # Applications list
        "applications_list_title": "📋 <b>Pending Applications</b>\n\n"
                                   "Select an application to review:",
        "app_list_item": "{num}. {name}",
        "view_app_title": "📋 <b>Application #{id}</b>",
        "processed_by_admin": "Processed by Admin ID: {admin_id}",
        
        # Admin management
        "btn_manage_admins": "👥 Manage Admins",
        "admin_management_title": "👥 <b>Admin Management</b>\n\n"
                                  "Current administrators:",
        "admin_list_main": "👑 {user_id} (Main Admin)",
        "admin_list_item": "👤 {user_id}",
        "no_additional_admins": "No additional administrators.",
        "btn_add_admin": "➕ Add Admin",
        "btn_remove_admin": "➖ Remove Admin",
        "add_admin_prompt": "👤 <b>Add New Admin</b>\n\n"
                            "Send the Telegram User ID of the new administrator.\n\n"
                            "💡 <i>To get User ID, use @getmy_idbot</i>",
        "remove_admin_prompt": "👤 <b>Remove Admin</b>\n\n"
                               "Select an administrator to remove:",
        "admin_added": "✅ Admin <b>{user_id}</b> has been added successfully.",
        "admin_removed": "✅ Admin <b>{user_id}</b> has been removed.",
        "admin_already_exists": "⚠️ This user is already an administrator.",
        "admin_invalid_id": "⚠️ Invalid User ID. Please enter a valid number.",
        "admin_cannot_remove_main": "⚠️ Cannot remove the main administrator.",
        "admin_not_found": "⚠️ Administrator not found.",
    },
    LANG_RU: {
        # Welcome and start
        "welcome": "👋 <b>Добро пожаловать в Applio Bot!</b>\n\n"
                   "Этот бот позволяет подавать заявки. "
                   "Используйте /apply, чтобы начать процесс подачи заявки.\n\n"
                   "Используйте /language, чтобы изменить настройки языка.",
        "start_instructions": "📋 <b>Как использовать:</b>\n\n"
                              "1. Используйте /apply для подачи новой заявки\n"
                              "2. Используйте /language для смены языка\n"
                              "3. Дождитесь проверки администратором\n\n"
                              "Ваша заявка будет рассмотрена администратором.",
        
        # Language selection
        "language_selected": "✅ Язык изменен на Русский",
        "select_language": "🌐 <b>Выберите ваш язык:</b>",
        "language_changed": "✅ Язык успешно изменен!",
        
        # Application process
        "apply_start": "<b>📝 Подача заявки</b>\n\n"
                       "Спасибо, что решили подать заявку!\n\n"
                       "Вы пройдете 3 быстрых шага, чтобы предоставить необходимую информацию.\n\n"
                       "➡️ Пожалуйста, подготовьте следующее:\n\n"
                       "1. Ваше полное имя\n"
                       "2. Контактная информация (Email/Телефон)\n"
                       "3. Цель запроса\n\n"
                       "Для начала, пожалуйста, введите ваше имя ниже.",
        "step_2_of_3": "<b>📝 Шаг 2 из 3</b>\n\n"
                       "Спасибо! Теперь, пожалуйста, предоставьте вашу контактную информацию.\n\n"
                       "➡️ Пожалуйста, введите вашу <b>контактную информацию</b>:\n"
                       "(Email, Телефон или Telegram username)\n\n"
                       "💡 <i>Или нажмите кнопку ниже, чтобы использовать ваш Telegram аккаунт.</i>",
        "step_3_of_3": "<b>📝 Шаг 3 из 3</b>\n\n"
                       "Почти готово! Пожалуйста, опишите цель вашего запроса.\n\n"
                       "➡️ Пожалуйста, введите <b>цель</b> вашей заявки:",
        "enter_name": "👤 Пожалуйста, введите ваше <b>имя</b>:",
        "enter_contact": "📞 Пожалуйста, введите вашу <b>контактную информацию</b> (телефон, email или Telegram username):",
        "enter_purpose": "📄 Пожалуйста, опишите <b>цель</b> вашей заявки:",
        "application_received": "✅ <b>Заявка получена!</b>\n\n"
                                "Ваша заявка успешно отправлена.\n\n"
                                "Администратор рассмотрит её в ближайшее время.\n\n"
                                "Вы будете уведомлены, когда будет принято решение.",
        "application_cancelled": "❌ Подача заявки отменена.",
        "cooldown_active": "⏳ <b>Пожалуйста, подождите</b>\n\n"
                           "Вы можете подать новую заявку через {seconds} секунд.\n"
                           "Это сделано для предотвращения спама.",
        
        # Errors
        "error_occurred": "❌ Произошла ошибка. Пожалуйста, попробуйте снова.",
        "invalid_input": "⚠️ Неверный ввод. Пожалуйста, попробуйте снова.",
        "error_name_format": "⚠️ Пожалуйста, введите полное имя (буквы, пробелы, дефис).",
        "error_contact_format": "⚠️ Укажите корректный email, телефон или Telegram username.",
        "error_purpose_format": "⚠️ Пожалуйста, опишите цель подробнее (не менее 10 символов).",
        "cancel": "Отмена",
        "back": "Назад",
        
        # Admin notifications
        "application_approved": "✅ <b>Ваша заявка одобрена!</b>\n\n"
                                "Спасибо за вашу заявку.",
        "application_rejected": "❌ <b>Ваша заявка отклонена.</b>\n\n"
                                "Если у вас есть вопросы, пожалуйста, свяжитесь с администратором.",
        
        # Admin panel
        "access_denied": "❌ Доступ запрещен. Эта команда доступна только администраторам.",
        "admin_panel_title": "🔐 <b>Панель администратора</b>\n\nВыберите действие:",
        "admin_error": "❌ Произошла ошибка при открытии панели администратора. Пожалуйста, попробуйте снова.",
        "admin_stats_error": "❌ Произошла ошибка при получении статистики. Пожалуйста, попробуйте снова.",
        "invalid_language": "Неверный язык",
        "app_not_found": "Заявка не найдена.",
        "app_already_processed": "Заявка уже обработана.",
        "admin_panel_closed": "Панель администратора закрыта.",
        "no_pending_apps": "📋 <b>Нет ожидающих заявок</b>\n\nВсе заявки были рассмотрены.",
        "app_approved_title": "✅ <b>Заявка #{id} одобрена</b>",
        "app_rejected_title": "❌ <b>Заявка #{id} отклонена</b>",
        "new_application_title": "📋 <b>Новая заявка #{id}</b>",
        "user_notified": "Пользователь уведомлен.",
        "bot_statistics": "📊 <b>Статистика бота</b>",
        "users_overview": "👥 <b>Обзор пользователей</b>",
        "total_registered_users": "Всего зарегистрированных пользователей:",
        "applications_overview": "📋 <b>Обзор заявок</b>",
        "total_applications_submitted": "Всего подано заявок:",
        "status_breakdown": "<b>Разбивка по статусам заявок:</b>",
        "pending_review": "⏳ Ожидают рассмотрения:",
        "approved": "✅ Одобрено:",
        "rejected": "❌ Отклонено:",
        "field_name": "Имя",
        "field_contact": "Контакты",
        "field_purpose": "Цель",
        "field_submitted": "Подано",
        "total_pending": "Всего ожидает",
        
        # Admin buttons
        "btn_new_applications": "📋 Новые заявки",
        "btn_show_stats": "📊 Показать статистику",
        "btn_exit": "❌ Выход",
        "btn_approve": "✅ Одобрить",
        "btn_reject": "❌ Отклонить",
        "btn_back_to_list": "🔙 Назад к списку",
        "btn_back_to_menu": "🔙 Назад в меню",
        
        # User buttons
        "btn_continue_telegram": "📱 Продолжить с Telegram",
        
        # Admin welcome
        "admin_welcome": "🔐 <b>Уведомление для администратора</b>\n\n"
                         "У вас есть права администратора.\n"
                         "Используйте /admin для открытия панели управления.",
        
        # Applications list
        "applications_list_title": "📋 <b>Ожидающие заявки</b>\n\n"
                                   "Выберите заявку для просмотра:",
        "app_list_item": "{num}. {name}",
        "view_app_title": "📋 <b>Заявка #{id}</b>",
        "processed_by_admin": "Обработано администратором ID: {admin_id}",
        
        # Admin management
        "btn_manage_admins": "👥 Управление админами",
        "admin_management_title": "👥 <b>Управление администраторами</b>\n\n"
                                  "Текущие администраторы:",
        "admin_list_main": "👑 {user_id} (Главный админ)",
        "admin_list_item": "👤 {user_id}",
        "no_additional_admins": "Дополнительных администраторов нет.",
        "btn_add_admin": "➕ Добавить админа",
        "btn_remove_admin": "➖ Удалить админа",
        "add_admin_prompt": "👤 <b>Добавить нового админа</b>\n\n"
                            "Отправьте Telegram User ID нового администратора.\n\n"
                            "💡 <i>Чтобы узнать User ID, используйте @getmy_idbot</i>",
        "remove_admin_prompt": "👤 <b>Удалить админа</b>\n\n"
                               "Выберите администратора для удаления:",
        "admin_added": "✅ Администратор <b>{user_id}</b> успешно добавлен.",
        "admin_removed": "✅ Администратор <b>{user_id}</b> удалён.",
        "admin_already_exists": "⚠️ Этот пользователь уже является администратором.",
        "admin_invalid_id": "⚠️ Неверный User ID. Введите корректное число.",
        "admin_cannot_remove_main": "⚠️ Невозможно удалить главного администратора.",
        "admin_not_found": "⚠️ Администратор не найден.",
    }
}


def get_string(language: str, key: str, **kwargs) -> str:
    """
    Get localized string by key and language.
    
    Args:
        language: Language code (en/ru)
        key: String key
        **kwargs: Format arguments for string formatting
        
    Returns:
        Localized string
    """
    lang = language if language in STRINGS else LANG_EN
    string = STRINGS[lang].get(key, STRINGS[LANG_EN].get(key, key))
    
    if kwargs:
        try:
            return string.format(**kwargs)
        except KeyError:
            return string
    
    return string

