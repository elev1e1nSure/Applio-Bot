"""
User handlers for common commands.
"""
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_ID
from db.models import User
from keyboards.user_kb import get_language_keyboard
from locales.strings import LANG_EN, get_string

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    """Handle /start command."""
    user_id = message.from_user.id
    
    # Get or create user
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user
        user = User(
            user_id=user_id,
            language=message.from_user.language_code or LANG_EN
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    language = user.language or LANG_EN
    await message.answer(
        get_string(language, "welcome")
    )
    
    # Send admin reminder if user is admin
    if user_id == ADMIN_ID:
        await message.answer(get_string(language, "admin_welcome"))


@router.message(Command("language"))
async def cmd_language(message: Message, session: AsyncSession):
    """Handle /language command."""
    user_id = message.from_user.id
    
    # Get user
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    language = user.language if user else LANG_EN
    await message.answer(
        get_string(language, "select_language"),
        reply_markup=get_language_keyboard()
    )


@router.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback: CallbackQuery, session: AsyncSession):
    """Handle language selection callback."""
    lang_code = callback.data.split("_")[1]
    
    if lang_code not in ["en", "ru"]:
        await callback.answer(get_string("en", "invalid_language"))
        return
    
    user_id = callback.from_user.id
    
    # Get or create user
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(user_id=user_id, language=lang_code)
        session.add(user)
    else:
        user.language = lang_code
    
    await session.commit()
    
    await callback.answer(get_string(lang_code, "language_changed"))
    await callback.message.edit_text(get_string(lang_code, "language_changed"))

