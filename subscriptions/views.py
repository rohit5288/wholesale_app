from django.shortcuts import render,redirect
from accounts.decorators import *
from accounts.utils import *
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import TemplateView, View
from .models import *
from django.utils.decorators import method_decorator


class AllSubscriptionPlans(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        plans = SubscriptionPlans.objects.filter(is_deleted=False).order_by('-created_on').only('id')
        if request.GET and not plans:
            messages.error(request, 'No Data Found')
        if request.GET.get('title'):
            plans=plans.filter(title__icontains=request.GET.get('title').strip())
        if request.GET.get('plan_type'):
            plans=plans.filter(validity=request.GET.get('plan_type'))
        if request.GET.get('price'):
            plans=plans.filter(price__icontains=request.GET.get('price').strip())
        if request.GET.get('created_on'):
            plans=plans.filter(created_on__date=request.GET.get('created_on'))
        return render(request, 'subscription/subscription-plans.html',{
            "head_title":"Subscription Plans Management",
            "plans":plans,
            "title":request.GET.get('title','') if request.GET.get('title') else '' ,
            "plan_type":request.GET.get('plan_type','') if request.GET.get('plan_type') else '' ,
            "price":request.GET.get('price','') if request.GET.get('price') else '' ,
            "created_on":request.GET.get('created_on','') if request.GET.get('created_on') else '' ,
        })
    
class AddSubscriptionPlan(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        return render(request, 'subscription/add-subscription-plan.html',{
            "head_title":"Subscription Plans Management",
        })  
    def post(self,request,*args,**kwargs):
        if SubscriptionPlans.objects.filter(title=request.POST.get('title').strip(),validity=request.POST.get('validity')).exists():
            messages.success(request, "Subscription Plan Already exists!")
        else:
            SubscriptionPlans.objects.create(
            title=request.POST.get('title'),
            price=request.POST.get('price'),
            features=request.POST.get('content'),
            # validity=request.POST.get('validity'),
            )
            messages.success(request, "Subscription Plan Added Successfully!")

        return redirect('subscriptions:all_plans')
    

class ViewSubscriptionPlan(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        plan = SubscriptionPlans.objects.get(id=self.kwargs['id'])
        return render(request, 'subscription/view-plan.html',{
            "head_title":"Subscription Plans Management",
            "plan":plan,
        })


class EditSubscriptionPlan(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        plan = SubscriptionPlans.objects.get(id=self.kwargs['id'])
        return render(request,'subscription/edit-subscription-plan.html',{'head_title':'Subscription Plans Management','plan':plan})
    
    def post(self,request,*args,**kwargs):
        if SubscriptionPlans.objects.filter(title=request.POST.get('title').strip()).exclude(id=self.kwargs['id']):
            messages.error(request,"Subscription Plan already exists with this title.")
        else:    
            plan = SubscriptionPlans.objects.get(id=self.kwargs['id'])
            if request.POST.get('title')  :
                plan.title=request.POST.get('title')     
            if request.POST.get('price'):
                plan.price=request.POST.get('price')  
            if request.POST.get('content')  :
                plan.features=request.POST.get('content')  
            # if request.POST.get('validity'):     
            #     plan.validity=request.POST.get('validity')     
            plan.save()
            messages.success(request, "Plan Updated Successfully!")
        return redirect('subscriptions:all_plans')


class DeleteSubscriptionPlan(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        if UserPlanPurchased.objects.filter(subscription_plan=self.kwargs['id']):
            messages.error(request, "Plan cannot be deleted because it is being used by the customer.!")
            return redirect('subscriptions:all_plans')
        try:
            plan=SubscriptionPlans.objects.get(id=self.kwargs['id'])
            plan.is_deleted = True
            plan.save()
        except:
            messages.error(request,"Subscription Plan does not exists.")
        messages.success(request, "Plan Deleted Successfully!")
        Activities.objects.create(user=request.user,title='deleted Plan',description='User has deleted Plan')
        return redirect('subscriptions:all_plans')


class AddDefaultSubscription(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        for data in DefaultSubscriptions(): 
            if not SubscriptionPlans.objects.filter(title=data['title']).exclude(is_deleted=True).exists():
                SubscriptionPlans.objects.create(
                    title = data['title'] if data['title'] else "",
                    features = data['description'] if data['description'] else "",
                    price = data['price'] if data['price'] else "",
                    validity = data['validity'] if data['validity'] else "",
                )      
        messages.success(request,'Plans Added Successfully!')
        Activities.objects.create(user=request.user,title='Added Derault Subscription',description='User has Added Derault Subscription')
        return redirect('subscriptions:all_plans')



class AllEventBoosterPlans(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        booster_plans = EventBoosterPlans.objects.filter(is_deleted=False).order_by('-created_on').only('id')
        if request.GET and not booster_plans:
            messages.error(request, 'No Data Found')
        if request.GET.get('title'):
            booster_plans=booster_plans.filter(title__icontains=request.GET.get('title').strip())
        # if request.GET.get('plan_type'):
        #     booster_plans=booster_plans.filter(validity=request.GET.get('plan_type'))
        if request.GET.get('price'):
            booster_plans=booster_plans.filter(price__icontains=request.GET.get('price').strip())
        if request.GET.get('created_on'):
            booster_plans=booster_plans.filter(created_on__date=request.GET.get('created_on'))
        Activities.objects.create(user=request.user,title='Viewed Booted Plan',description='User has Viewed Booster Plan')
        return render(request, 'booster_plans/booster-plans.html',{
            "head_title":"Event Booster Plan Management",
            "booster_plans":booster_plans,
            "title":request.GET.get('title','') if request.GET.get('title') else '' ,
            "plan_type":request.GET.get('plan_type','') if request.GET.get('plan_type') else '' ,
            "price":request.GET.get('price','') if request.GET.get('price') else '' ,
            "created_on":request.GET.get('created_on','') if request.GET.get('created_on') else '' ,
        })
    
class AddEventBoosterPlan(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        return render(request, 'booster_plans/add-booster-plan.html',{
            "head_title":"Event Booster Plan Management",
        })  

    def post(self,request,*args,**kwargs):
        if SubscriptionPlans.objects.filter(title=request.POST.get('title').strip(),validity=request.POST.get('validity')).exists():
            messages.success(request, "Subscription Plan Already exists!")
        else:
            EventBoosterPlans.objects.create(
            title=request.POST.get('title'),
            price=request.POST.get('price'),
            features=request.POST.get('content'),
            days=request.POST.get('days'),
            )
            Activities.objects.create(user=request.user,title='Added Booted Plan',description='User has Added Booster Plan')
            messages.success(request, "Booster Plan Added Successfully!")
        return redirect('subscriptions:all_booster_plans')
    

class ViewEventBoosterPlan(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        plan = EventBoosterPlans.objects.get(id=self.kwargs['id'])
        Activities.objects.create(user=request.user,title='Accessed Booted Plan',description='User has Accessed Booster Plan')  
        return render(request, 'booster_plans/view-booster-plan.html',{
            "head_title":"Event Booster Plan Management",
            "plan":plan,
        })


class EditEventBoosterPlan(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        plan = EventBoosterPlans.objects.get(id=self.kwargs['id'])
        Activities.objects.create(user=request.user,title='Edited Booted Plan',description='User has Edited Booster Plan')  
        return render(request,'booster_plans/edit-booster-plan.html',{'head_title':'Event Boost Plan Management','plan':plan})
    
    def post(self,request,*args,**kwargs):
        if EventBoosterPlans.objects.filter(title=request.POST.get('title').strip()).exclude(id=self.kwargs['id']):
            messages.error(request,"Subscription Plan already exists with this title.")
        else:    
            plan = EventBoosterPlans.objects.get(id=self.kwargs['id'])
            if request.POST.get('title')  :
                plan.title=request.POST.get('title')     
            if request.POST.get('price'):
                plan.price=request.POST.get('price')  
            if request.POST.get('content')  :
                plan.features=request.POST.get('content')  
            if request.POST.get('validity'):     
                plan.days=request.POST.get('days')     
            plan.save()
            messages.success(request, "Booster Updated Successfully!")
        return redirect('subscriptions:all_booster_plans')


class DeleteEventBoosterPlan(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        if BoostedEvents.objects.filter(plan=self.kwargs['id']):
            messages.error(request, "Plan cannot be deleted because it is being used by the sellers.!")
            return redirect('subscriptions:all_booster_plans')
        try:
            plan=EventBoosterPlans.objects.get(id=self.kwargs['id'])
            plan.is_deleted = True
            plan.save()
        except:
            messages.error(request,"Booster Plan does not exists.")
        messages.success(request, "Plan Deleted Successfully!")
        Activities.objects.create(user=request.user,title='Deleted Booted Plan',description='User has deleted Booster Plan')  
        return redirect('subscriptions:all_booster_plans')


class AddDefaultBoosterPlans(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        for data in DefaultBoosterPlans(): 
            if not EventBoosterPlans.objects.filter(title=data['title'],days=data['days']).exclude(is_deleted=True).exists():
                EventBoosterPlans.objects.create(
                    title = data['title'] if data['title'] else "",
                    features = data['description'] if data['description'] else "",
                    price = data['price'] if data['price'] else "",
                    days = data['days'] if data['days'] else "",
                )      
        messages.success(request,'Plans Added Successfully!')
        Activities.objects.create(user=request.user,title='Added Default Booted Plan',description='User has Added Default Booster Plan')  
        return redirect('subscriptions:all_booster_plans')