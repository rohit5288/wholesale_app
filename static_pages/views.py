from accounts.utils import get_pagination
from .models import *
from accounts.common_imports import *
from django.http import HttpResponseRedirect

"""
Page Management
"""
class PagesListView(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        pages = Pages.objects.all().order_by('-created_on').only('id')
        if request.GET.get('id'):
            pages = pages.filter(id=request.GET.get('id'))
        if request.GET.get('state'):
            pages = pages.filter(is_active = request.GET.get('state'))
        if request.GET.get('title'):
            pages = pages.filter(title__icontains=request.GET.get('title').strip())
        if request.GET.get('content'):
            pages = pages.filter(content__icontains=request.GET.get('content').strip())
        if request.GET.get('type_id'):
            pages = pages.filter(type_id=request.GET.get('type_id'))
        if request.GET.get('created_on'):
            pages = pages.filter(created_on__date=request.GET.get('created_on'))
        if request.GET and not pages:
            messages.error(request, 'No Data Found')
        return render(request, 'StaticPages/pages-list.html',{
            "pages":get_pagination(request,pages),
            "head_title":"Pages Management",
            "id":request.GET.get('id',''),
            "title":request.GET.get('title',''),
            "content":request.GET.get('content',''),
            "type_id":request.GET.get('type_id',''),
            "created_on":request.GET.get('created_on',''),
            "state": request.GET.get('state',''),
        })
    

class ViewPage(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        page = Pages.objects.get(id=self.kwargs['id'])
        return render(request, 'StaticPages/view-page.html',{"page":page,"head_title":"Pages Management"})




class AddPageView(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        return render(request, 'StaticPages/add-page.html',{"head_title":"Pages Management"})

    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        if Pages.objects.filter(type_id = request.POST.get("type_id")):
            messages.error(request, 'Page already exists!')
            return render(request, 'StaticPages/add-page.html',{"title":request.POST.get("title"),"content":request.POST.get("content"),"type_id":request.POST.get("type_id"),"head_title":"Pages"})
        page = Pages.objects.create(
            title=request.POST.get("title"),
            type_id=request.POST.get("type_id"),
            content=request.POST.get("content")
        )
        messages.error(request, 'Page added successfully!')
        return redirect('static_pages:view_page',id=page.id)



class EditPage(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        page = Pages.objects.get(id=self.kwargs['id'])
        return render(request, 'StaticPages/edit-page.html',{"head_title":"Pages Management","page":page})

    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        page = Pages.objects.get(id=self.kwargs['id'])
        if request.POST.get("title"):
            page.title = request.POST.get("title")
        if request.POST.get("content"):
            page.content = request.POST.get("content")
        page.save()
        messages.error(request, 'Page updated successfully!')
        return redirect('static_pages:view_page',id=page.id)



class DeletePage(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        Pages.objects.get(id=self.kwargs['id']).delete()
        messages.error(request, 'Page deleted successfully!')
        return redirect('static_pages:pages_list')


class ChangePageStatus(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        page = Pages.objects.get(id=self.kwargs['id'])
        if page.is_active:
            page.is_active = False
            message = "page Deactivated Successfully!"
        else:
            if Banners.objects.filter(is_active=True).count() >= MAX_ACTIVE_BANNER:
                messages.success(request,f'Sorry ,Maximum {MAX_ACTIVE_BANNER} banner could be activated at same time!')
                return redirect('accounts:banners_list')
            page.is_active = True
            message = "Page Activated Successfully!"
        page.save()
        messages.success(request,message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


"""
Faq Management
"""

class FaqsList(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        faqs = FAQs.objects.all().order_by('-created_on').only('id')
        if request.GET.get('question'):
            faqs = faqs.filter(question__icontains=request.GET.get('question'))
        if request.GET.get('answer'):
            faqs = faqs.filter(answer__icontains = request.GET.get('answer'))
        if request.GET.get('created_on'):
            faqs = faqs.filter(created_on__date = request.GET.get('created_on'))
        if request.GET and not faqs:
            messages.error(request, 'No Data Found')
        return render(request,'faq/faq-list.html',{
            'faqs':get_pagination(request,faqs),
            'head_title':'FAQs Management',
            'question':request.GET.get('question',''),
            'answer':request.GET.get('answer',''),
            'created_on':request.GET.get('created_on','') 
        })
    

class ViewFAQ(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        faq = FAQs.objects.get(id=self.kwargs['id'])
        return render(request,'faq/view-faq.html',{'head_title':'FAQs Management','faq':faq})


class AddFAQ(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        return render(request, 'faq/add-faq.html',{"head_title":"FAQs Management"})

    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        if FAQs.objects.filter(question=request.POST.get('question')):
            messages.error(request,'FAQ Already Exists!')
            return render(request, 'faq/add-faq.html',{"question":request.POST.get("question"),"answer":request.POST.get("answer"),"head_title":"FAQs Management"})
        faq = FAQs.objects.create(
            question = request.POST.get('question'),
            answer = request.POST.get('answer')
        )
        messages.error(request, 'Faq added successfully!')
        return redirect('static_pages:view_faq',id=faq.id)


class UpdateFAQ(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        faq = FAQs.objects.get(id=self.kwargs['id'])
        return render(request, 'faq/edit-faq.html',{"head_title":"FAQs Management","faq":faq})

    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        faq = FAQs.objects.get(id=self.kwargs['id'])
        if request.POST.get('question'):
            faq.question=request.POST.get('question')
        if request.POST.get('answer'):
            faq.answer = request.POST.get('answer')
        faq.save()
        messages.error(request, 'FAQ updated successfully!')
        return redirect('static_pages:view_faq',id=faq.id)



class DeleteFAQ(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        FAQs.objects.get(id=self.kwargs['id']).delete()
        messages.success(request,'FAQ Deleted Successfully')
        return redirect('static_pages:faq_list')
    

class DeleteAllFAQ(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        if FAQs.objects.all():
            FAQs.objects.all().delete()
            messages.success(request,'FAQ deleted successfully')
            return redirect('static_pages:faq_list')
        messages.success(request,'Sorry no data available to delete')
        return redirect('static_pages:faq_list')
