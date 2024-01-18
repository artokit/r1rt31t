import math
import os.path
import random
from aiogram.utils import markdown
from asgiref.sync import sync_to_async
from aiogram.dispatcher import FSMContext
from django.core.management.base import BaseCommand
from bot.management.commands.lang_middleware import i18n
from bot.models import *
from aiogram import executor
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from bot.management.commands import keyboards
from kaif.settings import dp
import requests
from kaif import states
# from .parser import *


LANGUAGES = ['ru', 'ka', 'uz']
_ = i18n.gettext
USD_COURSE = 89
BTC_COURSE = 3_758_800
LTC_COURSE = 6146
CHECKER_I18N = (lambda msg, text: msg.text in [_(text, locale=i) for i in LANGUAGES])


HELLO_TEXT_PATH = os.path.join(os.path.dirname(__file__), 'hello.txt')
CRYPTO_PAYMENTS = PaymentCrypto.objects.all()
PAYMENTS = [i.title for i in CRYPTO_PAYMENTS]


def get_course_usd():
    # ltc_courses = requests.get('https://apirone.com/api/v2/ticker?currency=ltc', headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 YaBrowser/23.11.0.0 Safari/537.36'}).json()
    # rub = ltc_courses['rub']
    # usd = ltc_courses['usd']
    # return rub / usd
    return USD_COURSE


def get_ltc_course(rub_amount):
    return rub_amount / LTC_COURSE


def get_btc_amount(rub_amount):
    return rub_amount / BTC_COURSE


def get_course(count_of_money):
    if count_of_money:
        ltc_course = requests.get('https://apirone.com/api/v2/ticker?currency=ltc').json()['rub']
        btc_course = requests.get('https://apirone.com/api/v2/ticker?currency=btc').json()['rub']
        return {
            'rub': count_of_money,
            'btc': round(count_of_money / btc_course, 8),
            'ltc': round(count_of_money / ltc_course, 8)
        }
    return {i: 0 for i in ['rub', 'btc', 'ltc']}


@dp.message_handler(commands=['start'], state='*')
async def start(message: Message, state: FSMContext):
    await state.reset_data()
    await state.finish()

    with open(HELLO_TEXT_PATH, 'rb') as f:
        text = f.read().decode()
        await message.answer(
            text,
            reply_markup=keyboards.get_start(),
            parse_mode='markdown'
        )

    await message.answer("Выберите язык/Choose language", reply_markup=keyboards.lang_select)


@dp.callback_query_handler(lambda call: call.data.startswith('select_lang'))
async def select_lang(call: CallbackQuery):
    lang = call.data.split(':')[1]
    await change_lang(call.message.chat.id, lang)
    await call.message.answer(_('Язык бота был изменен на Русский!', locale=lang), reply_markup=keyboards.get_start(lang))


@dp.message_handler(lambda msg: CHECKER_I18N(msg, 'Последняя покупка'))
@dp.message_handler(lambda msg: CHECKER_I18N(msg, "Мои заказы"))
async def my_orders(message: Message):
    await message.answer(_('У вас нет покупок'))


@dp.message_handler(lambda msg: CHECKER_I18N(msg, 'Витрина'))
async def goods(message: Message):
    city = await City.objects.aget(name='Москва')
    products = await sync_to_async(list)(Product.objects.filter(city=city))

    await message.answer(
        _("Вы выбрали город") + f" *{city.name}*",
        parse_mode='markdown',
    )

    await message.answer(
        _('Доступные товара') + f'г.{city.name}',
        reply_markup=await keyboards.product_keyboard(products)
    )


@dp.message_handler(lambda msg: CHECKER_I18N(msg, 'Промо-код'))
async def get_text_helper_code(message: Message):
    await message.answer(
        _('Для использования промокода, введите команду `/promo XXXXX`, где ХХХХХ - промо-код, '
          'который Вы хотите использовать.'),
        parse_mode='markdown'
    )


@dp.message_handler(Text(startswith='/promo'))
async def promo(message: Message):
    await message.answer(_('Промокод не найден.'))


@dp.message_handler(lambda message: CHECKER_I18N(message, 'Контакты'))
async def get_contacts(message: Message):
    await message.answer('Контакты\n\n[@Help_Tigr](https://t.me/+18492015901)', parse_mode='markdown')


@dp.message_handler(lambda message: CHECKER_I18N(message, 'Доступ к сайту'))
async def access_to_site(message: Message):
    login = f'_tg{message.chat.id}'
    random.seed(message.chat.id)
    letters = list('qwertyuioasdfghjklzxcvbnm1234567890')
    password = ''.join(random.choices(letters, k=8)).upper()
    await message.answer(
        _("Для доступа к сайту, перейдите по ссылке https://kaifshop.biz и используйте "
          "следующие данные для входа:").replace('https://kaifshop.biz', '`https://kaifshop.biz`') + '\n\n' +
        _("Логин") + f': `{login}`\n' +
        _("Пароль") + f': `{password}`\n\n' +
        "_" + _('При недоступности сайта, воспользуйтесь VPN или TOR.') + "_",
        parse_mode='markdown',
        reply_markup=keyboards.get_site_button()
    )


@dp.message_handler(lambda message: CHECKER_I18N(message, 'Профиль'))
async def get_profile_info(message: Message):
    user = await TelegramUser.objects.aget(user_id=message.chat.id)
    profile_user = _("Профиль пользователя") + '\n\n'
    nickname = markdown.bold(_("Никнейм") + ": ") + markdown.text(user.nickname) + '\n'
    login = markdown.bold(_("Логин") + ': ') + markdown.text(f"\_tg{message.chat.id}\n")
    balance = markdown.bold(_("Баланс" + ": ")) + markdown.text(f"{int(user.balance)}RUB\n")
    count_of_orders = markdown.bold(_("Заказов") + ": ") + "0 \(0\.00RUB\)\n"
    average_check = markdown.bold(_("Средний чек") + ": ") + "0\.00RUB\n"
    comments = markdown.bold(_("Отзывов") + ": ") + markdown.text("0\n")
    sale = markdown.bold(_("Скидка") + ": ") + markdown.text("0%\n")
    language = markdown.bold(_("Язык") + ": ")

    if user.lang == "ru":
        language += "🇷🇺 Русский язык"

    if user.lang == "ka":
        language += "🇬🇪 ქართული ენა"

    if user.lang == 'uz':
        language += "🇺🇿 Oʻzbek tili"

    await message.answer(
        profile_user + nickname + login + balance + count_of_orders + average_check + comments + sale + language,
        parse_mode='markdownv2',
        reply_markup=keyboards.get_profiles_buttons()
    )


@dp.callback_query_handler(lambda call: call.data == 'get_coupons')
async def get_coupons(call: CallbackQuery):
    await call.message.answer(_("У вас нет неиспользованных купонов"))


@dp.callback_query_handler(lambda call: call.data == 'add_bot')
async def add_bot(call: CallbackQuery):
    await call.message.answer(
        _(
            "У вас нет активных ботов\n\n"
            "Во избежании блокировок общедоступных ботов, Вы можете создать своего персонального бота и иметь доступ к магазину в любое время.\n\n"
            "💰 Распространяйте своего личного бота и получайте 50RUB за каждую покупку совершенную другими пользователями в вашем боте.\n\n"
            "💰 Пользователи в вашем боте получают 50RUB на баланс после каждой покупки."
        ),
        reply_markup=keyboards.how_add_bot()
    )


@dp.callback_query_handler(lambda call: call.data == 'how_add_bot')
async def how_add_bot(call: CallbackQuery):
    await call.message.answer(
        _(
            "Чтобы создать персонального бота, Вам необходимо выполнить следующие действия:\n\n"
            "1. Зайти к @BotFather и нажать на /newbot.\n"
            "2. Ввести имя бота, можно на русском языке.\n"
            "3. Ввести логин бота на английском языке. Обратите внимание, что логин должен быть свободен и заканчиваться на «bot» или «_bot», например: namemybot.\n"
            "4. После успешного ввода данных бот пришлет сообщение с поздравлениями и специальным токеном. Этот токен необходимо скопировать и переслать нам в этот чат.\n"
            "5. Бот добавлен и готов к работе.\n"
            "Пример токена : 1234567890:RdAQ9ds8Itdxzq_Tf8JFpsPA9sqhfIS\n\n"
            "Ни в коем случае не показывайте свой токен 3м лицам."
        )
    )


@dp.callback_query_handler(lambda call: call.data == 'change_language')
async def change_language(call: CallbackQuery):
    await call.message.answer("Выберите язык/Choose language", reply_markup=keyboards.lang_select)


@dp.callback_query_handler(lambda call: call.data == 'change_nickname')
async def change_nickname(call: CallbackQuery):
    await states.ChangeNickname.enter_nickname.set()
    await call.message.answer(
        _("Введите никнейм(его будут видеть все). Мин.длина 3 символа - максимальная 12 символов. Пробелы, эмодзи и прочие символы запрещены!"),
        reply_markup=keyboards.cancel_button()
    )


@dp.message_handler(state=states.ChangeNickname.enter_nickname)
async def check_new_nickname(message: Message, state: FSMContext):
    await state.finish()
    error_message = _("Не удалось обновить никнейм. Мин.длина 3 символа - максимальная 12 символов. Пробелы и прочие символы запрещены!")

    if 3 <= len(message.text) <= 12:
        for i in message.text:
            if not i.isdigit() and not i.isalpha():
                return await message.answer(error_message)

        await change_nickname(message.chat.id, message.text)
        return await message.answer(_('Никнейм успешно изменен'))

    await message.answer(error_message)


@dp.callback_query_handler(lambda call: call.data == 'cancel', state='*')
async def cancel_do(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer(_("Действие отменено"))


@dp.message_handler(lambda msg: CHECKER_I18N(msg, 'Отзывы'))
async def checker(message: Message):
    c = await sync_to_async(list)(Comment.objects.all())
    last_page = math.ceil(len(c) / 4)
    t = _("Отзывы") + " \(" + _("Страница") + f" 1/{last_page}\)\n\n"
    comments = await get_comments(1, c)

    for i in comments:
        t += f"📦 {markdown.italic(i.name_of_product)}\n"
        t += f"{markdown.bold(i.nickname)} `{markdown.text(i.date)}`\n"
        t += f"{markdown.bold(_('Оценка'))}: {'⭐️'*i.count_of_stars}\n"
        t += f"{markdown.italic(i.content)}\n\n"

    await message.answer(
        t,
        parse_mode='markdownv2',
        reply_markup=keyboards.comments_keyboard(1, last_page)
    )


@dp.callback_query_handler(lambda call: call.data.startswith('comments_page'))
async def get_reviews(call: CallbackQuery):
    current_page = int(call.data.split(":")[1])
    c = await sync_to_async(list)(Comment.objects.all())
    last_page = math.ceil(len(c) / 4)
    t = _("Отзывы") + " \(" + _("Страница") + f" {current_page}/{last_page}\)\n\n"
    comments = await get_comments(current_page, c)

    for i in comments:
        t += f"📦 {markdown.italic(i.name_of_product)}\n"
        t += f"{markdown.bold(i.nickname)} `{markdown.text(i.date)}`\n"
        t += f"{markdown.bold(_('Оценка'))}: {'⭐️' * i.count_of_stars}\n"
        t += f"{markdown.italic(i.content)}\n\n"

    await call.message.edit_text(
        t,
        parse_mode='markdownv2',
        reply_markup=keyboards.comments_keyboard(current_page, last_page)
    )


@dp.message_handler(lambda msg: CHECKER_I18N(msg, 'Выбрать город'))
async def select_city(message: Message):
    await message.answer(_('Выберите город:'), reply_markup=await keyboards.select_city())


@dp.callback_query_handler(lambda call: call.data.startswith('city'))
async def get_city(call: CallbackQuery):
    city_id = call.data.split(":")[1]
    city = await City.objects.aget(pk=int(city_id))
    products = await sync_to_async(list)(Product.objects.filter(city=city))
    await call.message.answer(
        _("Вы выбрали город") + f" *{city.name}*",
        parse_mode='markdown',
    )

    if not products:
        return await call.message.answer(_('Нет товаров в наличии'))

    await call.message.answer(
        _('Доступные товара') + f'г.{city.name}',
        reply_markup=await keyboards.product_keyboard(products)
    )


@dp.callback_query_handler(lambda call: call.data.startswith('prod'))
async def get_desc_prod(call: CallbackQuery):
    prod_id = int(call.data.split(':')[1])
    prod = await Product.objects.aget(pk=prod_id)

    if prod.photo:
        with open(os.path.join(MEDIA_ROOT, str(prod.photo)), 'rb') as f:
            await call.message.answer_photo(f.read())

    count_of_comments = len(await sync_to_async(list)(Comment.objects.filter(name_of_product=prod.name)))
    buy_text = _("Покупок")
    rating_text = _("Рейтинг")
    comments_text = _("Отзывы")

    await call.message.answer(
        f'🍭 _{prod.name}_\n\n'
        f'🎉 *{buy_text}*: {markdown.text(prod.count_of_buy)}\n'
        f'⭐️ *{rating_text}*: {markdown.text(prod.rating)}\n'
        f'🔥 *{comments_text}*: {count_of_comments}\n\n'
        f'{prod.description or ""}',
        parse_mode='markdown',
        # reply_markup=keyboards.get_more_info(prod_id)
    )

    areas_text = ''
    areas_set = set()

    pcs = await sync_to_async(list)(prod.packs.all())
    for pack in pcs:
        for area in await sync_to_async(list)(pack.areas.all()):
            areas_set.add(area.name)

    d = {i: set() for i in areas_set}

    for pack in pcs:
        for area in await sync_to_async(list)(pack.areas.all()):
            d[area.name].add(pack.weight)

    for i in d:
        areas_text += f"*{i}*: {', '.join([f'{j}гр' for j in d[i]])}\n"

    await call.message.answer(
        _('Выберите район') + ':\n\n' + areas_text,
        parse_mode='markdown',
        reply_markup=keyboards.get_areas_keyboard(areas_set, prod_id)
    )


@dp.callback_query_handler(lambda call: call.data.startswith('area'))
async def get_packs(call: CallbackQuery):
    prod = await Product.objects.aget(pk=int(call.data.split(':')[2]))
    area_name = call.data.split(":")[1]
    packs = []
    area_id = 0

    for pack in await sync_to_async(list)(prod.packs.all()):
        for j in await sync_to_async(list)(pack.areas.all()):
            if j.name == area_name:
                area_id = j.pk
                packs.append(pack)

    for pack1 in range(len(packs) - 1):
        for pack2 in range(pack1+1, len(packs)):
            if packs[pack1].weight > packs[pack2].weight:
                packs[pack1], packs[pack2] = packs[pack2], packs[pack1]

    await call.message.answer(
        _("Выберите фасовку") + ":",
        reply_markup=keyboards.get_pack_keyboard(packs, prod.pk, get_course_usd(), area_id)
    )


@dp.callback_query_handler(lambda call: call.data.startswith('pack'))
async def get_pack(call: CallbackQuery):
    prod_id, pack_id, area_id = call.data.split(':')[1:]
    pack = await Pack.objects.aget(pk=pack_id)
    freshness = await sync_to_async(list)(pack.freshness.all())

    if freshness:
        return await call.message.answer(
            _("Выберите свежесть") + ":",
            reply_markup=keyboards.get_freshness_keyboard(freshness, prod_id, pack_id, area_id)
        )

    type_of_buy = await sync_to_async(list)(pack.type_of_buy.all())

    await call.message.answer(
        _("Выберите тип клада") + ":",
        reply_markup=keyboards.get_type_of_buy_keyboard(type_of_buy, prod_id, -1, pack_id, area_id)
    )


@dp.callback_query_handler(lambda call: call.data.startswith('fresh'))
async def get_type_of_buy(call: CallbackQuery):
    prod_id, pack_id, fresh_id, area_id = call.data.split(":")[1:]
    pack = await Pack.objects.aget(pk=pack_id)
    type_of_buy = await sync_to_async(list)(pack.type_of_buy.all())

    await call.message.answer(
        _("Выберите тип клада") + ":",
        reply_markup=keyboards.get_type_of_buy_keyboard(type_of_buy, prod_id, fresh_id, pack_id, area_id)
    )


@dp.callback_query_handler(lambda call: call.data.startswith('final'))
async def get_user_check(call: CallbackQuery):
    prod_id, fresh_id, pack_id, area_id, type_of_buy_id = call.data.split(":")[1:]
    product = await Product.objects.select_related('city').aget(pk=int(prod_id))
    pack = await Pack.objects.aget(pk=int(pack_id))
    area = await Area.objects.aget(pk=area_id)

    prod_text = markdown.bold(_("Товар")) + ": " + product.name + '\n'
    your_order = _('Ваш заказ')
    location_text = markdown.bold(_("Локация")) + ": " + f'{product.city.name}, {area.name}\n'
    pack_text = markdown.bold(_("Фасовка")) + f": {pack.weight}гр"
    discount_amount = 0

    if fresh_id != -1:
        freshness = await Freshness.objects.aget(pk=int(fresh_id))
        pack_text += f", {freshness.name}"
        discount_amount = freshness.discount

    pack_text += "\n"

    type_of_buy = await TypeOfBuy.objects.aget(pk=int(type_of_buy_id))
    type_of_buy_text = markdown.bold(_("Тип клада")) + f": {type_of_buy.name}\n"
    discount_text = markdown.bold(_("Купон")) + ": -\n\n"
    amount_rub = round(pack.price*((100-discount_amount)/100), 2)
    amount_text = markdown.bold(_("Стоимость")) + (": 🇷🇺 %.2f RUB\n🇺🇸 %.2f USD\n\n\n" % (amount_rub, round(amount_rub / get_course_usd(), 2))) + _("Выберите метод оплаты")

    await call.message.answer(
        f"{your_order}:\n\n"
        f"{prod_text}"
        f"{location_text}"
        f"{pack_text}"
        f"{type_of_buy_text}"
        f"{discount_text}"
        f"{amount_text}",
        parse_mode='markdown',
        reply_markup=keyboards.method_of_pays(amount_rub)
    )


@dp.callback_query_handler(lambda call: call.data.startswith('pay_money_from_balance'))
async def pay_money_from_balance(call: CallbackQuery):
    amount = float(call.data.split(":")[1])
    not_enough_money = _("Недостаточно средств на счету") + '.'
    amount_order = _("Стоимость заказа") + " " + str(amount) + "\n\n"
    add_balance = _("Пополните баланс и повторите снова или выберите другой метод оплаты")

    await call.message.answer(
        f"{not_enough_money} {amount_order} {add_balance}",
        reply_markup=keyboards.add_b()
    )


@dp.callback_query_handler(lambda call: call.data.startswith('pay_of_money'))
async def pay_of_money(call: CallbackQuery):
    type_pay, amount = call.data.split(":")[1:]
    order_text = _("Заказ")
    type_add_balance = _("Метод пополнения")
    to_pay = _("Куда переводить")
    help_text = _('Если платеж не поступит в течении 120 минут, заявка будет отменена!\nТех. поддержка')
    amount_text = _("Точная сумма")
    only_crypt = _('ТОЛЬКО ПО КРИПТО-ОПЛАТАМ!')

    if type_pay == 'bitcoin':
        p = await PaymentCrypto.objects.aget(title='BITCOIN')
        await call.message.answer(
            f"""`{order_text} #{random.randint(21_522, 45367)}, kaifshop`

*{type_add_balance}*: `Bitcoin`
*{to_pay}*: `{p.card}`
*{amount_text}*: `%.6f`

{help_text}: @suppds01  ({only_crypt})""" % get_btc_amount(float(amount)), parse_mode='markdown', reply_markup=keyboards.crypt_keyboard_payment('BITCOIN')
        )

    if type_pay == 'litecoin':
        p = await PaymentCrypto.objects.aget(title='LITECOIN')
        await call.message.answer(
            f"""`{order_text} #{random.randint(21_522, 45367)}, kaifshop`

*{type_add_balance}*: `Litecoin`
*{to_pay}*: `{p.card}`
*{amount_text}*: `%.6f`

{help_text}: @suppds01  ({only_crypt})""" % get_ltc_course(float(amount)), parse_mode='markdown', reply_markup=keyboards.crypt_keyboard_payment('LITECOIN')
        )

    if type_pay == 'card':
        card = await Exchange.objects.aget(name='Карта')
        warning_text = _("Если платеж не поступит в течении 60 минут, заявка будет отменена!\nПосле перевода средств, нажмите на кнопку \"Подтвердить платеж\" ниже.")
        await call.message.answer(
            f"""Заказ CB-{random.randint(2312, 4562)} ({random.randint(16_276_887, 25_236_512)})

*{type_add_balance}*: `🇷🇺 Перевод на карту`
*{to_pay}*: `{card.card}`
*{amount_text}*: `{int(float(amount)*((card.percent+100)/100))}`

{warning_text}""",
            parse_mode='markdown',
            reply_markup=keyboards.card_add()
        )


@dp.callback_query_handler(lambda call: call.data == 'check_payment_card')
async def check_payment_card(call: CallbackQuery):
    tg_help = "@supdds01"
    await call.message.answer(_("""Прoверяем ваш платеж... Время обработки заявки 5-20 минут.

При проблемах с обменом свяжитесь с оператором""") + f" {tg_help}")


@dp.callback_query_handler(lambda call: call.data == 'cancel_payment')
async def cancel_payment(call: CallbackQuery):
    await call.message.answer(_("Вы действительно хотите отменить заявку?"), reply_markup=keyboards.cancel_exc())


@dp.callback_query_handler(lambda call: call.data == 'cancel_exc')
async def cancel_exc(call: CallbackQuery):
    await call.message.answer(_("Заявка отменена"))


@dp.callback_query_handler(lambda call: call.data.startswith('qr_code'))
async def get_qr(call: CallbackQuery):
    payment = await PaymentCrypto.objects.aget(title=call.data.split(':')[1])

    await call.message.answer_photo(
        caption=_('Просканируйте этот QR-код для быстрого ввода адреса и суммы в кошельке или терминале.'),
        photo=open(os.path.join(MEDIA_ROOT, str(payment.qr_code_image)), 'rb').read()
    )


@sync_to_async
def get_comments(page_num: int, objs):
    return objs[page_num*4-4:4*page_num]


@sync_to_async
def change_lang(user_id, lang):
    TelegramUser.objects.filter(user_id=user_id).update(lang=lang)


@sync_to_async
def change_nickname(user_id, nickname):
    TelegramUser.objects.filter(user_id=user_id).update(nickname=nickname)


class Command(BaseCommand):
    help = 'not help'

    def handle(self, *args, **options):
        executor.Executor(dp).start_polling()
