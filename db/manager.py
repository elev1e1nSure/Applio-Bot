"""
Database manager for CRUD operations and anti-spam checks.
"""
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_ID, APP_COOLDOWN_SECONDS
from db.models import Admin, Application, ApplicationStatus, User

logger = logging.getLogger(__name__)


async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get user by ID.

    Args:
        session: Database session
        user_id: Telegram user ID

    Returns:
        User object or None if not found
    """
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_or_create_user(
    session: AsyncSession,
    user_id: int,
    language: str = "en"
) -> User:
    """
    Get existing user or create new one.

    Args:
        session: Database session
        user_id: Telegram user ID
        language: User language code

    Returns:
        User object
    """
    user = await get_user(session, user_id)
    if not user:
        user = User(user_id=user_id, language=language)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info(f"Created new user: {user_id}")
    return user


async def update_user_language(
    session: AsyncSession,
    user_id: int,
    language: str
) -> Optional[User]:
    """
    Update user language preference.

    Args:
        session: Database session
        user_id: Telegram user ID
        language: New language code

    Returns:
        Updated user object or None
    """
    user = await get_user(session, user_id)
    if user:
        user.language = language
        await session.commit()
        logger.info(f"Updated language for user {user_id}: {language}")
    return user


async def check_cooldown(session: AsyncSession, user_id: int) -> Optional[int]:
    """
    Check if user is in cooldown period.

    Args:
        session: Database session
        user_id: Telegram user ID

    Returns:
        Remaining seconds if in cooldown, None otherwise
    """
    user = await get_user(session, user_id)
    if not user or not user.last_submission_time:
        return None

    time_diff = datetime.utcnow() - user.last_submission_time
    if time_diff.total_seconds() < APP_COOLDOWN_SECONDS:
        remaining = int(APP_COOLDOWN_SECONDS - time_diff.total_seconds())
        return remaining
    return None


async def create_application(
    session: AsyncSession,
    user_id: int,
    name: str,
    contact: str,
    purpose: str
) -> Application:
    """
    Create new application and update user's last submission time.

    Args:
        session: Database session
        user_id: Telegram user ID
        name: Applicant name
        contact: Contact information
        purpose: Application purpose

    Returns:
        Created application object
    """
    application = Application(
        user_id=user_id,
        name=name,
        contact=contact,
        purpose=purpose,
        status=ApplicationStatus.PENDING
    )
    session.add(application)

    # Update user's last submission time
    user = await get_user(session, user_id)
    if user:
        user.last_submission_time = datetime.utcnow()

    await session.commit()
    await session.refresh(application)
    logger.info(f"New application #{application.id} created by user {user_id}")
    return application


async def get_application(
    session: AsyncSession,
    app_id: int
) -> Optional[Application]:
    """
    Get application by ID.

    Args:
        session: Database session
        app_id: Application ID

    Returns:
        Application object or None
    """
    result = await session.execute(
        select(Application).where(Application.id == app_id)
    )
    return result.scalar_one_or_none()


async def update_application_status(
    session: AsyncSession,
    app_id: int,
    status: ApplicationStatus
) -> Optional[Application]:
    """
    Update application status.

    Args:
        session: Database session
        app_id: Application ID
        status: New status

    Returns:
        Updated application or None
    """
    app = await get_application(session, app_id)
    if app:
        app.status = status
        await session.commit()
        logger.info(f"Application #{app_id} status updated to {status.value}")
    return app


# ============== Admin Management ==============


async def is_admin(session: AsyncSession, user_id: int) -> bool:
    """
    Check if user is an admin (main admin or added admin).

    Args:
        session: Database session
        user_id: Telegram user ID

    Returns:
        True if user is admin, False otherwise
    """
    # Check if main admin from config
    if user_id == ADMIN_ID:
        return True

    # Check if added admin in database
    result = await session.execute(
        select(Admin).where(Admin.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


async def is_main_admin(user_id: int) -> bool:
    """
    Check if user is the main admin (from .env).

    Args:
        user_id: Telegram user ID

    Returns:
        True if main admin, False otherwise
    """
    return user_id == ADMIN_ID


async def get_all_admins(session: AsyncSession) -> list:
    """
    Get list of all admin user IDs (including main admin).

    Args:
        session: Database session

    Returns:
        List of admin user IDs
    """
    result = await session.execute(select(Admin))
    admins = result.scalars().all()
    admin_ids = [ADMIN_ID] + [admin.user_id for admin in admins]
    return admin_ids


async def get_added_admins(session: AsyncSession) -> list:
    """
    Get list of added admins (excluding main admin).

    Args:
        session: Database session

    Returns:
        List of Admin objects
    """
    result = await session.execute(
        select(Admin).order_by(Admin.created_at.desc())
    )
    return result.scalars().all()


async def add_admin(
    session: AsyncSession,
    user_id: int,
    added_by: int
) -> Optional[Admin]:
    """
    Add new admin.

    Args:
        session: Database session
        user_id: Telegram user ID to add as admin
        added_by: ID of admin who added this user

    Returns:
        Created Admin object or None if already exists
    """
    # Check if already admin
    if await is_admin(session, user_id):
        return None

    admin = Admin(user_id=user_id, added_by=added_by)
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    logger.info(f"New admin added: {user_id} by {added_by}")
    return admin


async def remove_admin(session: AsyncSession, user_id: int) -> bool:
    """
    Remove admin by user ID.

    Args:
        session: Database session
        user_id: Telegram user ID to remove

    Returns:
        True if removed, False if not found or is main admin
    """
    # Cannot remove main admin
    if user_id == ADMIN_ID:
        return False

    result = await session.execute(
        select(Admin).where(Admin.user_id == user_id)
    )
    admin = result.scalar_one_or_none()

    if not admin:
        return False

    await session.delete(admin)
    await session.commit()
    logger.info(f"Admin removed: {user_id}")
    return True

