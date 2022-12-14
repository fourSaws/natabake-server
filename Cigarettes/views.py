import openpyxl
from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from hashlib import sha256
from hmac import new
from os import environ
from telebot import TeleBot
import logging
from Cigarettes.serializer import *
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

def print_event(func):
    def wrapper(*args, **kwargs):
        logger.info(f"RAW AGRS: {args.data}")
        result = func(*args, **kwargs)
        logger.info(f"RESPONSE:{result.data}")
        return result
    return wrapper




@api_view(["POST"])
@permission_classes([AllowAny])
@print_event
def payment_notification(request):
    signature = request.headers.get("X-Api-Signature-Sha256")
    if "bill" not in request.POST:
        return Response("Incorrect post data", status=status.HTTP_400_BAD_REQUEST)
    if (
        "siteId",
        "billId",
        "amount",
        "status",
        "customer",
        "customFields",
        "comment",
        "creationDateTime",
        "expirationDateTime",
    ) not in request.POST.get("bill"):
        print("Incorrect post data")
        return Response("Incorrect post data", status=status.HTTP_400_BAD_REQUEST)
    currency = request.data.get("bill").get("amount").get("currency")
    amount = request.data.get("bill").get("amount").get("value")
    bill_id = request.data.get("bill").get("billId")
    site_id = request.data.get("bill").get("siteId")
    payment_status = request.data.get("bill").get("status").get("value")
    if not all((currency, amount, bill_id, site_id, payment_status)):
        return Response("Incorrect post data", status=status.HTTP_400_BAD_REQUEST)
    message = "|".join((currency, amount, bill_id, site_id, payment_status))
    my_signature = new(environ["qiwi_secret"].encode(), msg=message, digestmod=sha256).hexdigest()
    if my_signature != request.headers.get("X-Api-Signature-Sha256"):
        return Response("Wrong signature", status=status.HTTP_403_FORBIDDEN)
    bot = TeleBot(environ["teletoken"])

    try:
        order = ModelOrder.objects.get(id=int(bill_id))
    except ModelOrder.DoesNotExist:
        chat_id = request.data.get("bill").get("customer").get("account")
        if chat_id:
            try:
                bot.send_message(chat_id, "Ошибка во время оплаты, информация передана администрации")
            except Exception:
                pass
        with open("../../natabake-bot/chats.txt") as file:
            for admin_chat_id in file.readlines():
                admin_chat_id = int(admin_chat_id[:-1])
                try:
                    TeleBot(environ["notification_token"]).send_message(
                        admin_chat_id,
                        f"Пришла некорректная оплата по заказу {bill_id}, сведения о клиенте\n{request.data.get('bill').get('customer')}",
                    )
                except Exception:
                    pass
        return Response("OK", status=status.HTTP_200_OK)
    if payment_status == "PAID":
        assert float(amount) == order.sum
        order.status = "Оплачено"
        order.save()
        try:
            bot.send_message(request.data.get("bill").get("customer").get("account"), f"Заказ {bill_id} оплачен!")
        except Exception:
            pass
        username = request.data.get("bill").get("customFields").get("username")
        phone_number = request.data.get("bill").get("customer").get("phone")
        for char in (
            "_",
            "*",
            "[",
            "]",
            "(",
            ")",
            "~",
            "`",
            ">",
            "#",
            "+",
            "-",
            "=",
            "|",
            "{",
            "}",
            ".",
            "!",
        ):
            order.address = order.address.replace(char, "\\" + char)
            if username:
                username = username.replace(char, "\\" + char)
            if phone_number:
                phone_number = phone_number.replace(char, "\\" + char)
            order.cart = order.cart.replace(char, "\\" + char)
            order.address = order.address.replace("\n", "\n\t\t")

        notification_text = f"""
        *Новый заказ*
        {order.cart}
        *Итого: {order.sum}₽*
        Телефон: \\{phone_number} \\({"@" + username if username else "No nickname"}\\)
        Адрес:
        \t\t{order.address}

        Заказ оплачен *__Картой__*
            """
        with open("../../natabake-bot/chats.txt") as file:
            for admin_chat_id in file.readlines():
                admin_chat_id = int(admin_chat_id[:-1])
                try:
                    TeleBot(environ["notification_token"]).send_message(
                        admin_chat_id, notification_text, parse_mode="MarkdownV2"
                    )
                except Exception:
                    pass

    return Response("OK", status=status.HTTP_200_OK)


def mainPage(request):
    return redirect("/admin/")


@api_view(["GET"])
@permission_classes([AllowAny])
def getCart(request):
    chat_id_req = request.query_params["chat_id"]
    check_id = ModelCart.objects.filter(chat_id=chat_id_req).values()
    check_id = str(check_id)
    if chat_id_req in check_id:
        instance = ModelCart.objects.filter(chat_id=chat_id_req).values()
        serializer = CartSerializer(data=request.data, instance=instance)
        serializer.is_valid()
        return Response(instance)
    else:
        return Response({"getCart_ERROR:ID не найден"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([AllowAny])
def getBrands(request):
    all_brands = ModelBrand.objects.all().values()
    arr = [all_brands[i]["id"] for i in range(len(all_brands))]
    arr_true = [ModelBrand.objects.filter(id=i).values()[0] for i in arr if ModelProduct.objects.filter(brand=i, show=True)]
    return Response(arr_true)


@api_view(["GET"])
@permission_classes([AllowAny])
def getCategory(request):
    all_cat = ModelCategory.objects.all().values()
    arr = [all_cat[i]["id"] for i in range(len(all_cat))]
    arr_true = [
        ModelCategory.objects.filter(id=i).values()[0] for i in arr if ModelProduct.objects.filter(category=i, show=True)
    ]
    return Response(arr_true)


@api_view(["GET"])
@permission_classes([AllowAny])
def clearCart(request, **kwargs):
    chat_id_req = request.query_params["chat_id"]
    check_id = ModelCart.objects.filter(chat_id=chat_id_req).values()
    check_id = str(check_id)
    if chat_id_req in check_id:
        instance = ModelCart.objects.filter(chat_id=chat_id_req).delete()
        serializer = CartSerializer(data=request.data, instance=instance)
        serializer.is_valid()
        print(str(check_id))
        return Response({"DELETE": f"Запись удалена {check_id}"})
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([AllowAny])
def editCart(request):
    product = request.query_params["product_id"]
    chat_id = request.query_params["chat_id"]
    quantity_req = request.query_params["quantity"]
    try:
        _ = ModelCart.objects.filter(chat_id=chat_id).values("chat_id")[0]
    except IndexError:
        return Response({"Exception": "Chat ID does not Exist"}, status=status.HTTP_404_NOT_FOUND)
    same_rec = ModelCart.objects.filter(chat_id=chat_id, id=product)
    if quantity_req == "0":
        _ = ModelCart.objects.filter(chat_id=chat_id, id=product).delete()
        return Response({})
    if not same_rec.exists():
        return Response({"Exception": "ID not found in cart"}, status=status.HTTP_404_NOT_FOUND)
    else:
        a = same_rec[0]
        same_rec[0].quantity = quantity_req
        a.save()
        serializer = CartSerializer(data={"chat_id": chat_id, "quantity": quantity_req, "product": product}, instance=a)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            return Response({"Exception": "Data invalid"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def getProducts(request):
    name = request.GET.get("name")
    category = request.GET.get("category")
    id = request.GET.get("id")
    brand = request.GET.get("brand")
    instance = ModelProduct.objects.all()
    if brand:
        instance = instance.filter(brand=brand, show=True)
    if name:
        instance = instance.filter(name=name, show=True)
    if id:
        instance = instance.filter(id=id, show=True)
    if category:
        instance = instance.filter(category=category, show=True)
    instance = instance.values()
    return Response(instance)


@api_view(["GET"])
@permission_classes([AllowAny])
def addToCart(request):
    id_req = request.query_params["id"]
    chat_id = request.query_params["chat_id"]
    quantity_req = request.query_params["quantity"] if "quantity" in request.query_params else 1
    same_rec = ModelCart.objects.filter(product=id_req, chat_id=chat_id)
    if same_rec.exists():
        print(f"found same record {same_rec.values()}")
        quantity_req = same_rec[0].quantity + int(quantity_req)
        a = same_rec[0]
        a.quantity = quantity_req
        a.save()
    else:
        try:
            a = ModelCart(quantity=int(quantity_req), chat_id=int(chat_id), product=ModelProduct.objects.get(id=id_req))
        except ModelProduct.DoesNotExist:
            return Response({"Exception": "ID not found in catalogue"}, status=status.HTTP_404_NOT_FOUND)
        a.save()
    a = ModelCart.objects.get(id=a.id)
    serializer = CartSerializer(data={"chat_id": chat_id, "quantity": quantity_req, "product": id_req}, instance=a)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    else:
        return Response({"Exception": "Data invalid"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def getUser(request):
    chat_id = request.query_params["chat_id"]
    instance = ModelUser.objects.filter(chat_id=chat_id).values()
    return Response(instance)


@api_view(["GET"])
@permission_classes([AllowAny])
def createUser(request):
    chat_id = request.query_params["chat_id"]
    phone_number = request.query_params["phone_number"]
    address = request.query_params["address"]
    comment = request.query_params["comment"]
    id_check = ModelUser.objects.filter(chat_id=chat_id).values()
    if not id_check.exists():
        ModelUser.objects.create(chat_id=chat_id, address=address, phone_number=phone_number, comment=comment)
        instance = ModelUser.objects.filter(chat_id=chat_id).values()
        return Response(instance)
    else:
        ModelUser.objects.update(chat_id=chat_id, address=address, phone_number=phone_number, comment=comment)
        instance = ModelUser.objects.filter(chat_id=chat_id).values()
        return Response(instance)


@api_view(["GET"])
@permission_classes([AllowAny])
def createOrder(request):
    chat_id = request.query_params["chat_id"]
    cart = request.query_params["cart"]
    free_delivery = request.query_params["free_delivery"]
    sum = request.query_params["sum"]
    address = request.query_params["address"]
    status = request.query_params["status"]
    comment = request.GET.get("comment")
    a = ModelUser.objects.get(chat_id=chat_id)

    if comment:
        ModelOrder.objects.create(
            client=a, cart=cart, free_delivery=free_delivery, sum=sum, address=address, status=status, comment=comment
        )
        instance = ModelOrder.objects.filter(client=a).only("client")
        serializer = OrderSerializer(
            data={
                "client": chat_id,
                "cart": cart,
                "free_delivery": free_delivery,
                "sum": sum,
                "address": address,
                "status": status,
                "comment": comment,
            },
            instance=instance[0],
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    else:
        ModelOrder.objects.create(client=a, cart=cart, free_delivery=free_delivery, sum=sum, address=address, status=status)
        instance = ModelOrder.objects.filter(client=a).only("client")
        serializer = OrderSerializer(
            data={
                "client": chat_id,
                "cart": cart,
                "free_delivery": free_delivery,
                "sum": sum,
                "address": address,
                "status": status,
                "comment": comment,
            },
            instance=instance[0],
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def changeStatus(request):
    order_id = request.query_params["order_id"]
    new_status = request.query_params["new_status"]
    status = ModelOrder.objects.filter(id=order_id)
    status.update(status=new_status)
    return Response(status.values())


@api_view(["GET"])
@permission_classes([AllowAny])
def getOrder(request):
    order_id = request.query_params["order_id"]
    order = ModelOrder.objects.filter(id=order_id).values()
    return Response(order)


@api_view(["GET"])
@permission_classes([AllowAny])
def getOrders(request):
    chat_id = request.query_params["chat_id"]
    a = ModelUser.objects.get(chat_id=chat_id)
    queryset = ModelOrder.objects.filter(client=a).only("client")
    serializers = OrdersSerializer(queryset, many=True)
    return Response(serializers.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def addItem(request):
    CATEGORIES = {
        "Одноразовая электронная сигарета",
        "Одноразовая POD-система",
        "Уголь",
        "Плитка",
        "Щипцы",
        "Калауд",
        "Уплотнитель",
        "Шило",
        "Вилка",
        "Уплотнители для колбы",
        "Силикон",
        "Колба",
        "Мундштуки",
        "Табак",
        "Кальянная смесь",
        "Жидкость",
        "Табак сигаретный",
        "Бумага для самокруток",
        "Cигариллы с фильтром",
        "Pod система",
        "Электронная pod система",
        "Зажигалка",
        "Чаша",
        "Машинка для самокруток",
        "Фильтры для самокруток",
        "Сигариллы",
        "Кальянная смесь",
        "МК Кальянная смесь",
    }
    for cat in CATEGORIES:
        if not ModelCategory.objects.filter(name=cat):
            ModelCategory.objects.create(name=cat)
    book = openpyxl.load_workbook(filename="C:/Users/stepr/OneDrive/Рабочий стол/Main.xlsx")
    sheet = book["Main"]
    for i in range(2, 121):
        if sheet["B" + str(i)].value is None:
            current_brand = ""
            current_volume = 0
            for j in sheet["A" + str(i)].value.split():
                if j.isdigit():
                    current_volume = int(j)
                    break
                current_brand += j + " "
            current_brand = ModelBrand.objects.get_or_create(name=current_brand)[0]
        if str(sheet["D" + str(i)].value).startswith("Одноразовая электронная сигарета"):
            sheet["D" + str(i)].value = sheet["D" + str(i)].value.replace("Одноразовая электронная сигарета", "")
            sheet["D" + str(i)].value = sheet["D" + str(i)].value.replace(current_brand.name, "")
            sheet["D" + str(i)].value = sheet["D" + str(i)].value.replace("  ", " ")
            name = ""
            for index, word in enumerate(sheet["D" + str(i)].value.split()[::-1]):
                if word.isdigit():
                    name = " ".join(sheet["D" + str(i)].value.split()[: -(index + 1)])
                    current_volume = " ".join(sheet["D" + str(i)].value.split()[-(index + 1) :])
                    break
            category = sheet["N" + str(2)].value
            price = sheet["H" + str(i)].value
            name = name[0].upper() + name[1:]
            ModelProduct.objects.create(
                name=name,
                volume=current_volume,
                price=price,
                brand=current_brand,
                photo_url=None,
                category=ModelCategory.objects.get(name=category),
            )
    for row in range(121, 630):
        if sheet["B" + str(row)].value is None:
            # ЗНАЧИТ СТРОКА С БРЕНДОМ
            current_brand = ""
            for word in sheet["A" + str(row)].value.split():
                if word.isdigit():
                    break
                current_brand += word + " "
            current_brand = ModelBrand.objects.get_or_create(name=current_brand)[0]
        else:
            # ЗНАЧИТ СТРОКА С ТОВАРОМ
            # Определяем категорию
            found_category = False
            for i in range(1, len(sheet["D" + str(row)].value.split())):
                if " ".join(sheet["D" + str(row)].value.split()[:i]) not in CATEGORIES:
                    continue
                else:
                    category = " ".join(sheet["D" + str(row)].value.split()[:i])
                    # print(f"D{row} {sheet['D' + str(row)].value}->{' '.join(sheet['D' + str(row)].value.split()[:])}")
                    sheet["D" + str(row)].value = " ".join(sheet["D" + str(row)].value.split()[i:])
                    found_category = True
                    break
            if not found_category:
                print(f"NOT FOUND CATEGORY FOR {row=}")
                continue
            # print(f"D{row} {sheet['D' + str(row)].value}->{sheet['D' + str(row)].value.replace(current_brand, '')}")
            sheet["D" + str(row)].value = sheet["D" + str(row)].value.replace(current_brand.name, "")  # УБИРАЕМ БРЕНД
            # ДЕЛИМ НАЗВАНИЕ НА ИМЯ И КОЛ-ВО
            name = ""
            current_volume = ""
            try:
                for index, word in enumerate(sheet["D" + str(row)].value.split()[::-1]):
                    if word.isdigit():
                        # print(
                        #     f"D{row} name={' '.join(sheet['D' + str(row)].value.split()[:-(index + 1)])}\tcurrent_vol={' '.join(sheet['D' + str(row)].value.split()[-(index + 1):])}")

                        name = " ".join(sheet["D" + str(row)].value.split()[: -(index + 1)])
                        current_volume = " ".join(sheet["D" + str(row)].value.split()[-(index + 1) :])

                        break
            except AttributeError as e:
                print(f"ERROR ON {row} row")
                raise e
            name = name or sheet["D" + str(row)].value
            price = sheet["H" + str(row)].value
            name = name[0].upper() + name[1:]
            ModelProduct.objects.create(
                name=name,
                volume=current_volume or "Безразмерный",
                price=price,
                brand=current_brand,
                photo_url=None,
                category=ModelCategory.objects.get(name=category),
            )

    return render(request, "Mainpage.html")
