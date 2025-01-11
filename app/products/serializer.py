from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from .models import *


class CategoriesSerializer(ModelSerializer):

    class Meta:
        model=ProductCategory
        fields=("id","title")

class ProductColorSerializer(ModelSerializer):

    class Meta:
        model=ProductColors
        fields=("color_code")

class ProductListingSerializer(ModelSerializer):
    category=CategoriesSerializer()
    image=SerializerMethodField()
    def get_image(self,obj):
        request=self.context.get('request')
        return request.build_absolute_uri(obj.images.first().image.url) if obj.images.first() else None
    class Meta:
        model=Products
        fields=("id","title","image","cost","category")

class ProductDetailSerializer(ModelSerializer):
    images=SerializerMethodField()
    color=SerializerMethodField()
    category=CategoriesSerializer()

    def get_images(self,obj):
        request=self.context.get("request")
        return [request.build_absolute_uri(image) for image in obj.images.all()]
    def get_images(self,obj):
        request=self.context.get("request")
        return ProductColorSerializer(obj.color.all(),many=True,context={"request":request}).data
    
    class Meta:
        model=Products
        fields= "__all__"