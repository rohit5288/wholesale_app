from django.db import models
from accounts.constants import *
from accounts.models import CommonInfo,User
from subscriptions.models import *
# Create your models here.

class EventImages(CommonInfo):
    image = models.ImageField(upload_to='event_pictures',null=True,blank=True)

    class Meta:
        managed = True
        db_table = 'event_images'


class EventCategory(CommonInfo):
    title = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    image = models.ImageField(upload_to='event_category_image',null=True,blank=True)

    class Meta:
        managed = True
        db_table = 'event_category'


class UserInterestedCategory(CommonInfo):
    user=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE,related_name="categories")
    category=models.ForeignKey(EventCategory,null=True,blank=True,on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'intrested_category'



class Events(CommonInfo):
    title = models.CharField(max_length=255,null=True,blank=True)
    event_images = models.ManyToManyField(EventImages)
    description = models.TextField(null=True,blank=True)
    address=models.CharField(max_length=255,null=True,blank=True)
    city=models.CharField(max_length=255,null=True,blank=True)
    latitude = models.FloatField(default=0.0,null=True,blank=True)
    longitude = models.FloatField(default=0.0,null=True,blank=True)
    start_datetime = models.DateTimeField(auto_now_add=False,null=True,blank=True)
    end_datetime = models.DateTimeField(auto_now_add=False,null=True,blank=True)
    event_type = models.PositiveIntegerField(choices=EVENT_TYPE,null=True, blank=True)
    # ticket_type = models.PositiveIntegerField(choices=TICKET_TYPE,null=True, blank=True)
    event_link=models.CharField(max_length=255,null=True,blank=True)
    category = models.ForeignKey(EventCategory,on_delete=models.CASCADE,null=True,blank=True)
    # price = models.FloatField(null=True, blank=True, default=0.0)
    # tickets_count=models.PositiveIntegerField(default=0,null=True,blank=True)
    status = models.PositiveIntegerField(default=ACTIVE, choices=EVENT_STATUS,null=True, blank=True)
    average_rating=models.FloatField(default=0.0,null=True,blank=True)
    views_count=models.PositiveIntegerField(default=0,null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    active=models.BooleanField(default=False,null=True,blank=True)
    instructions = models.TextField(null=True,blank=True)
    
    class Meta:
        managed = True
        db_table = 'events' 

class TicketInventory(CommonInfo):
    event = models.ForeignKey(Events,on_delete=models.CASCADE,null=True,blank=True,related_name="inventory")
    ticket_type = models.PositiveIntegerField(choices=TICKET_TYPE,null=True, blank=True)
    title = models.CharField(max_length=255,null=True,blank=True)
    stock = models.PositiveIntegerField(default=0,null=True,blank=True)
    price = models.FloatField(null=True, blank=True, default=0.0)
    class Meta:
        managed = True
        db_table = 'tickets_inventory' 

class BoostedEvents(CommonInfo):
    plan = models.ForeignKey(EventBoosterPlans,on_delete=models.CASCADE,null=True,blank=True)
    event = models.ForeignKey(Events,on_delete=models.CASCADE,null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=False)
    amount_paid = models.FloatField(null=True, blank=True)
    plan_title = models.CharField(max_length=255, null=True, blank=True)
    features = models.TextField(null=True, blank=True)
    days =  models.IntegerField(null=True,blank=True)
    
    class Meta:
        db_table = 'purchased_boosted_events'
        managed = True

class Tickets(CommonInfo):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='user_tickets')
    inventory = models.ForeignKey(TicketInventory,on_delete=models.CASCADE,null=True,blank=True,related_name='tickets')
    is_paid = models.BooleanField(default=True)
    ticket_id = models.CharField(max_length=255,null=True,blank=True)
    qr_code = models.FileField(upload_to="qr_code",null=True,blank=True)
    is_scanned = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'tickets' 


class Booking(CommonInfo):
    inventory = models.ForeignKey(TicketInventory,on_delete=models.CASCADE,null=True,blank=True,related_name='booked_ticket')
    amount = models.FloatField(null=True, blank=True)
    service_fee = models.FloatField(null=True, blank=True)
    total_amount = models.FloatField(null=True, blank=True)
    payment_status = models.BooleanField(default=False)
    no_of_tickets=models.PositiveIntegerField(null=True,blank=True)
    tickets_booked = models.ManyToManyField(Tickets,related_name="booking")
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='user_booking')

    class Meta:
        managed = True
        db_table = 'Booking'


class EventRatingReviews(CommonInfo):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    event=models.ForeignKey(Events,on_delete=models.CASCADE,null=True,blank=True)
    rating = models.FloatField(default=0.0 ,null=True,blank=True)
    review = models.TextField(null=True,blank=True)
    
    class Meta:
        managed=True
        db_table='event_rating_reviews'

class FavouriteEvents(CommonInfo):
    user=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE,related_name="favourite_events")
    event=models.ForeignKey(Events,null=True,blank=True,on_delete=models.CASCADE)

    class Meta:
        managed=True
        db_table='fovourite_events'

class RecnentlyViewedEvents(CommonInfo):
    user=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE,related_name="recently_viewed")
    event=models.ForeignKey(Events,null=True,blank=True,on_delete=models.CASCADE)

    class Meta:
        managed=True
        db_table='recently_viewed_events'

class EventViews(CommonInfo):
    user=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE)
    event=models.ForeignKey(Events,null=True,blank=True,on_delete=models.CASCADE)

    class Meta:
        managed=True
        db_table='event_views'


class ReportEvent(CommonInfo):
    user=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE)
    event=models.ForeignKey(Events,null=True,blank=True,on_delete=models.CASCADE)
    reason = models.TextField(null=True,blank=True)

    class Meta:
        managed=True
        db_table='report_event'


class Transactions(CommonInfo):
    transaction_id = models.CharField(max_length=255,null=True,blank=True)
    type = models.PositiveIntegerField(choices=TRANSACTIONS_TYPE,null=True,blank=True)
    amount= models.FloatField(max_length=255,null=True,blank=True)
    status= models.BooleanField(default=False,null=True,blank=True)
    currency = models.CharField(max_length=500,default=0,blank=True,null=True)
    receipt_url = models.TextField(null=True,blank=True)
    charge_id= models.CharField(max_length=255,null=True,blank=True)
    created_by= models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name="by_transaction")
    created_for= models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name="to_transaction")
    booking= models.ForeignKey(Booking,on_delete=models.CASCADE,null=True,blank=True)                           # transaction for booking event tickets.
    boosted_event = models.ForeignKey(BoostedEvents,on_delete=models.CASCADE,null=True,blank=True)              # transactions for boosted events.  
    plan_purchased = models.ForeignKey(UserPlanPurchased, null=True, blank=True, on_delete=models.CASCADE)   # transactions for subscription plans. 
    
    class Meta:
        managed=True
        db_table='transactions'