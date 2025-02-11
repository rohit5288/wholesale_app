from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from .models import *

class ImageSerializer(ModelSerializer):
    class Meta:
        model=Images
        fields=("id","image")

class CategoriesSerializer(ModelSerializer):
    product_count=SerializerMethodField()
    def get_product_count(self,obj):
        request=self.context.get('request')
        return Products.objects.filter(created_by=request.user,category=obj).count()

    class Meta:
        model=ProductCategory
        fields=("id","title","image","product_count")

class ProductColorSerializer(ModelSerializer):

    class Meta:
        model=ProductColors
        fields=("id","color_code")

class ProductListingSerializer(ModelSerializer):
    category=CategoriesSerializer()
    images=SerializerMethodField()
    def get_images(self,obj):
        request=self.context.get('request')
        return ImageSerializer([obj.images.first()],many=True,context={"request":request}).data if obj.images.first() else None
    class Meta:
        model=Products
        fields=("id","title","description","images","cost","category","status")

class ProductDetailSerializer(ModelSerializer):
    images=SerializerMethodField()
    color=SerializerMethodField()
    category=CategoriesSerializer()

    def get_images(self,obj):
        request=self.context.get("request")
        return ImageSerializer(obj.images.all(),many=True,context={"request":request}).data
    def get_color(self,obj):
        request=self.context.get("request")
        return ProductColorSerializer(obj.color.all(),many=True,context={"request":request}).data
    
    class Meta:
        model=Products
        fields="__all__"