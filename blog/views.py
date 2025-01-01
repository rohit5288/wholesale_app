from accounts.common_imports import *
from .views import *
from .models import *
from django.http import HttpResponseRedirect


class BlogList(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        blogs = Blogs.objects.all().order_by('-created_on')
        if request.GET.get('title'):
            blogs = blogs.filter(title__icontains = request.GET.get('title'))
        if request.GET.get('status'):
            blogs = blogs.filter(status = request.GET.get('status'))
        if request.GET.get('created_on'):
            blogs = blogs.filter(created_on__date = request.GET.get('created_on'))
        if request.GET and not blogs:
            messages.error(request, 'No Data Found')
        return render(request, 'blog/blog-list.html',{
            "blogs":get_pagination(request, blogs),
            "head_title":"Blog Management",
            "title":request.GET.get('title',''),
            "status":request.GET.get('status',''),
            "created_on":request.GET.get('created_on',''),
        })
    

class AddBlog(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        return render(request, 'blog/add-blog.html',{'head_title':'Blog Management'})
    def post(self,request,*args,**kwargs):
        if Blogs.objects.filter(title=request.POST.get('title')):
            messages.error(request, 'Blog Already Exists')
            return render(request, 'blog/add-blog.html',{'head_title':'Blog Management'})
        else:
            blog = Blogs.objects.create(
                title = request.POST.get('title'),
                description = request.POST.get('description'),
            )
            for i in request.FILES.getlist('images'):
                blog.images.add(BlogImages.objects.create(image=i))
            
            BulkSendNotification(request.user,User.objects.filter(role_id__in=[BUYER,SELLER],status=True,is_verified=True),'New Blog Posted',f'New Blog Posted by admin',NEW_BLOG_POSTED,blog.id)
            messages.success(request,'Blog Added Successfully')
            return redirect('blog:view_blog',id=blog.id)


class UpdateBlog(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        blog=Blogs.objects.get(id=self.kwargs['id'])
        return render(request, 'blog/edit-blog.html',{'head_title':'Blog Management','blog':blog})
    def post(self,request,*args,**kwargs):
        blog=Blogs.objects.get(id=self.kwargs['id'])
        if Blogs.objects.filter(title=request.POST.get('title')).exclude(id=blog.id):
            messages.error(request, 'Blog Already Exists')
        blog.title=request.POST.get('title')
        blog.description=request.POST.get('description')
        if request.FILES.getlist('images'):
            blog.images.clear()
            for i in request.FILES.getlist('images'):
                blog.images.add(BlogImages.objects.create(image=i))
        blog.save()
        messages.success(request,'Blog Updated Successfully.')
        return redirect('blog:view_blog',id=blog.id)


class ViewBlogDetails(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        blog=Blogs.objects.get(id=self.kwargs['id'])
        return render(request, 'blog/view-blog.html',{
            'head_title':'Blog Management',
            'blog':blog,
        })


class ChangeBlogStatus(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        blog=Blogs.objects.get(id=self.kwargs['id'])
        if request.GET.get('status'):
            if request.GET.get('status') == ACTIVE_BLOG:
                blog.status=ACTIVE_BLOG
                messages.success(request,"Blog activated successfully!")
            else:
                blog.status=INACTIVE_BLOG
                messages.success(request,"Blog deactivated successfully!")
            blog.save()
            return redirect('blogs:view_blog',id=blog.id)
        else:
            messages.error(request,"Something went wrong!")
            return redirect('blogs:view_blog',id=blog.id)


class DeleteBlog(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        Blogs.objects.get(id=self.kwargs['id']).delete()
        messages.success(request,"Blog Deleted Successfully!")   
        return redirect('blog:blog_list')


class ChangeBlogStatus(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        try:
            blog=Blogs.objects.get(id=self.kwargs['id'])
        except:
            message="Blog does not exists!"
        if blog.status == ACTIVE_BLOG:
            blog.status=INACTIVE_BLOG
            message="Blog deactivated successfully!"
        else:
            blog.status=ACTIVE_BLOG
            message="Blog Activated successfully!"
        blog.save()
        messages.success(request,message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
