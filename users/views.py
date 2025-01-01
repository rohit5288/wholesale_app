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
            followed_users = user.following.all().order_by('-created_on')
            categories = user.categories.all().order_by('-created_on')
            favourite_events=user.favourite_events.all().order_by('-created_on')
            activities=Activities.objects.filter(user=user).count()
            return render(request, 'users/user-profile.html', {
                "head_title":"Buyer Profile",
                "isBuyer":True,
                "user":user,
                "device":device,
                "token":Token.objects.filter(user=user).last(),
                "activity":activity,
                'loginhistory':get_pagination1(request,login_history,1),
                "followed_users":get_pagination1(request,followed_users,2),
                "categories":get_pagination1(request,categories,3),
                "favourite_events":get_pagination1(request,favourite_events,4),
                "activities":activities
            })
        elif user.role_id == SELLER:
            device = Device.objects.filter(user=user).last()
            active_events = Events.objects.filter(created_by=user,start_datetime__gt=datetime.now()).order_by('-created_on').only('id')
            past_events = Events.objects.filter(created_by=user,end_datetime__lt=datetime.now()).order_by('-created_on').only('id')
            subscriptions_purchased = UserPlanPurchased.objects.filter(purchased_by=user).order_by('-created_on').only('id')
            activities=Activities.objects.filter(user=user).count()
            if request.GET.get('title'):
                active_events=active_events.filter(title__icontains=request.GET.get('title'))
            if request.GET.get('category'):
                active_events=active_events.filter(category__title__icontains=request.GET.get('category'))
            if request.GET.get('event_type'):
                active_events=active_events.filter(event_type=request.GET.get('event_type'))
            if request.GET.get('status'):
                active_events=active_events.filter(status=request.GET.get('status'))
            if request.GET.get('date'):
                active_events=active_events.filter(start_datetime__date=request.GET.get('date'))
            if request.GET.get('created_on'):
                active_events=active_events.filter(created_on__date=request.GET.get('created_on'))
            if request.GET.get('p_title'):
                past_events=past_events.filter(title__icontains=request.GET.get('p_title'))
            if request.GET.get('p_category'):
                past_events=past_events.filter(category__title__icontains=request.GET.get('p_category'))
            if request.GET.get('p_event_type'):
                past_events=past_events.filter(event_type=request.GET.get('p_event_type'))
            if request.GET.get('p_status'):
                past_events=past_events.filter(status=request.GET.get('p_status'))
            if request.GET.get('p_date'):
                past_events=past_events.filter(start_datetime__date=request.GET.get('p_date'))
            if request.GET.get('p_created_on'):
                past_events=past_events.filter(created_on__date=request.GET.get('p_created_on'))
            if not active_events and not past_events and request.GET:
                messages.success(request,"Events Not Found!")
            return render(request, 'users/sellers/seller-profile.html', {
                "user":user,
                "activity":activity,
                "head_title":"Seller Profile",
                "isBuyer":True,
                "token":Token.objects.filter(user=user).last(),
                "device":device,
                "active_events":get_pagination1(request,active_events,1),
                "past_events":get_pagination1(request,past_events,2),
                'loginhistory':get_pagination1(request,login_history,3),
                'subscriptions_purchased':get_pagination1(request,subscriptions_purchased,4),
                "title":request.GET.get('title') if request.GET.get('title') else ''  ,
                "event_type":request.GET.get('event_type') if request.GET.get('event_type') else '' ,
                "date":request.GET.get('date') if request.GET.get('date') else '' ,
                "category":request.GET.get('category',"") if request.GET.get('category') else '' ,
                "status":request.GET.get('status',"") if request.GET.get('status') else '' ,
                "created_on":request.GET.get('created_on',"") if request.GET.get('created_on') else '' ,
                "p_title":request.GET.get('p_title',"") if request.GET.get('p_title') else '' ,
                "p_event_type":request.GET.get('p_event_type',"") if request.GET.get('p_event_type') else '' ,
                "p_date":request.GET.get('p_date',"") if request.GET.get('p_date') else '' ,
                "p_category":request.GET.get('p_category',"") if request.GET.get('p_category') else '' ,
                "p_status":request.GET.get('p_status',"") if request.GET.get('p_status') else '' ,
                "p_created_on":request.GET.get('p_created_on',"") if request.GET.get('p_created_on') else '' ,
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
