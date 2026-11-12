from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    """FSM для регистрации клиента"""
    name = State()
    consent_given = State()
    number = State()

