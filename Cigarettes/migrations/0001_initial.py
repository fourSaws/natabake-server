# Generated by Django 4.1.1 on 2022-10-02 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ModelBrand",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name": "Бренды",
                "verbose_name_plural": "Бренды",
            },
        ),
        migrations.CreateModel(
            name="ModelCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default=None, max_length=255, null=True, verbose_name="Категории")),
            ],
            options={
                "verbose_name": "Категории",
                "verbose_name_plural": "Категории",
            },
        ),
        migrations.CreateModel(
            name="ModelUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("chat_id", models.IntegerField(blank=True, null=True, verbose_name="Чат ID")),
                ("phone_number", models.CharField(max_length=11, verbose_name="Номер телефона")),
                ("address", models.CharField(max_length=255, verbose_name="Адрес")),
                ("comment", models.CharField(max_length=500, verbose_name="Комментарий")),
            ],
            options={
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
            },
        ),
        migrations.CreateModel(
            name="ModelProduct",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, null=True, verbose_name="Название")),
                ("price", models.IntegerField(default=None, null=True, verbose_name="Цена")),
                ("photo_url", models.ImageField(blank=True, default=None, upload_to="", verbose_name="Фото")),
                ("volume", models.CharField(blank=True, default=1, max_length=255, verbose_name="Кол-во")),
                (
                    "brand",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="brand_serializer",
                        to="Cigarettes.modelbrand",
                        verbose_name="Бренд",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Cigarettes.modelcategory",
                        verbose_name="Категория",
                    ),
                ),
            ],
            options={
                "verbose_name": "Каталог",
                "verbose_name_plural": "Каталог",
            },
        ),
        migrations.CreateModel(
            name="ModelOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("cart", models.CharField(max_length=500, verbose_name="Корзина")),
                ("free_delivery", models.BooleanField(default=False, verbose_name="Бесплатная доставка")),
                ("sum", models.FloatField(null=True, verbose_name="Сумма")),
                ("address", models.CharField(max_length=255, verbose_name="Адрес")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("IN_CART", "В корзине"),
                            ("WAITING_FOR_PAYMENT", "Ожидает оплаты"),
                            ("PAID", "Оплачено"),
                            ("CASH", "Наличные"),
                        ],
                        max_length=255,
                        verbose_name="Статус заказа",
                    ),
                ),
                ("comment", models.CharField(blank=True, max_length=500, null=True, verbose_name="Комментарий")),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Cigarettes.modeluser",
                        verbose_name="Чат ID клиента",
                    ),
                ),
            ],
            options={
                "verbose_name": "Заказ",
                "verbose_name_plural": "Заказы",
            },
        ),
        migrations.CreateModel(
            name="ModelCart",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("quantity", models.PositiveIntegerField(blank=True, default=int, verbose_name="Количество")),
                ("chat_id", models.PositiveIntegerField(blank=True, default=int, null=True, verbose_name="Чат ID")),
                (
                    "product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products",
                        to="Cigarettes.modelproduct",
                        verbose_name="ID в каталоге",
                    ),
                ),
            ],
            options={
                "verbose_name": "Корзина",
                "verbose_name_plural": "Корзина",
            },
        ),
    ]
