import openpyxl
from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from Cigarettes.serializer import *
from django.shortcuts import redirect


def mainPage(request):
        return redirect('/admin/')


@api_view(['GET'])
@permission_classes([AllowAny])
def getCart(request):
    chat_id_req = request.query_params['chat_id']
    check_id = ModelCart.objects.filter(chat_id=chat_id_req).values()
    check_id = str(check_id)
    if chat_id_req in check_id:
        instance = ModelCart.objects.filter(chat_id=chat_id_req).values()
        serializer = CartSerializer(data=request.data, instance=instance)
        serializer.is_valid()
        return Response(instance)
    else:
        return Response({'getCart_ERROR:ID не найден'})


@api_view(['GET'])
@permission_classes([AllowAny])
def getBrands(request):
    instance = ModelBrand.objects.all().values()
    return Response(instance)

@api_view(['GET'])
@permission_classes([AllowAny])
def getCategory(request):
    instance = ModelCategory.objects.all().values()
    return Response(instance)


@api_view(['GET'])
@permission_classes([AllowAny])
def clearCart(request, **kwargs):
    chat_id_req = request.query_params['chat_id']
    check_id = ModelCart.objects.filter(chat_id=chat_id_req).values()
    check_id = str(check_id)
    if chat_id_req in check_id:
        instance = ModelCart.objects.filter(chat_id=chat_id_req).delete()
        serializer = CartSerializer(data=request.data, instance=instance)
        serializer.is_valid()
        print(str(check_id))
        return Response({'DELETE': f'Запись удалена {check_id}'})
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def editCart(request):
    product = request.query_params['product_id']
    chat_id = request.query_params['chat_id']
    quantity_req = request.query_params['quantity']
    try:
        _ = ModelCart.objects.filter(chat_id=chat_id).values('chat_id')[0]
    except IndexError:
        return Response({'Exception': 'Chat ID does not Exist'})
    same_rec = ModelCart.objects.filter(chat_id=chat_id)
    if quantity_req == "0":
        _ = ModelCart.objects.filter(chat_id=chat_id).delete()
        return Response({})
    if not same_rec.exists():
        try:
            a = ModelCart(quantity=int(quantity_req), chat_id=int(chat_id),
                          product=ModelProduct.objects.get(id=product))
        except ModelProduct.DoesNotExist:
            return Response({"Exception": "ID not found in catalogue"}, status=status.HTTP_404_NOT_FOUND)
        a.save()
        a = ModelCart.objects.get(id=a.id)
        serializer = CartSerializer(data={'chat_id': chat_id, 'quantity': quantity_req, 'product': product},
                                    instance=a)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            return Response({'Exception': 'Data invalid'})
        return Response(serializer.data)
    else:
        a = same_rec[0]
        same_rec[0].quantity = quantity_req
        a.save()
        serializer = CartSerializer(data={'chat_id': chat_id, 'quantity': quantity_req, 'product': product},
                                    instance=a)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            return Response({'Exception': 'Data invalid'})
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def getProducts(request):
    name = request.GET.get('name')
    category = request.GET.get('category')
    id = request.GET.get('id')
    brand = request.GET.get('brand')
    if brand:
        instance = ModelProduct.objects.filter(brand=brand).values()
        return Response(instance)
    if name:
        instance = ModelProduct.objects.filter(name=name).values()
        return Response(instance)
    if id:
        instance = ModelProduct.objects.filter(id=id).values()
        return Response(instance)

    if category:
        instance = ModelProduct.objects.filter(category=category).values()
        return Response(instance)

@api_view(['GET'])
@permission_classes([AllowAny])
def addToCart(request):
    id_req = request.query_params['id']
    chat_id = request.query_params['chat_id']
    quantity_req = (request.query_params['quantity'] if 'quantity' in request.query_params else 1)
    same_rec = ModelCart.objects.filter(product=id_req, chat_id=chat_id)
    if same_rec.exists():
        print(f'found same record {same_rec.values()}')
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
    serializer = CartSerializer(data={'chat_id': chat_id, 'quantity': quantity_req, 'product': id_req}, instance=a)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    else:
        return Response({'Exception': 'Data invalid'})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def addItem(request):
    CATEGORIES = {"Одноразовая электронная сигарета",
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
                  "МК Кальянная смесь"}
    for cat in CATEGORIES:
        if not ModelCategory.objects.filter(name=cat):
            ModelCategory.objects.create(name=cat)
    book = openpyxl.load_workbook(filename='C:/Users/stepr/OneDrive/Рабочий стол/Main.xlsx')
    sheet = book['Main']
    for i in range(2, 121):
        if sheet['B' + str(i)].value is None:
            current_brand = ''
            current_volume = 0
            for j in sheet['A' + str(i)].value.split():
                if j.isdigit():
                    current_volume = int(j)
                    break
                current_brand += j + ' '
            current_brand=ModelBrand.objects.get_or_create(name=current_brand)[0]
        if str(sheet['D' + str(i)].value).startswith("Одноразовая электронная сигарета"):
            sheet['D' + str(i)].value = sheet['D' + str(i)].value.replace('Одноразовая электронная сигарета', '')
            sheet['D' + str(i)].value = sheet['D' + str(i)].value.replace(current_brand.name, '')
            sheet['D' + str(i)].value = sheet['D' + str(i)].value.replace("  ", ' ')
            name = ''
            for index, word in enumerate(sheet['D' + str(i)].value.split()[::-1]):
                if word.isdigit():
                    name = ' '.join(sheet['D' + str(i)].value.split()[:-(index + 1)])
                    current_volume = ' '.join(sheet['D' + str(i)].value.split()[-(index + 1):])
                    break
            category = sheet['N' + str(2)].value
            price = sheet['H' + str(i)].value
            name = name[0].upper() + name[1:]
            ModelProduct.objects.create(name=name, volume=current_volume, price=price, brand=current_brand,
                                        photo_url=None, category=ModelCategory.objects.get(name=category))
    for row in range(121, 630):
        if sheet['B' + str(row)].value is None:
            # ЗНАЧИТ СТРОКА С БРЕНДОМ
            current_brand = ''
            for word in sheet['A' + str(row)].value.split():
                if word.isdigit():
                    break
                current_brand += word + ' '
            current_brand = ModelBrand.objects.get_or_create(name=current_brand)[0]
        else:
            # ЗНАЧИТ СТРОКА С ТОВАРОМ
            # Определяем категорию
            found_category = False
            for i in range(1, len(sheet['D' + str(row)].value.split())):
                if ' '.join(sheet['D' + str(row)].value.split()[:i]) not in CATEGORIES:
                    continue
                else:
                    category = ' '.join(sheet['D' + str(row)].value.split()[:i])
                    # print(f"D{row} {sheet['D' + str(row)].value}->{' '.join(sheet['D' + str(row)].value.split()[:])}")
                    sheet['D' + str(row)].value = ' '.join(sheet['D' + str(row)].value.split()[i:])
                    found_category = True
                    break
            if not found_category:
                print(f"NOT FOUND CATEGORY FOR {row=}")
                continue
            # print(f"D{row} {sheet['D' + str(row)].value}->{sheet['D' + str(row)].value.replace(current_brand, '')}")
            sheet['D' + str(row)].value = sheet['D' + str(row)].value.replace(current_brand.name, '')  # УБИРАЕМ БРЕНД
            # ДЕЛИМ НАЗВАНИЕ НА ИМЯ И КОЛ-ВО
            name = ''
            current_volume = ''
            try:
                for index, word in enumerate(sheet['D' + str(row)].value.split()[::-1]):
                    if word.isdigit():
                        # print(
                        #     f"D{row} name={' '.join(sheet['D' + str(row)].value.split()[:-(index + 1)])}\tcurrent_vol={' '.join(sheet['D' + str(row)].value.split()[-(index + 1):])}")

                        name = ' '.join(sheet['D' + str(row)].value.split()[:-(index + 1)])
                        current_volume = ' '.join(sheet['D' + str(row)].value.split()[-(index + 1):])

                        break
            except AttributeError as e:
                print(f'ERROR ON {row} row')
                raise e
            name = name or sheet['D' + str(row)].value
            price = sheet['H' + str(row)].value
            name = name[0].upper() + name[1:]
            ModelProduct.objects.create(name=name, volume=current_volume or 'Безразмерный', price=price,
                                        brand=current_brand,
                                        photo_url=None,
                                        category=ModelCategory.objects.get(name=category))

    return render(request, 'Mainpage.html')
