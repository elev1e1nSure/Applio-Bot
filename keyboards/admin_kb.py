"""
Admin keyboards for admin panel.
"""
from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from locales.strings import get_string


def get_admin_main_keyboard(
    pending_count: int = 0,
    language: str = "en",
    is_main_admin: bool = False
) -> InlineKeyboardMarkup:
    """
    Get main admin menu keyboard.

    Args:
        pending_count: Number of pending applications
        language: Admin language code
        is_main_admin: Whether the user is the main admin

    Returns:
        Inline keyboard for admin main menu
    """
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{get_string(language, 'btn_new_applications')} ({pending_count})",
                callback_data="admin_new_apps"
            ),
            InlineKeyboardButton(
                text=get_string(language, "btn_show_stats"),
                callback_data="admin_stats"
            )
        ],
    ]

    # Only main admin can manage other admins
    if is_main_admin:
        buttons.append([InlineKeyboardButton(
            text=get_string(language, "btn_manage_admins"),
            callback_data="admin_manage"
        )])

    buttons.append([InlineKeyboardButton(
        text=get_string(language, "btn_exit"),
        callback_data="admin_exit"
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_applications_list_keyboard(
    applications: List,
    language: str = "en"
) -> InlineKeyboardMarkup:
    """
    Get keyboard with list of pending applications.

    Args:
        applications: List of Application objects
        language: Admin language code

    Returns:
        Inline keyboard with application list
    """
    buttons = []
    for i, app in enumerate(applications, 1):
        buttons.append([InlineKeyboardButton(
            text=get_string(language, "app_list_item", num=i, name=app.name[:20]),
            callback_data=f"view_app_{app.id}"
        )])

    buttons.append([InlineKeyboardButton(
        text=get_string(language, "btn_back_to_menu"),
        callback_data="admin_menu"
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_application_actions_keyboard(application_id: int, language: str = "en") -> InlineKeyboardMarkup:
    """
    Get keyboard for application actions (approve/reject).

    Args:
        application_id: Application ID
        language: Admin language code

    Returns:
        Inline keyboard with approve/reject actions
    """
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
    """
    Get back to admin menu keyboard.

    Args:
        language: Admin language code

    Returns:
        Inline keyboard with back button
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=get_string(language, "btn_back_to_menu"),
                callback_data="admin_menu"
            )]
        ]
    )


def get_admin_management_keyboard(language: str = "en") -> InlineKeyboardMarkup:
    """
    Get admin management keyboard.

    Args:
        language: Admin language code

    Returns:
        Inline keyboard for admin management
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=get_string(language, "btn_add_admin"),
                callback_data="admin_add"
            )],
            [InlineKeyboardButton(
                text=get_string(language, "btn_remove_admin"),
                callback_data="admin_remove"
            )],
            [InlineKeyboardButton(
                text=get_string(language, "btn_back_to_menu"),
                callback_data="admin_menu"
            )]
        ]
    )


def get_admin_remove_keyboard(
    admins: List,
    language: str = "en"
) -> InlineKeyboardMarkup:
    """
    Get keyboard for removing admins.

    Args:
        admins: List of Admin objects
        language: Admin language code

    Returns:
        Inline keyboard with admin list for removal
    """
    buttons = []
    for user_id, label in admins:
        buttons.append([InlineKeyboardButton(
            text=f"❌ {label}",
            callback_data=f"admin_remove_{user_id}"
        )])

    buttons.append([InlineKeyboardButton(
        text=get_string(language, "btn_back_to_menu"),
        callback_data="admin_manage"
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

