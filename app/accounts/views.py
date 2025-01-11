
import re
from accounts.utils import *
from accounts.common_imports import *
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from cron_descriptor import get_description
import subprocess
from django.contrib.sites.models import Site

db_logger = logging.getLogger('db')
env = environ.Env()
environ.Env.read_env()


class AdminLoginView(TemplateView):
    def get(self, request, *args, **kwargs):
        return redirect('accounts:login')


class LogOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect('accounts:login')


class LoginView(View):
    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('frontend:index')
        return render(request,'registration/login.html')

    def post(self,request,*args,**kwargs):
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()
        if not username:
            return render(request, 'registration/login.html',{"username":username,"password":password})
        if not password:
            return render(request, 'registration/login.html',{"username":username,"password":password})
        if request.POST.get('remember_me')=='on':    
           request.session.set_expiry(1209600) 
        try:
            user = authenticate(username=username, password=password)
        except Exception as e:
            user = None
        if not user:
            CreateLoginHistory(request,username,None,LOGIN_FAILURE,None)
            messages.error(request, 'Invalid login details.')
            return render(request, 'registration/login.html',{"username":username,"password":password})
        if user.is_superuser and user.role_id == ADMIN:
            login(request, user)
            CreateLoginHistory(request,username,None,LOGIN_SUCCESS,None)
            messages.success(request, "Login Successfully!")
            return redirect('admin:index')
        elif not user.is_superuser and not user.role_id == ADMIN:
            messages.error(request,"You are not allowed to login on this portal")
            return render(request, 'registration/login.html')
        else:
            messages.error(request, 'Invalid login details.')
            return render(request, 'registration/login.html',{"username":username,"password":password})


class PasswordChange(View):
    @method_decorator(login_required)
    def get(self,request,*args,**kwargs):
        return render(request,'admin/change-password.html',{"head_title":"Change Password"})

    def post(self,request,*args,**kwargs):
        user = User.objects.get(id=request.user.id)
        if not user.check_password(request.POST.get('current_password')):
            messages.error(request, 'Current Password does not match')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if request.POST.get('current_password') == request.POST.get("password"):
            messages.error(request, 'New password must be different from the current password!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        user.set_password(request.POST.get("password"))
        user.save()
        messages.add_message(request, messages.INFO, 'Password changed successfully')
        return redirect('users:view_user',id=user.id)


 
def Validations(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data ={"valid":None,"email":False, "username":False,"mobile_no":False}
        if request.GET.get('email'):
            match = str(re.search(r'^[a-zA-Z0-9_.+-]+[@]\w+[.]\w{2,3}$',request.GET.get("email").strip()))    
            if match != "None":
                data['valid'] = '1'
            else:
                data['valid'] = '0'
        if request.GET.get('id'):
            user = User.objects.get(id=request.GET.get('id'))
            if request.GET.get('email'):
                data['email'] = User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE)|Q(status=DELETED),email=request.GET.get('email')).exclude(id=user.id).exists()
            if request.GET.get('username'):
                data['username'] = User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE|Q(status=DELETED)),username=request.GET.get('username')).exclude(id=user.id).exists()
            if request.GET.get('mobile_no') :
                data['mobile_no'] = User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE)|Q(status=DELETED),mobile_no=request.GET.get('mobile_no')).exclude(id=user.id).exists()
        else:
            if request.GET.get('email'):
                data['email'] = User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE|Q(status=DELETED)),email=request.GET.get('email')).exists()
            if request.GET.get('username'):
                data['username'] = User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE|Q(status=DELETED)),username=request.GET.get('username')).exists()
            if request.GET.get('mobile_no') :
                data['mobile_no'] = User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE|Q(status=DELETED)),mobile_no=request.GET.get('mobile_no')).exists()
        return JsonResponse(data)


"""
Password Management
"""

class ResetPassword(View):
    def get(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(key=self.kwargs.get('token'))
            user = User.objects.get(id=token.user_id)
            return render(request,'registration/ResetPassword.html',{"token":token})
        except:
            messages.error(request, 'Sorry! Your link has been expired. Please generate a new link to proceed further.')
            return redirect('accounts:login')

    def post(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(key=self.kwargs.get('token'))
            user = User.objects.get(id=token.user_id)
            user.password = make_password(request.POST.get("password"))
            user.save()
            token.delete()
            messages.success(request,'Password reset successfully!')
            return redirect('accounts:login')
        except:
            messages.error(request, 'Sorry! Your link has been expired. Please generate a new link to proceed further.')
            return redirect('accounts:login')
    


class ForgotPasswordEmail(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'registration/forgot-email.html')

    def post(self, request, *args, **kwargs):
        if not User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),email=request.POST.get("email")).exists():
            messages.success(request,'Please enter a registered email address.')
            return redirect('accounts:forgot_password_email')
        else:
            user = User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),email=request.POST.get("email")).last()
            try:
                token = Token.objects.get(user=user)
            except:
                token = Token.objects.create(user=user)  
            BulkSendUserEmail(request,user,'EmailTemplates/reset_password_admin.html','Reset Password',request.POST.get("email"),token,"","","")
            messages.success(request,'A link has been sent on your email to reset your password.')
            return redirect('accounts:login')
    


"""
Verify Account through email 
"""
class VerifyUserAccount(View):
    def get(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(key = self.kwargs.get('token'))
            user = User.objects.get(id=token.user_id)
            user.email_verified = True
            user.save()
            token.delete()
            return render(request,'EmailTemplates/verification-success.html',{"user":user,'protocol': 'https' if USE_HTTPS else 'http','domain':env('SITE_DOMAIN')})
        except:
            return render(request,'EmailTemplates/verification-fail.html',{'protocol': 'https' if USE_HTTPS else 'http','domain':env('SITE_DOMAIN')})

    

"""
Notification Management
"""
class NotificationsList(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs.get('id'))
        notifications = Notifications.objects.filter(created_for=user).order_by('-created_on')
        return render(request, "admin/notifications.html",{
            "head_title": "Notifications Management",
            "notifications": get_pagination(request, notifications),
            "user":user
        })



class DeleteNotifications(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        notifications = Notifications.objects.filter(created_for__role_id=ADMIN)
        if notifications:
            notifications.delete()
            messages.success(request, 'Notifications deleted successfully!')
        else:
            messages.error(request, "No notifications to delete!")
        return redirect('accounts:notifications_list',request.user.id)
        

class MarkReadNotifications(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs.get('id'))
        notifications = Notifications.objects.filter(created_for=user).order_by('-created_on')
        if notifications:
            notifications.update(is_read=True)
            messages.success(request, 'All notifications marked as read successfully!')
        else:
            messages.error(request, "No Notifications to Read!")
        return redirect('accounts:notifications_list',id=user.id)



'''
CronJob Management
'''


class ListCronjob(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        cron1,id,name,time,days=[],[],[],[],[]
        try:
            crons=subprocess.run(['python3','manage.py','crontab','show'],stdout=subprocess.PIPE)
            if crons:
                crons=crons.stdout.decode().split(':')[1].replace('->',',').replace('.',' ').replace("'","").replace("\"","").replace('(','').replace(')','').strip().split('\n')
                for x in crons:
                    cron1.append(x.split(','))
                for x in cron1:
                    if len(x)==3:
                        id.append(x[0].strip())
                        time.append(x[1].strip())
                        name.append(x[2].strip())
                cron1.clear()
                for x in name:
                    cron_name = x.split(' ')[::-1][0]
                    cron1.append(cron_name)
                for x in time:
                    cron=get_description(x)
                    days.append(cron)
                crontabs=list(zip(id,cron1,days,time))
        except subprocess.CalledProcessError as e:
            crons=f'Command {e.cmd} failed with error {e.returncode}'    
        return render(request,'admin/cronjobs.html',{'head_title':'Cronjob Management','crontab':crontabs})
        

class AddCronjob(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        os.system('python3 manage.py crontab remove')
        os.system('python3 manage.py crontab add')
        messages.success(request,'Cronjobs added successfully')
        return redirect('accounts:list_cronjob')
    

class RemoveCronjob(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        os.system('python3 manage.py crontab remove')
        messages.success(request,'Cronjobs removed successfully')
        return redirect('accounts:list_cronjob')

class RunCronjob(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        os.system(f"python3 manage.py crontab run {self.kwargs.get('id')}")
        messages.success(request,'Cronjob ran Successfully!')
        return redirect('accounts:list_cronjob')



"""
Login History Management
"""

class LoginHistoryView(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        loginhistory = LoginHistory.objects.all().order_by('-created_on')
        if request.GET.get('email'):
            loginhistory = loginhistory.filter(user_email__icontains = request.GET.get('email'))
        if request.GET.get('user_ip'):
            loginhistory = loginhistory.filter(user_ip__icontains = request.GET.get('user_ip'))
        if request.GET.get('agent'):
            loginhistory = loginhistory.filter(user_agent__icontains = request.GET.get('agent'))
        if request.GET.get('status'):
            loginhistory = loginhistory.filter(status = request.GET.get('status'))
        if request.GET.get('url'):
            loginhistory = loginhistory.filter(url__icontains = request.GET.get('url'))
        if request.GET.get('created_on'):
            loginhistory = loginhistory.filter(created_on__date = request.GET.get('created_on'))
        return render(request, 'admin/login-history.html', {
            "head_title":"Login History Management",
            "loginhistory":get_pagination(request,loginhistory),
            "email":request.GET.get('email',""), 
            "user_ip":request.GET.get('user_ip',""), 
            "agent":request.GET.get('agent',""), 
            "status":request.GET.get('status',""), 
            "url":request.GET.get('url',""), 
            "created_on":request.GET.get('created_on',"")
        })


class DeleteHistory(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        loginhistory = LoginHistory.objects.all()
        if loginhistory:
            loginhistory.delete()
            messages.success(request,"All login history cleared sucessfully!!!")
        else:
            messages.error(request,"Nothing to delete!")
        return redirect('accounts:login_history')

class SendBulkNotification(View):
    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        super_admin=User.objects.filter(is_superuser=True,role_id=ADMIN).first()
        users=User.objects.all()
        messages.success(request,"Successfully notified all users with your message.")
        BulkSendNotification(
                    created_by= super_admin,
                    created_for=[user for user in users],
                    title=f'Admin Message',
                    description=request.POST.get('message').strip(),
                    notification_type=ADMIN_NOTIFICATION,
                    obj_id= "",
                )
        return redirect('users:view_user', id=super_admin.id)



class BannersList(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        banners = Banners.objects.filter(created_by=request.user).order_by('-updated_on').only('id')
        if request.GET.get('title'):
            banners = banners.filter(title__icontains = request.GET.get('title').strip())
        if request.GET.get('state'):
            banners = banners.filter(is_active = request.GET.get('state'))
        if request.GET.get('created_on'):
            banners = banners.filter(created_on__date = request.GET.get('created_on'))
        if request.GET.get('updated_on'):
            banners = banners.filter(updated_on__date = request.GET.get('updated_on'))
        if request.GET and not banners:
            messages.error(request, 'No Data Found')
        return render(request, 'banners/banner-list.html',{
            "banners":get_pagination(request, banners),
            "head_title":"Banners Management",
            "title": request.GET.get('title','') ,
            "created_on": request.GET.get('created_on','') ,
            "updated_on": request.GET.get('updated_on','') ,
            "state": request.GET.get('state',''),
        })
    

class ChangeBannerStatus(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        banner = Banners.objects.get(id=self.kwargs['id'])
        if banner.is_active:
            banner.is_active = False
            message = "Banner Deactivated Successfully!"
        else:
            if Banners.objects.filter(is_active=True).count() >= MAX_ACTIVE_BANNER:
                messages.success(request,f'Sorry ,Maximum {MAX_ACTIVE_BANNER} banner could be activated at same time!')
                return redirect('accounts:banners_list')
            banner.is_active = True
            message = "Banner Activated Successfully!"
        banner.save()
        messages.success(request,message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    

class DeleteBanner(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        Banners.objects.get(id=self.kwargs['id']).delete()
        messages.success(request,'Banner Deleted Successfully!')
        return redirect('accounts:banners_list')


class AddBanner(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        return render(request,'banners/add-banner.html',{
            "head_title":"Banners Management",
        })
    @method_decorator(admin_only)
    def post(self, request,*args,**kwargs):
        Banners.objects.create(
            title = request.POST.get('title'),
            image = request.FILES.get('image',None),
            created_by = request.user,
            is_active = False if Banners.objects.filter(is_active=True).count() >= MAX_ACTIVE_BANNER else True,
        )
        messages.success(request, 'Banner Added Successfully!')
        return redirect('accounts:banners_list')

class ViewBanner(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        banner=Banners.objects.get(id=self.kwargs['id'])
        return render(request,'banners/view-banner.html',{
            "head_title":"Banners Management",
            "banner":banner
        })

class UpdateBanner(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        banner=Banners.objects.get(id=self.kwargs['id'])
        return render(request,'banners/edit-banner.html',{
            "head_title":"Banners Management",
            "banner":banner
        })

    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        banner = Banners.objects.get(id=self.kwargs['id'])
        if request.POST.get("title"):
            banner.title=request.POST.get("title")
        if request.FILES.get('image'):
            banner.image=request.FILES.get('image')
        banner.save()
        messages.error(request, 'Banner Updated Successfully!')
        return redirect('accounts:banners_list')



class Logo(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        logos=ProjectLogo.objects.all().order_by('-created_on')
        return render(request,'logo/logos.html',{
            "head_title":"Logo Management",
            "logos":logos
        })

class AddLogo(View):
    def get(self, request, *args, **kwargs):
        return render(request,'logo/add-logo.html',{
            "head_title":"Logo Management"
        })
    def post(self, request, *args, **kwargs):
        super_admin=User.objects.filter(is_superuser=True,role_id=ADMIN).first()
        ProjectLogo.objects.get_or_create(
            logo = request.FILES.get('lg_logo'),
            favicon = request.FILES.get('favicon'),
            created_by=request.user
            )
        messages.success(request,"logo updated successfully")
        return redirect('accounts:logo')

class EditLogo(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        logo = ProjectLogo.objects.get(id=self.kwargs['id'])
        return render(request, 'logo/edit-logo.html',{"head_title":"Logo Management",'logo':logo})

    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        logo = ProjectLogo.objects.get(id=self.kwargs['id'])
        if request.FILES.get("lg_logo"):
            logo.logo=request.FILES.get("lg_logo")
        if request.FILES.get("favicon"):
            logo.favicon=request.FILES.get("favicon")
        logo.save()
        messages.error(request, 'logo Updated Successfully!')
        return redirect('accounts:logo')


class DeleteLogo(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        ProjectLogo.objects.get(id=self.kwargs['id']).delete()
        messages.error(request, 'logo Deleted Successfully!')
        return redirect('accounts:logo')

class UpdateDjangoSite(View):
    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        site = Site.objects.first()
        site.domain = request.POST.get('domain')
        site.name = request.POST.get('domain')
        site.save()
        messages.success(request,'Site information updated successfully!')
        return redirect('users:view_user',id=request.user.id)
    
"""
User Activity Logs Management
"""

class UserActivityLogs(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        user=User.objects.get(id=self.kwargs.get('id'))
        activities = Activities.objects.filter(user=user).order_by('-created_on')
        return render(request, 'admin/user-activity.html', {
            "head_title":"Users Management",
            "user":user,
            "activities":get_pagination(request,activities,required_page_size=10),
        })
