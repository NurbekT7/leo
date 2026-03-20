from aiogram.fsm.state import StatesGroup, State

class Registration(StatesGroup):
    gender = State()
    search_gender = State()
    name = State()
    age = State()
    location = State()
    media = State()
    bio = State()

class Browsing(StatesGroup):
    viewing_profiles = State()