from accounts.common_imports import *
from static_pages.models import *
db_logger = logging.getLogger('db')
 

class index(View):
    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            user = request.user
            if user.is_superuser and user.role_id == ADMIN:
                return redirect('admin:index')
            else:
                return redirect('accounts:login')
        else:
            return render(request, "frontend/index.html", {"showclass":True})


def handler404(request, exception, template_name="frontend/404.html"):
    db_logger.exception(exception)
    return render(request, template_name, status=404)
    

def handler500(request, *args, **kwargs):
    db_logger.exception(Exception)
    return render(request, 'frontend/404.html', status=500)
    

def handler403(request, exception, template_name="frontend/404.html"):
    db_logger.exception(exception)
    return render(request, template_name, status=403)
    

def handler400(request, exception, template_name="frontend/404.html"):
    db_logger.exception(exception)
    return render(request, template_name, status=400)


class AboutUsview(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('frontend:index')
        about_us = Pages.objects.filter(type_id=ABOUT_US).first()
        return render(request, "frontend/aboutus.html",{"data":about_us, "page_title":"About Us"})


class TermsAndConditionsView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('frontend:index')
        terms = Pages.objects.filter(type_id=TERMS_AND_CONDITION).first()
        return render(request, "frontend/terms_condition.html",{"data":terms, "page_title":"Terms and Condition"})


class PrivacyPolicy(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('frontend:index')
        privacy_policy = Pages.objects.filter(type_id=PRIVACY_POLICY).first()
    
        return render(request, "frontend/privacy_policy.html",{"data":privacy_policy, "page_title":"Privacy Policy"})



