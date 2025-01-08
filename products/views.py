from accounts.common_imports import *
from products.models import *


class CategoriesListing(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        categories=ProductCategory.objects.all().order_by('-created_on')
        if request.GET.get('title'):
            categories=categories.filter(title__icontains=request.GET.get('title'))
        if request.GET.get('created_on'):
            categories=categories.filter(created_on__date=request.GET.get('created_on'))
        if not categories and request.GET:
            messages.success(request,"Product Categories Not Found!")
        return render(request,"products/categories.html",{
            "head_title":"Category Management",
            "categories":get_pagination(request,categories),
            "title":request.GET.get('title',""),
            "created_on":request.GET.get('created_on',""),
        })
    def post(self,request,*args,**kwargs):
        title = request.POST.get('title')        
        # Check if the title already exists
        category, created = ProductCategory.objects.get_or_create(
            title=title,
        )
        if not created:
            messages.error(request,"Category already exists!")
            return redirect('products:category_list')
        messages.success(request, 'Category Created Successfully!')
        return redirect('products:category_list')


class AddDefaultCategory(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        categories=GetCategories()
        for data in categories: 
            if not ProductCategory.objects.filter(title=data['title']).exists():
                ProductCategory.objects.create(
                    title = data['title'] if data['title'] else "",
                )      
        messages.success(request,'Categories Added Successfully!')
        return redirect('products:category_list')

class ImportCategoriesdata(View):
    def post(self,request,*args,**kwargs):
        file=request.FILES.get('file')
        try:
            data = pd.read_csv(file)
            df = pd.DataFrame(data, columns=['Title'])
            for row,item in data.iterrows():
                if not ProductCategory.objects.filter(title=item["Title"]).exists():
                        ProductCategory.objects.create(
                            title = item["Title"] if item["Title"] else "",
                        )
            messages.success(request, 'Categories imported successfully!')
            return redirect("products:category_list")
        except:
            messages.success(request,"There is something wrong with uploaded file. Please check and try again.")
            return redirect("products:category_list")

class ViewCategory(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        try:
            category=ProductCategory.objects.get(id=self.kwargs.get('id'))
        except:
            messages.error(request,"Category does not exists!")
            return redirect('products:category_list')
        return render(request,"products/view-category.html",{
            "head_title":"Category Management",
            "category":category,
        })


class UpdateCategory(View):
    @method_decorator(admin_only)
    def post(self,request,*args,**kwargs):
        title = request.POST.get('e_title')
        category=ProductCategory.objects.get(id=request.POST.get('category_id'))
        # Check if the title already exists
        if ProductCategory.objects.filter(title=title).exclude(id=category.id):
            messages.error(request,"Category already exists!")
            return redirect('products:category_list')
        category.title=title
        category.save()
        messages.success(request, 'Category Updated Successfully!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class DeleteCategory(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        category=ProductCategory.objects.get(id=self.kwargs.get('id'))
        if Products.objects.filter(category=category).exists():
            messages.error(request,"Category cannot be deleted!")
        else:
            category.delete()
            messages.success(request, 'Category Deleted Successfully!')
        return redirect('products:category_list')


class ProductsList(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        products=Products.objects.all().order_by('-created_on')
        if request.GET.get('title'):
            products=products.filter(title__icontains=request.GET.get('title'))
        if request.GET.get('created_on'):
            products=products.filter(created_on__date=request.GET.get('created_on'))
        if not products and request.GET:
            messages.success(request,"Products Not Found!")
        return render(request,"products/products-list.html",{
            "head_title":"Products Management",
            "products":get_pagination(request,products),
            "title":request.GET.get('title',""),
            "created_on":request.GET.get('created_on',""),
        })

class ViewProduct(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        try:
            product=Products.objects.get(id=self.kwargs.get('id'))
        except:
            messages.error(request,"Product does not exists!")
            return redirect('products:products_list')
        return render(request,"products/view-product.html",{
            "head_title":"Products Management",
            "product":product,
        })


class AddProduct(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        return render(request,"products/add-product.html",{
            "head_title":"Products Management",
        })
    def post(self,request,*args,**kwargs):


        return redirect('products:products_list')
