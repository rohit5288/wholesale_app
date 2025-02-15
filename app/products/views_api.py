from .models import *
from accounts.common_imports import *
from accounts.models import *
from products.models import *
from .serializer import *



class CategoriesListingAPI(APIView):
    """
    Categories Listing API
    """
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Products Management (Seller)"],
        operation_id="categories_list",
        operation_description="Categories List",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_NUMBER , description='page'),
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING , description='search'),
        ]
    )
    def get(self, request, *args, **kwargs):
        categories=ProductCategory.objects.all().order_by('title')
        if request.query_params.get('search'):
            categories=categories.filter(title__icontains=request.query_params.get('search'))
        start,end,meta_data= GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,categories)
        data=CategoriesSerializer(categories[start:end],many=True,context={"request":request}).data
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class ProductsListAPI(APIView):
    """
    Product Listing API
    """
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Products Management (Seller)"],
        operation_id="product_list",
        operation_description="Product List",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_NUMBER , description='page'),
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING , description='search'),
        ]
    )
    def get(self, request, *args, **kwargs):
        products=Products.objects.filter(created_by=request.user).order_by('title')
        if request.query_params.get('search'):
            products=products.filter(title__icontains=request.query_params.get('search'))
        start,end,meta_data= GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,products)
        data=ProductListingSerializer(products[start:end],many=True,context={"request":request}).data
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class AddProductAPI(APIView):
    """
    Add Product API
    """
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Products Management (Seller)"],
        operation_id="add_product",
        operation_description="Add Product",
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Title'),
            openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Description'),
            openapi.Parameter('category_id', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Category ID'),
            openapi.Parameter('fabric_type', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Fabric Type'),
            openapi.Parameter('delivery_timeline', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Fabric Type'),
            openapi.Parameter('size', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Size'),
            openapi.Parameter('color', openapi.IN_FORM, type=openapi.TYPE_ARRAY,items=openapi.Items(type=openapi.TYPE_STRING), description='Color Array'),
            openapi.Parameter('cost', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Cost'),
            
            openapi.Parameter('images', openapi.IN_FORM, type=openapi.TYPE_ARRAY,items=openapi.Items(type=openapi.TYPE_FILE), description='Product Images'),
        ]
    )
    def post(self, request, *args, **kwargs):
        ## Validate Required Fields
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'title',"post","Please enter title"),
            RequiredFieldValidations.validate_field(self,request,'description',"post","Please enter description"),
            RequiredFieldValidations.validate_field(self,request,'category_id',"post","Please select category"),
            RequiredFieldValidations.validate_field(self,request,'fabric_type',"post","Please enter fabric type"),
            RequiredFieldValidations.validate_field(self,request,'delivery_timeline',"post","Please enter delivery timeline"),
            RequiredFieldValidations.validate_field(self,request,'size',"post","Please enter size"),
            RequiredFieldValidations.validate_field(self,request,'cost',"post","Please enter date cost"),
            RequiredFieldValidations.validate_field(self,request,'color',"post","Please select colors"),
            RequiredFieldValidations.validate_field(self,request,'images',"post","Please upload images"),
        ]))
        if Products.objects.filter(title=request.data.get('title'),created_by=request.user).exists():
            return Response({"message":"Product already exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            category=ProductCategory.objects.get(id=request.data.get('category_id'))
        except:
            return Response({"message":"Category does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        product=Products.objects.create(
            title=request.data.get('title'),
            description=request.data.get('description'),
            category=category,
            fabric_type=request.data.get('fabric_type'),
            delivery_timeline=request.data.get('delivery_timeline'),
            size=request.data.get('size'),
            cost=float(request.data.get('cost')),
            created_by=request.user
        )
        for color_code in request.data.getlist('color'):
            product.color.add(ProductColors.objects.get_or_create(color_code=color_code)[0])
        for image in request.FILES.getlist('images'):
            product.images.add(Images.objects.create(image=image))
        product.save()
        product.refresh_from_db()
        data=ProductDetailSerializer(product,context={"request":request}).data
        return Response({"message":f"Product added successfully!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class UpdateProductAPI(APIView):
    """
    Update Product API
    """
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Products Management (Seller)"],
        operation_id="update_product",
        operation_description="Update Product",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Product ID'),
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Title'),
            openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Description'),
            openapi.Parameter('category_id', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Category ID'),
            openapi.Parameter('fabric_type', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Fabric Type'),
            openapi.Parameter('delivery_timeline', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Fabric Type'),
            openapi.Parameter('size', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Size'),
            openapi.Parameter('color', openapi.IN_FORM, type=openapi.TYPE_ARRAY,items=openapi.Items(type=openapi.TYPE_STRING), description='Color Array'),
            openapi.Parameter('cost', openapi.IN_FORM, type=openapi.TYPE_STRING , description='Cost'),
            openapi.Parameter('status', openapi.IN_FORM, type=openapi.TYPE_NUMBER , description='1:ACTIVE, 2:INACTIVE, 3:DELETED'),
            
            openapi.Parameter('old_images', openapi.IN_FORM, type=openapi.TYPE_ARRAY,items=openapi.Items(type=openapi.TYPE_FILE), description='Old Images'),
            openapi.Parameter('images', openapi.IN_FORM, type=openapi.TYPE_ARRAY,items=openapi.Items(type=openapi.TYPE_FILE), description='Product Images'),
        ]
    )
    def patch(self, request, *args, **kwargs):
        try:
            product=Products.objects.get(id=request.data.get('id'))
        except:
            return Response({"message":"Product does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        if Products.objects.filter(title=request.data.get('title'),created_by=request.user).exclude(id=product.id).exists():
            return Response({"message":"Product already exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        if request.data.get('title'):
            product.title=request.data.get('title')
        if request.data.get('description'):
            product.description=request.data.get('description')
        if request.data.get('category'):
            try:
                category=ProductCategory.objects.get(id=request.data.get('category_id'))
            except:
                return Response({"message":"Category does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            product.category=category
        if request.data.get('fabric_type'):
            product.fabric_type=request.data.get('fabric_type')
        if request.data.get('delivery_timeline'):
            product.delivery_timeline=request.data.get('delivery_timeline')
        if request.data.get('size'):
            product.size=request.data.get('size')
        if request.data.get('cost'):
            product.cost=float(request.data.get('cost'))
        if request.data.get('status'):
            product.status=int(request.data.get('status'))
        if request.data.get('color'):
            product.color.clear()
            for color_code in request.data.getlist('color'):
                product.color.add(ProductColors.objects.get_or_create(color_code=color_code)[0])
        if request.FILES.getlist('old_images'):
            product.images.exclude(id__in=request.data.getlist('old_images')).delete()
        if request.FILES.getlist('images'):
            for image in request.FILES.getlist('images'):
                product.images.add(Images.objects.create(image=image))
        product.save()
        product.refresh_from_db()
        data=ProductDetailSerializer(product,context={"request":request}).data
        return Response({"message":f"Product updated successfully!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class ProductDetailsAPI(APIView):
    """
        Product Details API
    """
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Products Management (Seller)"],
        operation_id="product_details",
        operation_description="Product Details",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_STRING , description='Product ID'),
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            product=Products.objects.get(id=request.query_params.get('id'))
        except:
            return Response({"message":"Product does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        data=ProductDetailSerializer(product,context={"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
