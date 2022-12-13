import hashlib
import os
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.core.files.storage import default_storage, FileSystemStorage
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver


class ModelCategory(models.Model):
    name = models.CharField(max_length=255, null=True, default=None, verbose_name='Категории')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Категории'
        verbose_name_plural = 'Категории'


class ModelBrand(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Бренды'
        verbose_name_plural = 'Бренды'


class UUIDFileStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        _, ext = os.path.splitext(name)
        return uuid4().hex + ext


class ModelProduct(models.Model):
    name = models.CharField(max_length=255, null=True, verbose_name='Название')
    price = models.IntegerField(default=None, null=True, verbose_name='Цена')
    brand = models.ForeignKey(blank=True, verbose_name='Бренд', to=ModelBrand, on_delete=models.CASCADE,
                              related_name='brand_serializer')
    photo_url = models.ImageField(default=None, upload_to='someimages', storage=UUIDFileStorage(), verbose_name='Фото',
                                  blank=True)
    volume = models.CharField(max_length=255, default=1, verbose_name='Объём/количество/размер', blank=True)
    category = models.ForeignKey(to=ModelCategory, on_delete=models.CASCADE, default=None, null=True,
                                 verbose_name='Категория')
    show = models.BooleanField(default=True, blank=True, verbose_name='Показывать')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f"{self.name}"


class ModelCart(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(ModelProduct, on_delete=models.CASCADE, null=True, blank=True,
                                verbose_name='ID в каталоге', related_name='products')
    quantity = models.PositiveIntegerField(default=int, blank=True, verbose_name='Количество')
    chat_id = models.PositiveIntegerField(default=int, blank=True, null=True, verbose_name='Чат ID')

    def __str__(self):
        return f"{self.id}"

    @property
    def Multiply(self):
        return self.product.price * self.quantity

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'


class ModelUser(models.Model):
    chat_id = models.IntegerField(null=True, blank=True, verbose_name="Чат ID")
    phone_number = models.CharField(max_length=11, verbose_name="Номер телефона")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    comment = models.CharField(max_length=500, verbose_name="Комментарий")

    def __str__(self):
        return f"{self.chat_id}"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class ModelOrder(models.Model):
    IN_CART = 'IN_CART'
    WAITING_FOR_PAYMENT = 'WAITING_FOR_PAYMENT'
    PAID = 'PAID'
    CASH = 'CASH'
    STATUS_CHOICES = [
        (IN_CART, 'В корзине'),
        (WAITING_FOR_PAYMENT, 'Ожидает оплаты'),
        (PAID, 'Оплачено'),
        (CASH, 'Наличные')
    ]

    client = models.ForeignKey('ModelUser', on_delete=models.CASCADE, verbose_name='Чат ID клиента')
    cart = models.CharField(max_length=500, verbose_name='Корзина')
    free_delivery = models.BooleanField(default=False, verbose_name='Бесплатная доставка')
    sum = models.FloatField(null=True, verbose_name='Сумма')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    status = models.CharField(choices=STATUS_CHOICES, max_length=255, verbose_name='Статус заказа')
    comment = models.CharField(max_length=500, blank=True, null=True, verbose_name='Комментарий')

    def __str__(self):
        return f"{self.client}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
