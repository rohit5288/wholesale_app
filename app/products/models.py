from django.db import models
from accounts.models import *

class ProductColors(CommonInfo):
    color_code=models.CharField(max_length=255,null=True,blank=True)

    class Meta:
        db_table="product_colors"
        managed=True

class ProductCategory(CommonInfo):
    title=models.CharField(max_length=255,null=True,blank=True)
    image=models.FileField(upload_to="category_images/",null=True,blank=True)
    
    class Meta:
        db_table="product_category"
        managed=True

class Products(CommonInfo):
    title=models.CharField(max_length=255,null=True,blank=True)
    description=models.CharField(max_length=255,null=True,blank=True)
    category=models.ForeignKey(ProductCategory,on_delete=models.CASCADE,null=True,blank=True)
    images=models.ManyToManyField(Images)
    fabric_type=models.CharField(max_length=255,null=True,blank=True)
    delivery_timeline=models.PositiveIntegerField(default=0,null=True,blank=True)
    size=models.CharField(max_length=10,null=True,blank=True)
    color=models.ManyToManyField(ProductColors)
    cost=models.FloatField(default=0.0,null=True,blank=True)
    status = models.PositiveIntegerField(default=ACTIVE_PRODUCT, choices=PRODUCT_STATUS,null=True, blank=True)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name="products")

    class Meta:
        db_table="product"
        managed=True

class Orders(CommonInfo):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name="user_orders")
    product=models.ForeignKey(Products,on_delete=models.CASCADE,null=True,blank=True,related_name="product_orders")
    price=models.FloatField(default=0.0,null=True,blank=True)
    stock=models.PositiveIntegerField(null=True,blank=True)
    amount = models.FloatField(null=True, blank=True)
    service_fee = models.FloatField(null=True, blank=True)
    total_amount = models.FloatField(null=True, blank=True)
    status = models.PositiveIntegerField(choices=ORDER_STATUS,default=PENDING_ORDER)

    class Meta:
        db_table="orders"
        managed=True