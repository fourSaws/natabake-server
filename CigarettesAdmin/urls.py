from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from Cigarettes.views import mainPage, clearCart,getCart, editCart, getProducts, getBrands,addToCart,addItem,getCategory

#TODO:
'''
getCart(chat_id:int)->list[CartItem] - done
clearCart(chat_id:int)->response, - done
editCart(id:int, quantity:int,chat_id=int) -> CartItem  # если quantity=0 - удалить и вернуть пустой ответ - ?
addToCart(chat_id:int,id_product:int)->response
getProducts(brand:str=None,name:str,id:int)->list[Product] - done
getBrands()->list[str] - done
getCategories()->list[str] 
'''


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', mainPage),
    path('api/getCart', getCart),
    path('api/clearCart', clearCart),
    path('api/editCart',editCart),
    path('api/getProducts',getProducts),
    path('api/getBrands',getBrands),
    path('api/addToCart',addToCart),
    path('api/addItem',addItem),
    path('api/getCategory',getCategory),
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    #path('admin/', include(admin.site.urls))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

