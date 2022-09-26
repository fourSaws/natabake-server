from rest_framework import serializers
from Cigarettes.models import *


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    class Meta:
        model = ModelCategory
        fields = ('__all__')


class ForGetProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='name',read_only=True)
    brand = serializers.SlugRelatedField(slug_field='id', read_only=True)
    class Meta:
        model = ModelProduct
        fields = ('id', 'name', 'brand', 'price','category','volume',)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelProduct
        fields = ('id', 'name', 'brand', 'price','category','volume',)


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    quantity = serializers.IntegerField(required=False)
    chat_id = serializers.IntegerField(required=False)

    class Meta:
        model = ModelCart
        fields = ('product', 'quantity', 'chat_id')


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelProduct
        fields = ('brand',)
