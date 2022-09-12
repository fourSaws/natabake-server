from django.db import models
from django.core.files.storage import default_storage
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
        verbose_name='Бренды'
        verbose_name_plural = 'Бренды'


class ModelProduct(models.Model):
    name = models.CharField(max_length=255, null=True, verbose_name='Название')
    price = models.IntegerField(default=None, null=True, verbose_name='Цена')
    brand = models.ForeignKey(blank=True, verbose_name='Бренд', to=ModelBrand, on_delete=models.CASCADE,related_name='brand_serializer')
    photo_url = models.ImageField(default=None, verbose_name='Фото',blank=True)
    volume = models.CharField(max_length=255,default=1,verbose_name='Кол-во',blank=True)
    category = models.ForeignKey(to=ModelCategory,on_delete=models.CASCADE,default=None,null=True,verbose_name='Категория')

    class Meta:
        verbose_name = 'Каталог'
        verbose_name_plural = 'Каталог'

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
