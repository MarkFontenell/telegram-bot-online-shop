from aiogram.fsm.state import StatesGroup, State

class NewProduct(StatesGroup):
    """FSM для добавления товара"""
    product_name = State()
    product_description = State()
    product_count = State()
    product_price = State()
    product_category = State()
    product_image = State()

class ProductFSM(StatesGroup):
    waiting_for_id = State()
    choosing_field = State()
    editing_value = State()

class CategoryFSM(StatesGroup):
    waiting_for_category_name = State()
    waiting_for_category_id_to_delete = State()
