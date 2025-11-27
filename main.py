"""
Main entry point for the Telegram bot.
"""
import asyncio
import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, TelegramObject

from config import BOT_TOKEN
from db.database import init_db, get_session
from middlewares.antiflood import AntiFloodMiddleware
from handlers import common_handlers, application_handlers, admin_handlers, cancel_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def setup_bot_commands(bot: Bot):
    """Set up bot commands menu."""
    commands = [
        BotCommand(command="start", description="Shows welcome message and instructions"),
        BotCommand(command="apply", description="Starts the application submission process"),
        BotCommand(command="language", description="Change language settings"),
    ]
    await bot.set_my_commands(commands)


class DatabaseMiddleware(BaseMiddleware):
    """Database session middleware."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Inject database session into handler data."""
        async for session in get_session():
            data["session"] = session
            return await handler(event, data)


async def main():
    """Main function to start the bot."""
    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register middlewares
    dp.message.middleware(AntiFloodMiddleware())
    dp.callback_query.middleware(AntiFloodMiddleware())
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    
    # Register routers (order matters - cancel_handler should be last)
    dp.include_router(common_handlers.router)
    dp.include_router(application_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(cancel_handler.router)  # Last to catch cancel button
    
    # Set up bot commands
    await setup_bot_commands(bot)
    
    # Start polling
    logger.info("Starting bot...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

