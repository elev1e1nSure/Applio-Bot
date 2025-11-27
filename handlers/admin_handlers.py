"""
Admin handlers for admin panel.
"""
import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_ID
from db.manager import (
    add_admin,
    get_added_admins,
    is_admin,
    is_main_admin,
    remove_admin,
)
from db.models import Application, ApplicationStatus, User
from keyboards.admin_kb import (
    get_admin_main_keyboard,
    get_admin_management_keyboard,
    get_admin_remove_keyboard,
    get_application_actions_keyboard,
    get_applications_list_keyboard,
    get_back_to_menu_keyboard,
)
from locales.strings import LANG_EN, get_string
from states.application_states import AdminStates

router = Router()
logger = logging.getLogger(__name__)


async def safe_edit_message(message: Message, text: str, reply_markup=None):
    """Safely edit a message, fallback to sending a new one if editing fails."""
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        await message.answer(text, reply_markup=reply_markup)


async def get_admin_language(session: AsyncSession, user_id: int = None) -> str:
    """Get admin's language preference."""
    target_id = user_id or ADMIN_ID
    result = await session.execute(
        select(User).where(User.user_id == target_id)
    )
    user = result.scalar_one_or_none()
    return user.language if user else LANG_EN


async def get_admin_display(bot: Bot, user_id: int) -> str:
    """Return display value for admin (username with @ or fallback to ID)."""
    try:
        chat = await bot.get_chat(user_id)
        if chat.username:
            return f"@{chat.username}"
    except Exception:
        pass
    return str(user_id)


@router.message(Command("admin"))
async def cmd_admin(message: Message, session: AsyncSession):
    """Handle /admin command."""
    user_id = message.from_user.id
    logger.info(f"Admin command received from user {user_id}, ADMIN_ID={ADMIN_ID}")
    
    language = await get_admin_language(session, user_id)
    
    if not await is_admin(session, user_id):
        await message.answer(get_string(language, "access_denied"))
        return
    
    try:
        # Count pending applications
        result = await session.execute(
            select(func.count(Application.id)).where(
                Application.status == ApplicationStatus.PENDING
            )
        )
        pending_count = result.scalar() or 0
        
        await message.answer(
            get_string(language, "admin_panel_title"),
            reply_markup=get_admin_main_keyboard(
                pending_count,
                language,
                is_main_admin=await is_main_admin(user_id)
            )
        )
    except Exception as e:
        logger.error(f"Error in admin command: {e}", exc_info=True)
        await message.answer(get_string(language, "admin_error"))


@router.callback_query(F.data == "admin_menu")
async def admin_menu_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle admin menu callback."""
    user_id = callback.from_user.id
    language = await get_admin_language(session, user_id)
    
    if not await is_admin(session, user_id):
        await callback.answer(get_string(language, "access_denied"))
        return
    
    # Count pending applications
    result = await session.execute(
        select(func.count(Application.id)).where(
            Application.status == ApplicationStatus.PENDING
        )
    )
    pending_count = result.scalar() or 0
    
    await safe_edit_message(
        callback.message,
        get_string(language, "admin_panel_title"),
        reply_markup=get_admin_main_keyboard(
            pending_count,
            language,
            is_main_admin=await is_main_admin(user_id)
        )
    )
    await callback.answer()


@router.callback_query(F.data == "admin_new_apps")
async def admin_new_apps_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle new applications list callback - shows list of pending applications."""
    user_id = callback.from_user.id
    language = await get_admin_language(session, user_id)
    
    if not await is_admin(session, user_id):
        await callback.answer(get_string(language, "access_denied"))
        return
    
    # Get pending applications
    result = await session.execute(
        select(Application)
        .where(Application.status == ApplicationStatus.PENDING)
        .order_by(Application.created_at.desc())
        .limit(10)
    )
    applications = result.scalars().all()
    
    if not applications:
        await safe_edit_message(
            callback.message,
            get_string(language, "no_pending_apps"),
            reply_markup=get_back_to_menu_keyboard(language)
        )
        await callback.answer()
        return
    
    # Show list of applications
    await safe_edit_message(
        callback.message,
        get_string(language, "applications_list_title"),
        reply_markup=get_applications_list_keyboard(applications, language)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("view_app_"))
async def view_application_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle viewing a specific application."""
    user_id = callback.from_user.id
    language = await get_admin_language(session, user_id)
    
    if not await is_admin(session, user_id):
        await callback.answer(get_string(language, "access_denied"))
        return
    
    app_id = int(callback.data.split("_")[-1])
    
    # Get application
    result = await session.execute(
        select(Application).where(Application.id == app_id)
    )
    app = result.scalar_one_or_none()
    
    if not app:
        await callback.answer(get_string(language, "app_not_found"))
        return
    
    text = (
        f"{get_string(language, 'view_app_title').replace('{id}', str(app.id))}\n\n"
        f"👤 <b>{get_string(language, 'field_name')}:</b> {app.name}\n"
        f"📞 <b>{get_string(language, 'field_contact')}:</b> {app.contact}\n"
        f"📄 <b>{get_string(language, 'field_purpose')}:</b> {app.purpose}\n\n"
        f"🕐 <b>{get_string(language, 'field_submitted')}:</b> {app.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await safe_edit_message(
        callback.message,
        text,
        reply_markup=get_application_actions_keyboard(app.id, language)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_approve_"))
async def admin_approve_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle application approval."""
    user_id = callback.from_user.id
    language = await get_admin_language(session, user_id)
    
    if not await is_admin(session, user_id):
        await callback.answer(get_string(language, "access_denied"))
        return
    
    app_id = int(callback.data.split("_")[-1])
    
    # Get application
    result = await session.execute(
        select(Application).where(Application.id == app_id)
    )
    app = result.scalar_one_or_none()
    
    if not app:
        await callback.answer(get_string(language, "app_not_found"))
        return
    
    if app.status != ApplicationStatus.PENDING:
        await callback.answer(get_string(language, "app_already_processed"))
        return
    
    # Update status
    app.status = ApplicationStatus.APPROVED
    await session.commit()
    
    # Get user
    user_result = await session.execute(
        select(User).where(User.user_id == app.user_id)
    )
    user = user_result.scalar_one_or_none()
    
    # Notify user
    if user:
        language = user.language or "en"
        bot: Bot = callback.bot
        try:
            await bot.send_message(
                app.user_id,
                get_string(language, "application_approved")
            )
        except Exception:
            pass  # User blocked bot or other error
    
    # Update message with admin ID
    admin_language = await get_admin_language(session)
    approved_title = get_string(admin_language, 'app_approved_title').replace('{id}', str(app.id))
    text = (
        f"{approved_title}\n\n"
        f"👤 <b>{get_string(admin_language, 'field_name')}:</b> {app.name}\n"
        f"📞 <b>{get_string(admin_language, 'field_contact')}:</b> {app.contact}\n"
        f"📄 <b>{get_string(admin_language, 'field_purpose')}:</b> {app.purpose}\n\n"
        f"{get_string(admin_language, 'user_notified')}\n"
        f"{get_string(admin_language, 'processed_by_admin', admin_id=callback.from_user.id)}"
    )
    
    await safe_edit_message(
        callback.message,
        text,
        reply_markup=get_back_to_menu_keyboard(admin_language)
    )
    await callback.answer(get_string(admin_language, "application_approved").split("\n")[0])


@router.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle application rejection."""
    user_id = callback.from_user.id
    language = await get_admin_language(session, user_id)
    
    if not await is_admin(session, user_id):
        await callback.answer(get_string(language, "access_denied"))
        return
    
    app_id = int(callback.data.split("_")[-1])
    
    # Get application
    result = await session.execute(
        select(Application).where(Application.id == app_id)
    )
    app = result.scalar_one_or_none()
    
    if not app:
        await callback.answer(get_string(language, "app_not_found"))
        return
    
    if app.status != ApplicationStatus.PENDING:
        await callback.answer(get_string(language, "app_already_processed"))
        return
    
    # Update status
    app.status = ApplicationStatus.REJECTED
    await session.commit()
    
    # Get user
    user_result = await session.execute(
        select(User).where(User.user_id == app.user_id)
    )
    user = user_result.scalar_one_or_none()
    
    # Notify user
    if user:
        language = user.language or "en"
        bot: Bot = callback.bot
        try:
            await bot.send_message(
                app.user_id,
                get_string(language, "application_rejected")
            )
        except Exception:
            pass  # User blocked bot or other error
    
    # Update message with admin ID
    admin_language = await get_admin_language(session)
    rejected_title = get_string(admin_language, 'app_rejected_title').replace('{id}', str(app.id))
    text = (
        f"{rejected_title}\n\n"
        f"👤 <b>{get_string(admin_language, 'field_name')}:</b> {app.name}\n"
        f"📞 <b>{get_string(admin_language, 'field_contact')}:</b> {app.contact}\n"
        f"📄 <b>{get_string(admin_language, 'field_purpose')}:</b> {app.purpose}\n\n"
        f"{get_string(admin_language, 'user_notified')}\n"
        f"{get_string(admin_language, 'processed_by_admin', admin_id=callback.from_user.id)}"
    )
    
    await safe_edit_message(
        callback.message,
        text,
        reply_markup=get_back_to_menu_keyboard(admin_language)
    )
    await callback.answer(get_string(admin_language, "application_rejected").split("\n")[0])


@router.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle admin stats callback."""
    user_id = callback.from_user.id
    language = await get_admin_language(session, user_id)
    
    if not await is_admin(session, user_id):
        await callback.answer(get_string(language, "access_denied"))
        return
    
    # Get statistics
    total_apps = await session.execute(
        select(func.count(Application.id))
    )
    total = total_apps.scalar() or 0
    
    pending_apps = await session.execute(
        select(func.count(Application.id)).where(
            Application.status == ApplicationStatus.PENDING
        )
    )
    pending = pending_apps.scalar() or 0
    
    approved_apps = await session.execute(
        select(func.count(Application.id)).where(
            Application.status == ApplicationStatus.APPROVED
        )
    )
    approved = approved_apps.scalar() or 0
    
    rejected_apps = await session.execute(
        select(func.count(Application.id)).where(
            Application.status == ApplicationStatus.REJECTED
        )
    )
    rejected = rejected_apps.scalar() or 0
    
    total_users = await session.execute(
        select(func.count(User.user_id))
    )
    users = total_users.scalar() or 0
    
    # Calculate percentages
    approval_rate = (approved / total * 100) if total > 0 else 0
    rejection_rate = (rejected / total * 100) if total > 0 else 0
    
    text = (
        f"{get_string(language, 'bot_statistics')}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{get_string(language, 'users_overview')}\n"
        f"{get_string(language, 'total_registered_users')} <b>{users}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{get_string(language, 'applications_overview')}\n"
        f"{get_string(language, 'total_applications_submitted')} <b>{total}</b>\n\n"
        f"{get_string(language, 'status_breakdown')}\n\n"
        f"{get_string(language, 'pending_review')} <b>{pending}</b>\n"
        f"{get_string(language, 'approved')} <b>{approved}</b> ({approval_rate:.1f}%)\n"
        f"{get_string(language, 'rejected')} <b>{rejected}</b> ({rejection_rate:.1f}%)"
    )
    
    await safe_edit_message(
        callback.message,
        text,
        reply_markup=get_back_to_menu_keyboard(language)
    )
    await callback.answer()


@router.callback_query(F.data == "admin_exit")
async def admin_exit_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle admin exit callback."""
    language = await get_admin_language(session, callback.from_user.id)
    await callback.message.delete()
    await callback.answer(get_string(language, "admin_panel_closed"))


# ============== Admin Management Handlers ==============


@router.callback_query(F.data == "admin_manage")
async def admin_manage_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle admin management menu."""
    user_id = callback.from_user.id
    language = await get_admin_language(session, user_id)
    
    if not await is_main_admin(user_id):
        await callback.answer(get_string(language, "access_denied"))
        return
    
    # Get list of added admins
    admins = await get_added_admins(session)
    
    # Build admin list text
    text = get_string(language, "admin_management_title") + "\n\n"
    main_display = await get_admin_display(callback.bot, ADMIN_ID)
    text += get_string(language, "admin_list_main", user_id=main_display) + "\n"
    
    if admins:
        for admin in admins:
            display = await get_admin_display(callback.bot, admin.user_id)
            text += get_string(language, "admin_list_item", user_id=display) + "\n"
    else:
        text += "\n" + get_string(language, "no_additional_admins")
    
    await safe_edit_message(
        callback.message,
        text,
        reply_markup=get_admin_management_keyboard(language)
    )
    await callback.answer()


@router.callback_query(F.data == "admin_add")
async def admin_add_callback(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """Handle add admin button - request user ID."""
    user_id = callback.from_user.id
    language = await get_admin_language(session, user_id)
    
    if not await is_main_admin(user_id):
        await callback.answer(get_string(language, "access_denied"))
        return
    
    await state.set_state(AdminStates.waiting_for_admin_id)
    await callback.message.edit_text(
        get_string(language, "add_admin_prompt"),
        reply_markup=get_back_to_menu_keyboard(language)
    )
    await callback.answer()


@router.message(AdminStates.waiting_for_admin_id)
async def process_admin_id(message: Message, session: AsyncSession, state: FSMContext):
    """Process admin ID input."""
    user_id = message.from_user.id
    language = await get_admin_language(session, user_id)
    
    if not await is_main_admin(user_id):
        await state.clear()
        return
    
    try:
        new_admin_id = int(message.text.strip())
        if new_admin_id <= 0:
            raise ValueError()
    except ValueError:
        await message.answer(get_string(language, "admin_invalid_id"))
        return
    
    # Try to add admin
    admin = await add_admin(session, new_admin_id, user_id)
    
    if admin:
        display = await get_admin_display(message.bot, new_admin_id)
        await message.answer(
            get_string(language, "admin_added", user_id=display)
        )
    else:
        await message.answer(get_string(language, "admin_already_exists"))
    
    await state.clear()


@router.callback_query(F.data == "admin_remove")
async def admin_remove_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle remove admin button - show list of admins to remove."""
    user_id = callback.from_user.id
    language = await get_admin_language(session, user_id)
    
    if not await is_main_admin(user_id):
        await callback.answer(get_string(language, "access_denied"))
        return
    
    admins = await get_added_admins(session)

    if not admins:
        await callback.answer(get_string(language, "no_additional_admins"))
        return
    admin_entries = []
    for admin in admins:
        display = await get_admin_display(callback.bot, admin.user_id)
        admin_entries.append((admin.user_id, display))

    await safe_edit_message(
        callback.message,
        get_string(language, "remove_admin_prompt"),
        reply_markup=get_admin_remove_keyboard(admin_entries, language)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_remove_"))
async def admin_remove_confirm_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle admin removal confirmation."""
    user_id = callback.from_user.id
    language = await get_admin_language(session, user_id)
    
    if not await is_main_admin(user_id):
        await callback.answer(get_string(language, "access_denied"))
        return
    
    admin_to_remove = int(callback.data.split("_")[-1])
    
    display = await get_admin_display(callback.bot, admin_to_remove)

    if await remove_admin(session, admin_to_remove):
        await callback.answer(
            get_string(language, "admin_removed", user_id=display)
        )
        # Return to admin management
        await admin_manage_callback(callback, session)
    else:
        await callback.answer(get_string(language, "admin_not_found"))

