from aiogram.dispatcher.filters.state import StatesGroup, State


class ChangeNickname(StatesGroup):
    enter_nickname = State()
