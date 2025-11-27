"""
FSM states for application submission process.
"""
from aiogram.fsm.state import State, StatesGroup


class ApplicationSteps(StatesGroup):
    """Application submission steps."""
    name = State()
    contact = State()
    purpose = State()


class AdminStates(StatesGroup):
    """Admin management states."""
    waiting_for_admin_id = State()

