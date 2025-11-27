"""
Handlers for application submission process.
"""
import logging
import re
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_ID
from db.manager import get_all_admins, get_user
from db.models import Application, ApplicationStatus, User
from keyboards.admin_kb import get_application_actions_keyboard
from keyboards.user_kb import get_cancel_keyboard, get_contact_step_keyboard
from locales.strings import LANG_EN, get_string
from states.application_states import ApplicationSteps

logger = logging.getLogger(__name__)

NAME_REGEX = re.compile(r"^[A-Za-zА-Яа-яЁё\s\-']{2,100}$")
PHONE_REGEX = re.compile(r"^\+?\d{7,15}$")
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
USERNAME_REGEX = re.compile(r"^@?[A-Za-z0-9_]{5,32}$")


async def get_admin_language(session: AsyncSession) -> str:
    """Get admin's language preference."""
    result = await session.execute(
        select(User).where(User.user_id == ADMIN_ID)
    )
    user = result.scalar_one_or_none()
    return user.language if user else LANG_EN

router = Router()


@router.callback_query(F.data == "continue_with_telegram", ApplicationSteps.contact)
async def process_telegram_contact(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession
):
    """
    Handle 'Continue with Telegram' button press.
    Uses user's Telegram username or ID as contact.
    """
    user_id = callback.from_user.id
    username = callback.from_user.username

    # Get user language
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    language = user.language if user else LANG_EN

    # Use username if available, otherwise use user ID
    contact_value = f"@{username}" if username else f"tg://user?id={user_id}"

    await state.update_data(contact=contact_value)
    await state.set_state(ApplicationSteps.purpose)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(get_string(language, "step_3_of_3"))
    await callback.answer()


@router.message(Command("apply"))
async def cmd_apply(message: Message, state: FSMContext, session: AsyncSession):
    """Start application submission process."""
    user_id = message.from_user.id
    
    # Get user
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Create user if doesn't exist
        user = User(user_id=user_id, language=LANG_EN)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    language = user.language or LANG_EN
    
    await state.set_state(ApplicationSteps.name)
    await message.answer(
        get_string(language, "apply_start"),
        reply_markup=get_cancel_keyboard(language)
    )


@router.message(ApplicationSteps.name)
async def process_name(message: Message, state: FSMContext, session: AsyncSession):
    """Process user name input."""
    user_id = message.from_user.id
    
    # Get user
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    language = user.language if user else LANG_EN
    
    # Check for cancel
    if message.text == get_string(language, "cancel"):
        await state.clear()
        await message.answer(
            get_string(language, "application_cancelled"),
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    if not message.text or len(message.text.strip()) < 2:
        await message.answer(get_string(language, "invalid_input"))
        return

    if not NAME_REGEX.match(message.text.strip()):
        await message.answer(get_string(language, "error_name_format"))
        return
    
    await state.update_data(name=message.text.strip())
    await state.set_state(ApplicationSteps.contact)
    await message.answer(
        get_string(language, "step_2_of_3"),
        reply_markup=get_contact_step_keyboard(language)
    )


@router.message(ApplicationSteps.contact)
async def process_contact(message: Message, state: FSMContext, session: AsyncSession):
    """Process contact information input."""
    user_id = message.from_user.id
    
    # Get user
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    language = user.language if user else LANG_EN
    
    # Check for cancel
    if message.text == get_string(language, "cancel"):
        await state.clear()
        await message.answer(
            get_string(language, "application_cancelled"),
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    if not message.text or len(message.text.strip()) < 3:
        await message.answer(get_string(language, "invalid_input"))
        return

    contact_value = message.text.strip()
    if not (
        EMAIL_REGEX.match(contact_value)
        or PHONE_REGEX.match(contact_value)
        or USERNAME_REGEX.match(contact_value)
    ):
        await message.answer(get_string(language, "error_contact_format"))
        return

    await state.update_data(contact=contact_value)
    await state.set_state(ApplicationSteps.purpose)
    await message.answer(get_string(language, "step_3_of_3"))


@router.message(ApplicationSteps.purpose)
async def process_purpose(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    """Process purpose input and save application."""
    user_id = message.from_user.id
    
    # Get user
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(user_id=user_id, language=LANG_EN)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    language = user.language or LANG_EN
    
    # Check for cancel
    if message.text == get_string(language, "cancel"):
        await state.clear()
        await message.answer(
            get_string(language, "application_cancelled"),
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    if not message.text or len(message.text.strip()) < 5:
        await message.answer(get_string(language, "invalid_input"))
        return

    if len(message.text.strip()) < 10:
        await message.answer(get_string(language, "error_purpose_format"))
        return
    
    # Get all data
    data = await state.get_data()
    
    # Create application
    application = Application(
        user_id=user_id,
        name=data["name"],
        contact=data["contact"],
        purpose=message.text.strip(),
        status=ApplicationStatus.PENDING
    )
    session.add(application)
    
    # Update user's last submission time
    user.last_submission_time = datetime.utcnow()
    
    await session.commit()
    await session.refresh(application)
    await state.clear()
    
    # Notify all admins about new application
    try:
        admin_ids = await get_all_admins(session)
        for admin_id in admin_ids:
            try:
                admin_user = await get_user(session, admin_id)
                admin_language = admin_user.language if admin_user else LANG_EN
                admin_text = (
                    f"{get_string(admin_language, 'new_application_title').replace('{id}', str(application.id))}\n\n"
                    f"👤 <b>{get_string(admin_language, 'field_name')}:</b> {application.name}\n"
                    f"📞 <b>{get_string(admin_language, 'field_contact')}:</b> {application.contact}\n"
                    f"📄 <b>{get_string(admin_language, 'field_purpose')}:</b> {application.purpose}\n\n"
                    f"🕐 <b>{get_string(admin_language, 'field_submitted')}:</b> {application.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                await bot.send_message(
                    admin_id,
                    admin_text,
                    reply_markup=get_application_actions_keyboard(application.id, admin_language)
                )
            except Exception:
                pass  # Admin blocked bot or other error
    except Exception as e:
        logger.error(f"Failed to notify admins about new application: {e}", exc_info=True)
    
    await message.answer(
        get_string(language, "application_received"),
        reply_markup=ReplyKeyboardRemove()
    )

