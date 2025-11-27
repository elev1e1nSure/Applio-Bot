"""
Common keyboards for user interactions.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from locales.strings import get_string, LANG_EN, LANG_RU, AVAILABLE_LANGUAGES


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

