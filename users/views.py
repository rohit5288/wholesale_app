from accounts.common_imports import *
from django.contrib.auth.hashers import make_password
from django.contrib.sites.models import Site

class EditAdmin(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs['id'])
        if not user.role_id == ADMIN:
            messages.error(request,"Sorry! You have no permissions to do this task.")
            return redirect("frontend:index")
        return render(request, 'admin/edit-admin.html',{"head_title":"Admin Profile","user":user})

    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs['id'])
        email_users = User.objects.filter(Q(status = ACTIVE)|Q(status = INACTIVE), email = request.POST.get("email")).exclude(id=self.kwargs['id'])
        username_users = User.objects.filter(Q(status = ACTIVE)|Q(status = INACTIVE), username = request.POST.get("username")).exclude(id=self.kwargs['id'])
        if username_users:
            messages.success(request,"Username already exists")
            return render(request, 'admin/edit-admin.html',{"head_title":"Admin Profile","user":user}) 
        if email_users:
            messages.success(request,"Email already exists")
            return render(request, 'admin/edit-admin.html',{"head_title":"Admin Profile","user":user}) 
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        if request.FILES.get('profile_pic'):
            user.profile_pic = request.FILES.get('profile_pic')
        user.save()
        messages.success(request,"Profile updated successfully!")
        return redirect('users:view_user',id=user.id)

class ViewUser(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs['id'])
        activity = Activities.objects.filter(user=user).order_by('-created_on').only('id')
        login_history = LoginHistory.objects.filter(Q(user_email=user.email)|Q(mobile_no=user.mobile_no)).order_by('-created_on').only('id')
        if user.role_id == ADMIN:
            if not request.user.role_id == ADMIN:
                return render(request, 'frontend/restrict.html')
            site=Site.objects.first()
            return render(request, 'admin/admin-profile.html', {"user":user,"site":site,"head_title":"Admin Profile"})
        elif user.role_id == BUYER:
            device = Device.objects.filter(user=user).last()
            activities=Activities.objects.filter(user=user).count()
            return render(request, 'users/user-profile.html', {
                "head_title":"Buyer Profile",
                "isBuyer":True,
                "user":user,
                "device":device,
                "token":Token.objects.filter(user=user).last(),
                "activity":activity,
                'loginhistory':get_pagination1(request,login_history,3),
                "activities":activities
            })
        elif user.role_id == SELLER:
            device = Device.objects.filter(user=user).last()
            activities=Activities.objects.filter(user=user).count()
            return render(request, 'users/sellers/seller-profile.html', {
                "user":user,
                "activity":activity,
                "head_title":"Seller Profile",
                "isBuyer":True,
                "token":Token.objects.filter(user=user).last(),
                "device":device,
                'loginhistory':get_pagination1(request,login_history,3),
                "activities":activities

            })
        
class InactivateUser(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs['id'])
        Activities.objects.create(user=user,title='User Inactivated',description='User has been deactivated')
        if request.user == user:
            return render(request, 'frontend/restrict.html')
        user.status = INACTIVE
        user.save()
        Token.objects.filter(user=user).delete()
        messages.success(request,'Account deactivated successfully!')
        BulkSendUserEmail(request,user,'EmailTemplates/AccountStatus.html','Account Deactivated',user.email,"","Your account has been deactivated. Please contact admin to activate your account.",'Account Deactivated',"")
        return redirect('users:view_user',id=user.id)

class DeleteUser(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs['id'])
        Activities.objects.create(user=user,title='User Deleted',description='User has been deleted')
        if request.user == user:
            return render(request, 'frontend/restrict.html')
        user.status = DELETED
        # Token.objects.filter(user=user).delete()
        # if user:
        #     try:
        #         user.username = user.username + str(user.id)
        #     except:
        #         user.username = str(user.id)
        #     user.email = user.email+ str(user.id)
        # user.save()
        messages.success(request,'Account deleted successfully!')
        BulkSendUserEmail(request,user,'EmailTemplates/AccountStatus.html','Account Deleted',user.email,"","Your account has been deleted. Please contact admin to activate your account.",'Account Deleted',"")
        return redirect('users:view_user',id=user.id)
        
class ActivateUser(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs['id'])
        Activities.objects.create(user=user,title='User Activated',description='User has been activated')
        if request.user == user:
            return render(request, 'frontend/restrict.html')
        user.status = ACTIVE
        user.save()
        messages.success(request,'Account activated successfully!')
        BulkSendUserEmail(request,user,'EmailTemplates/AccountStatus.html','Account Activated',user.email,"","Your account has been activated.",'Account Activated',"")
        return redirect('users:view_user',id=user.id)

class BuyersList(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        users = User.objects.filter(role_id=BUYER).order_by('-created_on').only('id')
        if request.GET.get('username'):
            users = users.filter(username__icontains = request.GET.get('username').strip())
        if request.GET.get('full_name'):
            users = users.filter(full_name__icontains = request.GET.get('full_name').strip())
        if request.GET.get('email'):
            users = users.filter(email__icontains = request.GET.get('email').strip())
        if request.GET.get('mobile_no'):
            users = users.filter(id__in=[i.id for i in users if request.GET.get('mobile_no').strip() in str(i.country_code)+str(i.mobile_no)])
        if request.GET.get('created_on_from'):
            users = users.filter(created_on__date__gte = request.GET.get('created_on_from'))
        if request.GET.get('created_on_to'):
            users = users.filter(created_on__date__lte = request.GET.get('created_on_to'))
        if request.GET.get('status'):
            users = users.filter(status=request.GET.get('status'))            
        if request.GET and not users:
            messages.error(request, 'No Data Found')
        return render(request,'users/users-list.html',{
            "head_title":'Buyers Management',
            "users" : get_pagination(request, users),
            "full_name":request.GET.get('full_name',''),
            "username":request.GET.get('username',''),
            "email":request.GET.get('email',''),
            "mobile_no":request.GET.get('mobile_no',''),
            "created_on_from":request.GET.get('created_on_from',''),
            "created_on_to":request.GET.get('created_on_to',''),
            "status":request.GET.get('status',''),
            "scroll_required":True if request.GET else False,
        })


class AddUser(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        return render(request,'users/add-user.html',{'head_title':"Buyer Profile",'GOOGLE_PLACES_KEY': env('GOOGLE_PLACES_KEY')})

    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        if User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),email=request.POST.get("email"), role_id__in=BUYER):
            messages.error(request,'User already exists with this email id.')
        if User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),mobile_no=request.POST.get("mobile_no"), role_id__in=BUYER):
            messages.error(request,'User already exists with this mobile no')

        user=User.objects.create(
            full_name = request.POST.get('full_name'),
            email = request.POST.get('email'),
            address = request.POST.get('address'),
            role_id = BUYER,
            gender = request.POST.get('gender'),
            latitude = request.POST.get('latitude',None),
            longitude = request.POST.get('longitude',None),
            mobile_no = request.POST.get('mobile_no'),
            profile_pic = request.FILES.get('profile_pic'),
            password = make_password(request.POST.get('password'))
        )
        Activities.objects.create(user=user,title='User Created',description='User has been created')
        messages.success(request,'User created successfully !')
        BulkSendUserEmail(request,user,"EmailTemplates/login-crenditials.html",'Login credentials',user.email,request.POST.get("password"),'','','')
        return redirect('users:customers_list')
    
class EditUser(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs['id'])
        Activities.objects.create(user=user,title='User Updated',description='User has been updated')
        return render(request, 'users/edit-user.html',{"head_title":"Buyer Profile","user":user,'GOOGLE_PLACES_KEY': env('GOOGLE_PLACES_KEY')})

    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs['id'])
        if User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),email=request.POST.get("email"), role_id__in=BUYER).exclude(id=user.id):
            messages.error(request,'User already exists with this email id.')
        if User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),mobile_no=request.POST.get("mobile_no"), role_id__in=BUYER).exclude(id=user.id):
            messages.error(request,'User already exists with this mobile no')
        if request.POST.get('full_name'):
            user.full_name = request.POST.get('full_name')
        if request.POST.get('gender'):
            user.gender = request.POST.get('gender')
        if request.POST.get('email'):
            user.email = request.POST.get('email')
        if request.POST.get('mobile_no'):
            user.mobile_no = request.POST.get('mobile_no')
        if request.POST.get('zipcode'):
            user.zipcode = request.POST.get('zipcode')
        if request.POST.get('address'):
            user.address = request.POST.get('address')
            user.latitude = request.POST.get('latitude') if request.POST.get('latitude') else None
            user.longitude = request.POST.get('longitude') if  request.POST.get('longitude') else None
        if request.FILES.get('profile_pic'):
            user.profile_pic = request.FILES.get('profile_pic')
        user.save()
        messages.success(request,'Profile updated successfully.')
        return redirect('users:view_user',id=user.id)
