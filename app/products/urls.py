import os
import environ
from django.contrib import admin
from django.urls import re_path
from .views_api import *
from .views_api import *
from .views import *
env = environ.Env()
environ.Env.read_env()

admin.autodiscover()
app_name = 'products'

urlpatterns = [
    ## Product Category Management Admin Panel
    re_path(r'^categories-listing/$',CategoriesListing.as_view(),name="category_list"),
    re_path(r'^add-default-categories/$',AddDefaultCategory.as_view(),name="add_default_categories"),
    re_path(r'^view-category/(?P<id>[-\w]+)/$',ViewCategory.as_view(),name="view_category"),
    re_path(r'^update-category/$',UpdateCategory.as_view(),name="update_category"),
    re_path(r'^delete-category/(?P<id>[-\w]+)/$',DeleteCategory.as_view(),name="delete_category"),
    re_path(r'^import-categories-data/$',ImportCategoriesdata.as_view(),name="import_categories_data"),

    ## Product Management Admin Panel
    re_path(r'^products-list/$',ProductsList.as_view(),name="products_list"),
    re_path(r'^view-product/(?P<id>[-\w]+)/$',ViewProduct.as_view(),name="view_product"),

    ##Product Management APIs (Seller)
    re_path(r'^list-categories-api/$',CategoriesListingAPI.as_view(),name="list_categories_api"),
    re_path(r'^add-product-api/$',AddProductAPI.as_view(),name="add_product_api"),
    re_path(r'^list-products-api/$',ProductsListAPI.as_view(),name="add_product_api"),
    re_path(r'^update-product-api/$',UpdateProductAPI.as_view(),name="update_product_api"),
    re_path(r'^product-detail-api/$',ProductDetailsAPI.as_view(),name="product_detail_api"),
    
    ##Product Management APIs (Buyer)
    re_path(r'^all-products-api/$',AllProductsListAPI.as_view(),name="all_products_api"),
]
