"""
Handlers for application submission process.
"""
from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import User, Application, ApplicationStatus
from states.application_states import ApplicationSteps
from locales.strings import get_string, LANG_EN
from keyboards.common_kb import get_cancel_keyboard
from config import ADMIN_ID
from keyboards.admin_kb import get_application_actions_keyboard

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
    await message.answer(get_string(language, "step_2_of_3"))


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
    
    # Notify admin about new application
    try:
        admin_language = await get_admin_language(session)
        admin_text = (
            f"{get_string(admin_language, 'new_application_title').replace('{id}', str(application.id))}\n\n"
            f"👤 <b>{get_string(admin_language, 'field_name')}:</b> {application.name}\n"
            f"📞 <b>{get_string(admin_language, 'field_contact')}:</b> {application.contact}\n"
            f"📄 <b>{get_string(admin_language, 'field_purpose')}:</b> {application.purpose}\n\n"
            f"🕐 <b>{get_string(admin_language, 'field_submitted')}:</b> {application.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await bot.send_message(
            ADMIN_ID,
            admin_text,
            reply_markup=get_application_actions_keyboard(application.id, admin_language)
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to notify admin about new application: {e}", exc_info=True)
    
    await message.answer(
        get_string(language, "application_received"),
        reply_markup=ReplyKeyboardRemove()
    )

