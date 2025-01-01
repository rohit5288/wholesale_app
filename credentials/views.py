from accounts.utils import get_pagination
from .models import *
from accounts.common_imports import *
from django.http import HttpResponseRedirect


"""
SMTP keys Management
"""
class SMTPListView(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        smtp_settings = SMTPSetting.objects.all().order_by('-created_on').only('id')
        if request.GET.get('email_host'):
            smtp_settings = smtp_settings.filter(email_host__icontains=request.GET.get('email_host').strip())
        if request.GET.get('email_port'):
            smtp_settings = smtp_settings.filter(email_port__icontains=request.GET.get('email_port').strip())
        if request.GET.get('email_host_user'):
            smtp_settings = smtp_settings.filter(email_host_user__icontains=request.GET.get('email_host_user').strip())
        if request.GET.get('created_on'):
            smtp_settings = smtp_settings.filter(created_on__date=request.GET.get('created_on'))
        if request.GET.get('use_tls'):
            smtp_settings = smtp_settings.filter(use_tls=request.GET.get('use_tls'))
        if request.GET.get('is_active'):
            smtp_settings = smtp_settings.filter(is_active=request.GET.get('use_tls'))
        if request.GET and not smtp_settings:
            messages.error(request, 'No Data Found')
        return render(request, 'smtp_settings/smtp-list.html',{
            "smtp_settings":get_pagination(request,smtp_settings),
            "head_title":"SMTP Management",
            "email_host":request.GET.get('email_host',''),
            "email_port":request.GET.get('email_port',""),
            "use_tls":request.GET.get('use_tls',""),
            "email_host_user":request.GET.get('email_host_user',""),
            "email_host_password":request.GET.get('email_host_password',""),
            "created_on":request.GET.get('created_on',""),
        })


class ViewSMTP(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        smtp = SMTPSetting.objects.get(id=self.kwargs['id'])
        return render(request, 'smtp_settings/view-smtp.html',{"smtp":smtp,"head_title":"SMTP Management"})



class AddSMTPView(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        return render(request, 'smtp_settings/add-smtp.html',{"head_title":"SMTP Management"})

    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        if SMTPSetting.objects.filter(email_host=request.POST.get("email_host"), email_port=request.POST.get("email_port"), email_host_user=request.POST.get("email_host_user"), email_host_password=request.POST.get("email_host_password")):
            messages.error(request, 'SMTP keys already exists!')
            return render(request, 'smtp_settings/add-smtp.html',{'email_host':request.POST.get("email_host"), 'email_port':request.POST.get("email_port"), 'use_tls' : request.POST.get("tls"), 'email_host_user':request.POST.get("email_host_user"), 'email_host_password':request.POST.get("email_host_password"),"head_title":"Add SMTP Detail"})
        smtp_detail = SMTPSetting.objects.create(
            email_backend = "django.core.mail.backends.smtp.EmailBackend",
            email_host=request.POST.get("email_host"),
            email_port=request.POST.get("email_port"),
            email_host_user=request.POST.get("email_host_user"),
            email_host_password=request.POST.get("email_host_password"),
        )
        if request.POST.get("tls") == "1":
            smtp_detail.use_tls = True
        else:
            smtp_detail.use_tls = False
        smtp_detail.save()
        messages.error(request, 'Key added successfully!')
        return redirect('credentials:view_smtp',id=smtp_detail.id)



class EditSMTP(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        page = SMTPSetting.objects.get(id=self.kwargs['id'])
        return render(request, 'smtp_settings/edit-smtp.html',{"head_title":"SMTP Management",'email_host':page.email_host, 'email_port':page.email_port, 'use_tls' : page.use_tls, 'email_host_user':page.email_host_user, 'email_host_password':page.email_host_password, "page":page})


    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        page = SMTPSetting.objects.get(id=self.kwargs['id'])
        if request.POST.get("email_host"):
            page.email_host=request.POST.get("email_host")
        if request.POST.get("email_port"):
            page.email_port=request.POST.get("email_port")
        if request.POST.get("email_host_user"):
            page.email_host_user=request.POST.get("email_host_user")
        if request.POST.get("email_host_password"):
            page.email_host_password=request.POST.get("email_host_password")
        if request.POST.get("tls") == "1":
            page.use_tls = True
        else:
            page.use_tls = False
        page.save()
        messages.error(request, 'Key Updated Successfully!')
        return redirect('credentials:view_smtp',id=page.id)



class DeleteSMTP(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        SMTPSetting.objects.get(id=self.kwargs['id']).delete()
        messages.error(request, 'Key Deleted Successfully!')
        return redirect('credentials:smtp_list')


class ActivateDeActiveSMTP(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        page = SMTPSetting.objects.get(id=self.kwargs['id'])
        if page.is_active:
            page.is_active=False
            messages.error(request,'Key deactivated successfully!')
        else:
            SMTPSetting.objects.all().update(is_active = False)
            page.is_active = True   
            messages.error(request,'Key activated auccessfully!')
        page.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



'''
Firebase 
'''
class FirebaseCredentialsList(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        firebase_credentials = FirebaseCredentials.objects.all().order_by('-created_on').only('id')
        if request.GET.get('key'):
            firebase_credentials = firebase_credentials.filter(key__icontains=request.GET.get('key'))
        if request.GET.get('status'):
            firebase_credentials = firebase_credentials.filter(active=request.GET.get('status'))
        if request.GET.get('created_on'):
            firebase_credentials = firebase_credentials.filter(created_on__date=request.GET.get('created_on'))
        return render (request,'firebase/credentials-list.html',{
            'head_title':'Firebase Management',
            'firebase_credentials':get_pagination(request,firebase_credentials),
            'key':request.GET.get('key',''),
            'status':request.GET.get('status',''),
            'created_on':request.GET.get('created_on',''),
        })
    
class AddFirebaseCredentials(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        return render(request,'firebase/add-credentials.html',{
            'head_title':'Firebase Management',            
        })
    @method_decorator(admin_only)
    def post(self,request,*args,**kwargs):
        if FirebaseCredentials.objects.filter(key=request.POST.get('key')):
            messages.error(request,'Key already exists!')
            return redirect('credentials:firebase_credentials_list')
        else:
             FirebaseCredentials.objects.create(
                key = request.POST.get('key').strip(),
            )
             messages.success(request,'Credentials added successfully!')             
        return redirect('credentials:firebase_credentials_list')

class ViewFirebaseCredentials(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        firebase_credentials = FirebaseCredentials.objects.get(id=self.kwargs['id'])
        return render(request,'firebase/view-credentials.html',{
            'head_title':'Firebase Management',
            'firebase_credential':firebase_credentials, 
        })
    
class ActivateFirebaseStatus(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        
        firebase_credentials = FirebaseCredentials.objects.get(id=self.kwargs['id'])
        if firebase_credentials.active:
            firebase_credentials.active = False
            message = 'Deactivated Successfully!'
        else: 
            FirebaseCredentials.objects.all().update(active=False)
            firebase_credentials.active = True
            message = 'Activated Successfully!'
        firebase_credentials.save()
        messages.success(request,message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    
class UpdateFirebaseCredential(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        firebase_credentials = FirebaseCredentials.objects.get(id=self.kwargs['id'])
        return render(request,'firebase/edit-credentials.html',{
            'head_title':'Firebase Management',
            'firebase_credential':firebase_credentials,
        })
    @method_decorator(admin_only)
    def post(self,request,*args,**kwargs):
        firebase_credentials = FirebaseCredentials.objects.get(id=self.kwargs['id'])
        if FirebaseCredentials.objects.filter(key = request.POST.get('key').strip()).exclude(id=self.kwargs['id']):
            messages.error(request,'Key already exists!')
            return redirect('chat_gpt:view_firebase_credentials',id=self.kwargs['id'])
        if request.POST.get('key'):
            firebase_credentials.key = request.POST.get('key').strip()
        firebase_credentials.save()
        return redirect('credentials:view_firebase_credentials',id=self.kwargs['id'])
    
class DeleteFirebase(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        FirebaseCredentials.objects.get(id=self.kwargs['id']).delete()
        messages.success(request,'Firebase credentials deleted successfully!')
        return redirect('credentials:firebase_credentials_list')

class StripeListView(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        stripe_keys = StripeSetting.objects.all()
        if request.GET.get('test_secretkey'):
            stripe_keys = stripe_keys.filter(test_secretkey__icontains=request.GET.get('test_secretkey').strip())
        if request.GET.get('test_publishkey'):
            stripe_keys = stripe_keys.filter(test_publishkey__icontains=request.GET.get('test_publishkey').strip())
        if request.GET.get('is_active'):
            stripe_keys = stripe_keys.filter(is_active=request.GET.get('is_active'))
        if request.GET.get('created_on'):
            stripe_keys = stripe_keys.filter(created_on__date=request.GET.get('created_on'))
        if request.GET and not stripe_keys:
            messages.error(request, 'No Data Found')
        return render(request, 'stripe/stripe-list.html',{
            "stripe_keys":get_pagination(request,stripe_keys),
            "head_title":"Stripe Management",
            "test_secretkey":request.GET.get('test_secretkey',''),
            "test_publishkey":request.GET.get('test_publishkey',''),
            'is_active' : request.GET.get("is_active"),
            "created_on":request.GET.get('created_on',""),
        })


class EditStripeKey(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        stripe_key = StripeSetting.objects.get(id=self.kwargs.get('id'))
        return render(request, 'stripe/edit-stripe.html',{
            "test_secretkey": stripe_key.test_secretkey,
            "test_publishkey": stripe_key.test_publishkey,
            "head_title":"Stripe Management",
                "stripe_key":stripe_key
            })
    def post(self,request,*args,**kwargs):
        stripe_key = StripeSetting.objects.get(id=self.kwargs.get('id'))
        if request.POST.get("test_secretkey"):
            stripe_key.test_secretkey=request.POST.get("test_secretkey")
        if request.POST.get("test_publishkey"):
            stripe_key.test_publishkey=request.POST.get("test_publishkey")

        stripe_key.save()
        messages.error(request, 'Firebase Key Updated Successfully!')
        return redirect('credentials:view_stripe',id=stripe_key.id)


class AddStripeKeyView(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        return render(request, 'stripe/add-stripe.html',{"head_title":"Stripe Management"})
    def post(self,request,*args,**kwargs):
        if StripeSetting.objects.filter(test_secretkey=request.POST.get("test_secretkey"),test_publishkey=request.POST.get('test_publishkey')):
            messages.error(request, 'Stripe Key Already Exists!')
        StripeSetting.objects.create(
            test_secretkey = request.POST.get('test_secretkey'),
            test_publishkey = request.POST.get('test_publishkey'),
        )
        messages.error(request, 'Stripe Key Added Successfully!')
        return redirect('credentials:stripe_list')


class DeleteStripeKey(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        StripeSetting.objects.get(id=self.kwargs.get('id')).delete()
        messages.error(request, 'Stripe Key Deleted Successfully!')
        return redirect('credentials:stripe_list')


class ViewStripeKey(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        stripe_key = StripeSetting.objects.get(id=self.kwargs.get('id'))
        return render(request, 'stripe/view-stripe.html',{"stripe_key":stripe_key,"head_title":"Stripe Management"})


class ActivateDeActiveStripeKey(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):    
        stripe_key = StripeSetting.objects.get(id=self.kwargs.get('id'))
        if stripe_key.is_active:
            stripe_key.is_active=False
            messages.error(request,'Stripe Key Deactivated Successfully!')
        else:
            StripeSetting.objects.all().update(is_active=False)
            stripe_key.is_active = True   
            messages.error(request,'Stripe Key Activated Successfully!')
        stripe_key.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))