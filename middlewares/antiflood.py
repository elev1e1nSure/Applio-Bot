"""
Anti-flood middleware to prevent spam.
Implements cooldown mechanism for application submissions.
"""
import logging
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import APP_COOLDOWN_SECONDS
from db.models import User
from locales.strings import LANG_EN, get_string

logger = logging.getLogger(__name__)


class AntiFloodMiddleware(BaseMiddleware):
    """Middleware to prevent spam by implementing cooldown between submissions."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Check if user is in cooldown period.
        
        Args:
            handler: Next handler in chain
            event: Telegram event
            data: Handler data
            
        Returns:
            Handler result or error message
        """
        # Only process messages (not callbacks)
        if not isinstance(event, Message):
            return await handler(event, data)
        
        # Skip if not a command or text message
        if not event.text or not (event.text.startswith("/apply") or event.text.startswith("/start")):
            return await handler(event, data)
        
        # Get database session
        session: AsyncSession = data.get("session")
        if not session:
            return await handler(event, data)
        
        user_id = event.from_user.id
        
        # Get or create user
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # New user, allow
            return await handler(event, data)
        
        # Check cooldown
        if user.last_submission_time:
            time_diff = datetime.utcnow() - user.last_submission_time
            if time_diff.total_seconds() < APP_COOLDOWN_SECONDS:
                remaining = int(APP_COOLDOWN_SECONDS - time_diff.total_seconds())
                language = user.language or LANG_EN
                logger.info(
                    f"User {user_id} blocked by antiflood, {remaining}s remaining"
                )
                await event.answer(
                    get_string(language, "cooldown_active", seconds=remaining)
                )
                return
        
        # Allow handler to proceed
        return await handler(event, data)

