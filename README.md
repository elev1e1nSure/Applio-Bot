# Applio Bot

A multi-language Telegram bot built with aiogram 3.x for handling application submissions with an admin panel for review and management.

## Features

- 🌐 **Multi-language Support**: English (EN) and Russian (RU) localization
- 📝 **FSM-based Application Process**: Step-by-step form submission using Finite State Machine
- 🔐 **Admin Panel**: Complete admin interface for reviewing and managing applications
- 🛡️ **Anti-Spam Protection**: Cooldown mechanism to prevent spam submissions
- 💾 **SQLite Database**: Persistent storage using SQLAlchemy ORM
- 🎨 **Clean Architecture**: Modular structure with separation of concerns

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Telegram Bot Token (obtain from [@BotFather](https://t.me/BotFather))

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Applio
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   Create a `.env` file in the root directory with the following variables:
   ```env
   BOT_TOKEN=your_bot_token_here
   ADMIN_ID=your_telegram_user_id
   DB_FILE=applio_bot.db
   APP_COOLDOWN_SECONDS=300
   ```
   
   - `BOT_TOKEN`: Your Telegram bot token from [@BotFather](https://t.me/BotFather)
   - `ADMIN_ID`: Your Telegram user ID (you can get it from [@userinfobot](https://t.me/userinfobot))
   - `DB_FILE`: Database filename (default: `applio_bot.db`)
   - `APP_COOLDOWN_SECONDS`: Cooldown time between submissions in seconds (default: 300 = 5 minutes)

5. **Run the bot:**
   ```bash
   python main.py
   ```

## Usage

### User Commands

- `/start` - Shows welcome message and instructions
- `/apply` - Starts the application submission process
- `/language` - Change language settings (EN/RU)

### Application Process

1. User runs `/apply` command
2. Bot asks for:
   - Name
   - Contact information
   - Purpose of application
3. Application is submitted and stored in database with "pending" status
4. User receives confirmation message
5. Admin reviews the application through admin panel

### Admin Commands

- `/admin` - Opens admin panel with the following options:
  - **New Applications (X)**: View pending applications
  - **Show Stats**: Display statistics (total users, applications, etc.)
  - **Exit**: Close admin panel

### Admin Actions

When viewing an application, admin can:
- ✅ **Approve**: Approve the application and notify the user
- ❌ **Reject**: Reject the application and notify the user
- 🔙 **Back to List**: Return to applications list

## Project Structure

```
Applio/
├── db/
│   ├── __init__.py
│   ├── models.py          # Database models (User, Application)
│   └── database.py        # Database initialization
├── handlers/
│   ├── __init__.py
│   ├── common_handlers.py  # Common commands (start, language)
│   ├── application_handlers.py  # Application submission handlers
│   └── admin_handlers.py  # Admin panel handlers
├── keyboards/
│   ├── __init__.py
│   ├── common_kb.py       # Common keyboards
│   └── admin_kb.py        # Admin keyboards
├── middlewares/
│   ├── __init__.py
│   └── antiflood.py       # Anti-spam middleware
├── states/
│   ├── __init__.py
│   └── application_states.py  # FSM states
├── locales/
│   ├── __init__.py
│   └── strings.py         # Localization strings
├── config.py              # Configuration
├── main.py                # Entry point
├── requirements.txt       # Dependencies
├── .gitignore            # Git ignore rules
├── LICENSE               # MIT License
└── README.md             # This file
```

## Configuration

All configuration is done through the `.env` file. The bot reads:
- `BOT_TOKEN`: Required - Telegram bot token
- `ADMIN_ID`: Required - Admin Telegram user ID
- `DB_FILE`: Optional - Database filename (default: `applio_bot.db`)
- `APP_COOLDOWN_SECONDS`: Optional - Cooldown time in seconds (default: 300)

## Database

The bot uses SQLite database with two main tables:

- **users**: Stores user information (user_id, language, last_submission_time)
- **applications**: Stores application data (id, user_id, name, contact, purpose, status)

Database is automatically created on first run.

## Localization

The bot supports two languages:
- English (EN) - default
- Russian (RU)

Users can change language using `/language` command. All strings are stored in `locales/strings.py`.

## Anti-Spam

The bot includes an anti-spam middleware that enforces a cooldown period between application submissions. Default cooldown is 5 minutes (300 seconds), configurable via `APP_COOLDOWN_SECONDS` in `.env`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the GitHub repository.

