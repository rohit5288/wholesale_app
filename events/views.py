from django.shortcuts import render
from .models import *
from accounts.common_imports import *


class CategoriesListing(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        categories=EventCategory.objects.all().order_by('-created_on')
        if request.GET.get('title'):
            categories=categories.filter(title__icontains=request.GET.get('title'))
        if request.GET.get('description'):
            categories=categories.filter(description__icontains=request.GET.get('description'))
        if request.GET.get('created_on'):
            categories=categories.filter(created_on__date=request.GET.get('created_on'))
        if not categories and request.GET:
            messages.success(request,"Event Categories Not Found!")
        return render(request,"events/categories.html",{
            "head_title":"Category Management",
            "categories":get_pagination(request,categories),
            "title":request.GET.get('title',""),
            "description":request.GET.get('description',""),
            "created_on":request.GET.get('created_on',""),
        })
    def post(self,request,*args,**kwargs):
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        # Check if the title already exists
        category, created = EventCategory.objects.get_or_create(
            title=title,
        )
        if not created:
            messages.error(request,"Category already exists!")
            return redirect('events:event_category_list')
        category.description=description
        category.created_by=request.user
        category.save()
        messages.success(request, 'Category Created Successfully!')
        return redirect('events:event_category_list')


class AddDefaultCategory(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        categories=GetCategories()
        for data in categories: 
            if not EventCategory.objects.filter(title=data['title']).exists():
                EventCategory.objects.create(
                    title = data['title'] if data['title'] else "",
                    created_by=request.user
                )      
        messages.success(request,'Categories Added Successfully!')
        return redirect('events:event_category_list')

class ImportCategoriesdata(View):
    def post(self,request,*args,**kwargs):
        file=request.FILES.get('file')
        try:
            data = pd.read_csv(file) 
            df = pd.DataFrame(data, columns=['Title','Description'])
            for row,item in data.iterrows():
                if not EventCategory.objects.filter(title=item["Title"]).exists():
                        EventCategory.objects.create(
                            title = item["Title"] if item["Title"] else "",
                            description=item["Description"] if item["Description"] else "",
                            created_by=request.user
                        )
            messages.success(request, 'Categories imported successfully!')
            return redirect("events:event_category_list")
        except:
            messages.success(request,"There is something wrong with uploaded file. Please check and try again.")
            return redirect("events:event_category_list")




class ViewCategory(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        try:
            category=EventCategory.objects.get(id=self.kwargs.get('id'))
        except:
            messages.error(request,"Category does not exists!")
            return redirect('events:event_category_list')
        return render(request,"events/view-category.html",{
            "head_title":"Category Management",
            "category":category,
        })


class UpdateCategory(View):
    @method_decorator(admin_only)
    def post(self,request,*args,**kwargs):
        title = request.POST.get('e_title')
        description = request.POST.get('e_description')
        category=EventCategory.objects.get(id=request.POST.get('category_id'))
        # Check if the title already exists
        if EventCategory.objects.filter(title=title).exclude(id=category.id):
            messages.error(request,"Category already exists!")
            return redirect('events:event_category_list')
        category.title=title
        category.description=description
        category.save()
        messages.success(request, 'Category Updated Successfully!')
        if request.GET.get('view') == "true":
            return redirect('events:view_category',id=category.id)
        return redirect('events:event_category_list')


class DeleteCategory(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        category=EventCategory.objects.get(id=self.kwargs.get('id'))
        if Events.objects.filter(category=category).exists():
            messages.error(request,"Category cannot be deleted!")
        else:
            category.delete()
            messages.success(request, 'Category Deleted Successfully!')
        return redirect('events:event_category_list')


class EventsListing(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        events=Events.objects.all().order_by('-created_on')
        if request.GET.get('title'):
            events=events.filter(title__icontains=request.GET.get('title'))
        if request.GET.get('category'):
            events=events.filter(category__title__icontains=request.GET.get('category'))
        if request.GET.get('event_type'):
            events=events.filter(event_type=request.GET.get('event_type'))
        if request.GET.get('status'):
            events=events.filter(status=request.GET.get('status'))
        if request.GET.get('date'):
            events=events.filter(start_datetime__date=request.GET.get('date'))
        if request.GET.get('created_on'):
            events=events.filter(created_on__date=request.GET.get('created_on'))
        if not events and request.GET:
            messages.success(request,"Events Not Found!")
        return render(request,"events/event-list.html",{
            "head_title":"Events Management",
            "events":get_pagination(request,events),
            "title":request.GET.get('title',""),
            "event_type":request.GET.get('event_type',""),
            "date":request.GET.get('date',""),
            "category":request.GET.get('category',""),
            "status":request.GET.get('status',""),
            "created_on":request.GET.get('created_on',""),
        })


class ViewEventDetails(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        event=Events.objects.get(id=self.kwargs.get('id'))
        ratings=EventRatingReviews.objects.filter(event=event)
        try:
            rating_bars=EventRatingsBars(request,event.id,ratings.count())
        except:
            rating_bars=((5,0),(4,0),(3,0),(2,0),(1,0))
        return render(request,"events/view-event.html",{
            "head_title":"Events Management",
            "event":event,
            "rating_bars":rating_bars,
            "ratings":ratings
        })
    
class BookingsListing(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        bookings=Booking.objects.all().order_by('-created_on')
        if request.GET.get('event'):
            bookings=bookings.filter(inventory__event__title__icontains=request.GET.get('event').strip())
        if request.GET.get('amount'):
            bookings=bookings.filter(amount=request.GET.get('amount'))
        if request.GET.get('payment_status'):
            bookings=bookings.filter(payment_status=request.GET.get('payment_status'))
        if not bookings and request.GET:
            messages.success(request,"Bookings Not Found!")
        return render(request,"bookings/bookings-list.html",{
            "head_title":"Bookings Management",
            "bookings":get_pagination(request,bookings),
            "event":request.GET.get('event',""),
            "amount":request.GET.get('event_type',""),
            "payment_status":request.GET.get('payment_status',""),
            "created_on":request.GET.get('created_on',""),
        })


class ViewBookingDetails(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        booking=Booking.objects.get(id=self.kwargs.get('id'))
        return render(request,"bookings/view-booking.html",{
            "head_title":"Bookings Management",
            "booking":booking
        })


class RatingandReviewsList(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        try:
            event=Events.objects.get(id=self.kwargs.get('id'))
        except:
            messages.error(request,"Event does not exists!")
            return redirect('events:event_list')
        ratings=EventRatingReviews.objects.filter(event = event).order_by('-created_on')
        return render(request,'events/event-ratings.html',{'ratings':get_pagination(request, ratings),'event':event,'head_title':'Events Management'})


class InactivateEvent(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        event = Events.objects.get(id=self.kwargs['id'])
        event.status = INACTIVE
        event.save()
        messages.success(request,'Event deactivated successfully!')
        return redirect('events:view_event_details',id=event.id)


class ActivateEvent(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        event = Events.objects.get(id=self.kwargs['id'])
        event.status = ACTIVE
        event.save()
        messages.success(request,'Event activated successfully!')
        return redirect('events:view_event_details',id=event.id)

class DeleteEvent(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        event = Events.objects.get(id=self.kwargs['id'])
        event.status = DELETED
        event.save()
        messages.success(request,'Event deleted successfully!')
        return redirect('events:view_event_details',id=event.id)


"""
Subscription Transactions
"""
class SubscriptionTransactionsList(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        transaction = Transactions.objects.filter(type = SUBSCRIPTION_TRANS).order_by('-created_on')
        subscription_plans = SubscriptionPlans.objects.all()
        if request.GET.get('transaction_id'):
            transaction = transaction.filter(transaction_id__icontains = request.GET.get('transaction_id').strip())
        if request.GET.get('plan'):
            transaction = transaction.filter(plan_purchased__subscription_plan__title__icontains = request.GET.get('plan').strip())
        if request.GET.get('amount'):
            transaction = transaction.filter(amount__icontains = request.GET.get('amount').strip())
        if request.GET.get('status'):
            transaction = transaction.filter(status = request.GET.get('status').strip())
        if request.GET.get('created_on'):
            transaction = transaction.filter(created_on__date = request.GET.get('created_on').strip())
        if request.GET and not transaction:
            messages.success(request,"Transactions Not Found!")
        return render(request,'transactions/subscription_transactions/transactions-list.html',{
            'head_title':'Subscription Transactions Management',
            'transactions':get_pagination(request,transaction),
            'subscription_plans':get_pagination(request,subscription_plans),
            'transaction_id':request.GET.get('transaction_id',''),
            'plan':request.GET.get('plan',''),
            'seller':request.GET.get('seller',''),
            'amount':request.GET.get('amount',''),
            'status':request.GET.get('status',''),
            'created_on':request.GET.get('created_on',''),
        })

"""
Transaction Detail
"""
class TransactionDetail(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        transaction = Transactions.objects.get(id=self.kwargs['id'])
        if transaction.type == SUBSCRIPTION_TRANS:
            head_title="Subscription Transactions Management"
        elif transaction.type == BOOST_EVENT_TRANS:
            head_title="Boosted Events Management"
        else:
            head_title="Events Booking Management"
        return render(request, 'transactions/transaction-details.html',{
            'head_title':head_title,
            'transaction':transaction,
        })


"""
Events Bookings Transactions
"""
class EventBookingTransactionsList(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        service_fees = AdminServiceFees.objects.all().first()
        event_bookings = Transactions.objects.filter(type = BOOKING_TRANS).order_by('-created_on')
        total_booking = event_bookings.aggregate(Sum("amount",default=0))['amount__sum']
        booking_service_fee = event_bookings.aggregate(Sum("booking__service_fee",default=0))['booking__service_fee__sum']
        return render(request,'transactions/event_bookings/transactions-list.html',{
            'head_title':'Events Booking Management',
            'service_fees':service_fees,
            'event_bookings':get_pagination(request,event_bookings),
            'booking_service_fee':booking_service_fee,
            'total_booking':total_booking
        })

"""
Booking Transaction Detail
"""
class BookingTransactionDetail(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        transaction = Transactions.objects.get(id=self.kwargs['id'])
        return render(request, 'transactions/transaction-details.html',{
            'transaction':transaction,
            'head_title':"Events Booking Management",
        })

"""
Booking Transaction Detail
"""
class BookingTransactionDetail(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        transaction = Transactions.objects.get(id=self.kwargs['id'])
        return render(request, 'transactions/transaction-details.html',{
            'transaction':transaction,
            'head_title':"Events Booking Management",
        })

"""
Boosted Events Transactions
"""
class BoosterTransactionsList(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        boosted_events = Transactions.objects.filter(type = BOOST_EVENT_TRANS).order_by('-created_on')
        return render(request,'transactions/boosted_events/transactions-list.html',{
            'head_title':'Boosted Events Management',
            'boosted_events':get_pagination(request,boosted_events)
        })


"""
Boosted Event Transaction Detail
"""
class BoostedEventTransactionDetail(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        Activities.objects.create(user=request.user,title='Viewed Boosted Events transaction details',description='user Viewed Boosted Events transaction details')
        transaction = Transactions.objects.get(id=self.kwargs['id'])
        return render(request, 'transactions/transaction-details.html',{
            'transaction':transaction,
            'head_title':"Boosted Events Management",
        })
  