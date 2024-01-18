from django.db import models

from kaif.settings import MEDIA_ROOT


class Comment(models.Model):
    nickname = models.CharField(max_length=150, verbose_name='Ник')
    date = models.CharField(max_length=50, verbose_name='Дата публикации')
    content = models.TextField(verbose_name='Комментарий')
    count_of_stars = models.IntegerField(default=5, verbose_name='Количество звёзд')
    name_of_product = models.CharField(max_length=150, null=True, verbose_name='Название продукта')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий от {self.nickname}'


class TelegramUser(models.Model):
    user_id = models.IntegerField(primary_key=True, verbose_name='ID пользователя')
    username = models.CharField(max_length=150, null=True, blank=True)
    balance = models.IntegerField(default=0, verbose_name='Баланс (в руб.)')
    lang = models.CharField(
        max_length=2,
        choices=(('uz', "Узбекский"), ('ru', "Русский"), ('ka', "Киргизский")),
        default='ru',
        verbose_name='Язык пользователя'
    )
    nickname = models.CharField(max_length=12, verbose_name='Никнейм в боте', default='TG user')

    class Meta:
        verbose_name = 'Телеграм пользователь'
        verbose_name_plural = 'Телеграм пользователи'

    def __str__(self):
        return f'№{self.user_id} - {self.username}'


class PaymentCrypto(models.Model):
    title = models.CharField(max_length=50, verbose_name='Монета')
    code = models.CharField(max_length=5, editable=False, verbose_name='Код')
    card = models.TextField(verbose_name='Кошелёк')
    qr_code_image = models.ImageField(null=True, blank=True, verbose_name='QR-код для оплаты', upload_to=MEDIA_ROOT)

    class Meta:
        verbose_name = 'Способ оплаты (криптовалюта)'
        verbose_name_plural = 'Способы оплаты (криптовалюта)'

    def __str__(self):
        return self.title


class City(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название города')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Area(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название района')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город')

    class Meta:
        verbose_name = 'Район'
        verbose_name_plural = 'Районы'

    def __str__(self):
        return f'{self.city} - {self.name}'


class Freshness(models.Model):
    name = models.CharField(max_length=150)
    discount = models.FloatField(verbose_name='Скидка в процентах', default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Свежесть'
        verbose_name_plural = "Свежести"


class TypeOfBuy(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип клада'
        verbose_name_plural = 'Типы кладов'


class Pack(models.Model):
    weight = models.FloatField(verbose_name='Вес')
    price = models.IntegerField(verbose_name='Цена')
    areas = models.ManyToManyField(Area, verbose_name='Районы')
    freshness = models.ManyToManyField(Freshness, verbose_name='Свежесть')
    type_of_buy = models.ManyToManyField(TypeOfBuy, verbose_name='Тип клада')

    class Meta:
        verbose_name = 'Фасовка'
        verbose_name_plural = 'Фасовки'

    def __str__(self):
        return f'{self.weight} г за {self.price} руб'


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название товара')
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    packs = models.ManyToManyField(Pack, verbose_name='Фасовки')
    photo = models.ImageField(verbose_name='Фото товара', null=True, upload_to=MEDIA_ROOT)
    count_of_buy = models.TextField(verbose_name='Количество покупок', default='50+')
    rating = models.FloatField(verbose_name='Рейтинг', default='5.0')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')

    def __str__(self):
        return f'{self.city} - {self.name}'

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class Exchange(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название обменника')
    card = models.CharField(max_length=100, verbose_name='Номер карты')
    percent = models.FloatField(verbose_name='Процент комиссии')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Обменник'
        verbose_name_plural = 'Обменники'
