"""
Admin keyboards for admin panel.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locales.strings import get_string


def get_admin_main_keyboard(pending_count: int = 0, language: str = "en") -> InlineKeyboardMarkup:
    """Get main admin menu keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{get_string(language, 'btn_new_applications')} ({pending_count})",
                callback_data="admin_new_apps"
            )],
            [InlineKeyboardButton(
                text=get_string(language, "btn_show_stats"),
                callback_data="admin_stats"
            )],
            [InlineKeyboardButton(
                text=get_string(language, "btn_exit"),
                callback_data="admin_exit"
            )]
        ]
    )


def get_application_actions_keyboard(application_id: int, language: str = "en") -> InlineKeyboardMarkup:
    """Get keyboard for application actions (approve/reject)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_string(language, "btn_approve"),
                    callback_data=f"admin_approve_{application_id}"
                ),
                InlineKeyboardButton(
                    text=get_string(language, "btn_reject"),
                    callback_data=f"admin_reject_{application_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_string(language, "btn_back_to_list"),
                    callback_data="admin_new_apps"
                )
            ]
        ]
    )


def get_back_to_menu_keyboard(language: str = "en") -> InlineKeyboardMarkup:
    """Get back to admin menu keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=get_string(language, "btn_back_to_menu"),
                callback_data="admin_menu"
            )]
        ]
    )

