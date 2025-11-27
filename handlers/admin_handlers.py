"""
Admin handlers for admin panel.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from config import ADMIN_ID
from db.models import User, Application, ApplicationStatus
from locales.strings import get_string, LANG_EN
from keyboards.admin_kb import (
    get_admin_main_keyboard,
    get_application_actions_keyboard,
    get_back_to_menu_keyboard
)

router = Router()
logger = logging.getLogger(__name__)


async def safe_edit_message(message: Message, text: str, reply_markup=None):
    """Safely edit a message, fallback to sending a new one if editing fails."""
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        await message.answer(text, reply_markup=reply_markup)


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    result = int(user_id) == int(ADMIN_ID)
    if not result:
        logger.warning(f"Access denied for user {user_id}. Admin ID: {ADMIN_ID}")
    return result


async def get_admin_language(session: AsyncSession) -> str:
    """Get admin's language preference."""
    result = await session.execute(
        select(User).where(User.user_id == ADMIN_ID)
    )
    user = result.scalar_one_or_none()
    return user.language if user else LANG_EN


@router.message(Command("admin"))
async def cmd_admin(message: Message, session: AsyncSession):
    """Handle /admin command."""
    user_id = message.from_user.id
    logger.info(f"Admin command received from user {user_id}, ADMIN_ID={ADMIN_ID}")
    
    language = await get_admin_language(session)
    
    if not is_admin(user_id):
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
            reply_markup=get_admin_main_keyboard(pending_count, language)
        )
    except Exception as e:
        logger.error(f"Error in admin command: {e}", exc_info=True)
        await message.answer(get_string(language, "admin_error"))


@router.callback_query(F.data == "admin_menu")
async def admin_menu_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle admin menu callback."""
    language = await get_admin_language(session)
    
    if not is_admin(callback.from_user.id):
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
        reply_markup=get_admin_main_keyboard(pending_count, language)
    )
    await callback.answer()


@router.callback_query(F.data == "admin_new_apps")
async def admin_new_apps_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle new applications list callback."""
    language = await get_admin_language(session)
    
    if not is_admin(callback.from_user.id):
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
    
    # Show first application
    app = applications[0]
    
    # Get user
    user_result = await session.execute(
        select(User).where(User.user_id == app.user_id)
    )
    user = user_result.scalar_one_or_none()
    
    text = (
        f"📋 <b>Application #{app.id}</b>\n\n"
        f"👤 <b>{get_string(language, 'field_name')}:</b> {app.name}\n"
        f"📞 <b>{get_string(language, 'field_contact')}:</b> {app.contact}\n"
        f"📄 <b>{get_string(language, 'field_purpose')}:</b> {app.purpose}\n\n"
        f"🕐 <b>{get_string(language, 'field_submitted')}:</b> {app.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"📊 <b>{get_string(language, 'total_pending')}:</b> {len(applications)}"
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
    language = await get_admin_language(session)
    
    if not is_admin(callback.from_user.id):
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
        from aiogram import Bot
        bot: Bot = callback.bot
        try:
            await bot.send_message(
                app.user_id,
                get_string(language, "application_approved")
            )
        except Exception:
            pass  # User blocked bot or other error
    
    # Update message
    approved_title = get_string(language, 'app_approved_title').replace('{id}', str(app.id))
    text = (
        f"{approved_title}\n\n"
        f"👤 <b>{get_string(language, 'field_name')}:</b> {app.name}\n"
        f"📞 <b>{get_string(language, 'field_contact')}:</b> {app.contact}\n"
        f"📄 <b>{get_string(language, 'field_purpose')}:</b> {app.purpose}\n\n"
        f"{get_string(language, 'user_notified')}"
    )
    
    await safe_edit_message(
        callback.message,
        text,
        reply_markup=get_back_to_menu_keyboard(language)
    )
    await callback.answer(get_string(language, "application_approved").split("\n")[0])


@router.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle application rejection."""
    language = await get_admin_language(session)
    
    if not is_admin(callback.from_user.id):
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
        from aiogram import Bot
        bot: Bot = callback.bot
        try:
            await bot.send_message(
                app.user_id,
                get_string(language, "application_rejected")
            )
        except Exception:
            pass  # User blocked bot or other error
    
    # Update message
    rejected_title = get_string(language, 'app_rejected_title').replace('{id}', str(app.id))
    text = (
        f"{rejected_title}\n\n"
        f"👤 <b>{get_string(language, 'field_name')}:</b> {app.name}\n"
        f"📞 <b>{get_string(language, 'field_contact')}:</b> {app.contact}\n"
        f"📄 <b>{get_string(language, 'field_purpose')}:</b> {app.purpose}\n\n"
        f"{get_string(language, 'user_notified')}"
    )
    
    await safe_edit_message(
        callback.message,
        text,
        reply_markup=get_back_to_menu_keyboard(language)
    )
    await callback.answer(get_string(language, "application_rejected").split("\n")[0])


@router.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle admin stats callback."""
    language = await get_admin_language(session)
    
    if not is_admin(callback.from_user.id):
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
    language = await get_admin_language(session)
    await callback.message.delete()
    await callback.answer(get_string(language, "admin_panel_closed"))

