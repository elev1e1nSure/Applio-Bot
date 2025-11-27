"""
FSM states for application submission process.
"""
from aiogram.fsm.state import State, StatesGroup


class ApplicationSteps(StatesGroup):
    """Application submission steps."""
    name = State()
    contact = State()
    purpose = State()

