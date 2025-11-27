"""
User keyboards for common interactions.
"""
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from locales.strings import AVAILABLE_LANGUAGES, LANG_EN, get_string


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard."""
    buttons = []
    for lang_code, lang_name in AVAILABLE_LANGUAGES.items():
        buttons.append([InlineKeyboardButton(
            text=lang_name,
            callback_data=f"lang_{lang_code}"
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_keyboard(language: str = LANG_EN) -> ReplyKeyboardMarkup:
    """Get cancel keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=get_string(language, "cancel"))]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_contact_step_keyboard(language: str = LANG_EN) -> InlineKeyboardMarkup:
    """
    Get keyboard for contact step with 'Continue with Telegram' button.

    Args:
        language: User language code

    Returns:
        Inline keyboard with Telegram contact option
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=get_string(language, "btn_continue_telegram"),
                callback_data="continue_with_telegram"
            )]
        ]
    )
