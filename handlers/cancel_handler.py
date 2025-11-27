"""
Handler for cancel button that works globally.
This router should be registered last to not interfere with other handlers.
"""
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import User
from locales.strings import get_string, LANG_EN

router = Router()


@router.message(F.text)
async def handle_cancel_button(message: Message, state: FSMContext, session: AsyncSession):
    """Handle cancel button press globally."""
    user_id = message.from_user.id
    
    # Get user language
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    language = user.language if user else LANG_EN
    
    # Check if message text matches cancel button in any language
    cancel_text_en = get_string("en", "cancel")
    cancel_text_ru = get_string("ru", "cancel")
    
    if message.text not in [cancel_text_en, cancel_text_ru]:
        return  # Not a cancel button, let other handlers process it
    
    # Check if user is in any FSM state
    current_state = await state.get_state()
    
    if current_state:
        # User is in FSM state, cancel it and remove keyboard
        await state.clear()
        await message.answer(
            get_string(language, "application_cancelled"),
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        # User is not in any state, just remove keyboard silently
        await message.answer(
            reply_markup=ReplyKeyboardRemove()
        )

