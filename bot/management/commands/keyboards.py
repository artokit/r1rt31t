from aiogram.types import *
from asgiref.sync import sync_to_async

from bot.management.commands.lang_middleware import i18n
from bot.models import City, Product, Pack, TypeOfBuy

_ = i18n.gettext


def get_start(lang=None):
    start = ReplyKeyboardMarkup(resize_keyboard=True)
    start.add(
        KeyboardButton(_('Выбрать город', locale=lang)),
        KeyboardButton(_('Витрина', locale=lang)),
        KeyboardButton(_('Отзывы', locale=lang)),
    )
    start.add(
        KeyboardButton(_('Профиль', locale=lang)),
        KeyboardButton(_('Контакты', locale=lang)),
        KeyboardButton(_('Доступ к сайту', locale=lang)),
    )
    start.add(
        KeyboardButton(_('Мои заказы', locale=lang)),
        KeyboardButton(_('Последняя покупка', locale=lang)),
        KeyboardButton(_('Промо-код', locale=lang)),
    )
    return start


lang_select = InlineKeyboardMarkup()
lang_select.row(InlineKeyboardButton("🇷🇺 Русский язык", callback_data='select_lang:ru'))
lang_select.row(InlineKeyboardButton("🇬🇪 ქართული ენა", callback_data='select_lang:ka'))
lang_select.row(InlineKeyboardButton("🇺🇿 o'zbek tili", callback_data='select_lang:uz'))


def get_profiles_buttons():
    profile_buttons = InlineKeyboardMarkup()
    profile_buttons.row(InlineKeyboardButton(_("Сменить никнейм"), callback_data='change_nickname'))
    profile_buttons.row(InlineKeyboardButton(_("Пополнить баланс"), callback_data='add_balance'))
    profile_buttons.row(InlineKeyboardButton(_("Показать купоны"), callback_data='get_coupons'))
    profile_buttons.row(InlineKeyboardButton(_("Персональный бот"), callback_data='add_bot'))
    profile_buttons.row(InlineKeyboardButton("Сменить язык/Change language", callback_data='change_language'))

    return profile_buttons


def cancel_button():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(_("Отмена"), callback_data='cancel'))
    return keyboard


def how_add_bot():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(_("Как добавить персонального бота?"), callback_data="how_add_bot"))
    return keyboard


def get_site_button():
    site_button = InlineKeyboardMarkup()
    site_button.add(InlineKeyboardButton(_('Перейти на сайт'), url='https://kaifshop.biz/login'))
    return site_button


async def select_city():
    keyboard = InlineKeyboardMarkup()

    for i in await sync_to_async(list)(City.objects.all()):
        keyboard.row(InlineKeyboardButton(i.name, callback_data=f'city:{i.pk}'))

    return keyboard


async def product_keyboard(products: list[Product]):
    keyboard = InlineKeyboardMarkup()

    for i in products:
        keyboard.row(InlineKeyboardButton(i.name, callback_data=f'prod:{i.pk}'))
    return keyboard


def get_more_info(prod_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text='Показать отзывы', callback_data=f"get_comments:{prod_id}"))
    return keyboard


def get_areas_keyboard(areas: set, prod_id: int):
    keyboard = InlineKeyboardMarkup()
    for i in areas:
        keyboard.row(InlineKeyboardButton(i, callback_data=f'area:{i}:{prod_id}'))
    return keyboard


def get_pack_keyboard(packs: list[Pack], prod_id: int, usd_course: float, area_id: int):
    keyboard = InlineKeyboardMarkup()

    for pack in packs:
        keyboard.row(
            InlineKeyboardButton(
                f'{pack.weight}гр: 🇷🇺 %.2f RUB, 🇺🇸 %.2f USD' %
                (round(pack.price, 2), round(pack.price / usd_course, 2)),
                callback_data=f'pack:{prod_id}:{pack.pk}:{area_id}'
            )
        )

    return keyboard


def get_freshness_keyboard(freshness: list, prod_id: int, pack_id: int, area_id: int):
    keyboard = InlineKeyboardMarkup()

    for i in freshness:
        keyboard.row(InlineKeyboardButton(i.name, callback_data=f'fresh:{prod_id}:{pack_id}:{i.pk}:{area_id}'))

    return keyboard


def get_type_of_buy_keyboard(types: list[TypeOfBuy], prod_id: int, fresh_id: int, pack_id: int, area_id: int):
    keyboard = InlineKeyboardMarkup()

    for i in types:
        keyboard.row(InlineKeyboardButton(
            i.name,
            callback_data=f'final:{prod_id}:{fresh_id}:{pack_id}:{area_id}:{i.pk}')
        )

    return keyboard


def method_of_pays(amount):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(_('Оплата с баланса'), callback_data=f'pay_money_from_balance:{amount}'))
    keyboard.row(InlineKeyboardButton('Bitcoin', callback_data=f'pay_of_money:bitcoin:{amount}'))
    keyboard.row(InlineKeyboardButton('Litecoin', callback_data=f'pay_of_money:litecoin:{amount}'))
    keyboard.row(InlineKeyboardButton('🇷🇺 Перевод на карту', callback_data=f'pay_of_money:card:{amount}'))
    return keyboard


def add_b():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(_("Пополнить баланс"), callback_data='add_balance'))
    return keyboard


def card_add():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text=_('Подтвердить платеж'), callback_data='check_payment_card'))
    keyboard.row(InlineKeyboardButton(text=_('Отменить заказ'), callback_data='cancel_payment'))
    return keyboard


def cancel_exc():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text=_('Отменить заказ'), callback_data='cancel_exc'))
    return keyboard


def crypt_keyboard_payment(type_of_payment):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text=_("Показать QR-код для оплаты"), callback_data=f'qr_code:{type_of_payment}'))
    keyboard.row(InlineKeyboardButton(text=_('Отменить заказ'), callback_data='cancel_payment'))
    return keyboard


def comments_keyboard(current_page: int, last_page: int):
    keyboard = InlineKeyboardMarkup()
    buttons = []

    if current_page != 1:
        buttons.append(InlineKeyboardButton(text=_('Пред.'), callback_data=f'comments_page:{current_page-1}'))

    if current_page != last_page:
        buttons.append(InlineKeyboardButton(text=_('След.'), callback_data=f'comments_page:{current_page+1}'))

    keyboard.row(*buttons)
    return keyboard
