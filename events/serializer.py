from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from events.models import *
from api.serializer import *
from datetime import datetime,timedelta

class CategorySerializer(ModelSerializer):
    class Meta:
        model = EventCategory
        exclude=("created_on","updated_on","created_by")

class TicketInventroySerializer(ModelSerializer):

    class Meta:
        model=TicketInventory
        exclude=("event","created_on","updated_on")

class EventSerializer(ModelSerializer):
    is_favourite=SerializerMethodField()
    created_by=MinorUserSerializer()
    event_images=SerializerMethodField()
    category = CategorySerializer()
    inventory = SerializerMethodField()
    def get_inventory(self,obj):
        inventory=TicketInventory.objects.filter(event=obj)
        return TicketInventroySerializer(inventory,many=True).data
    def get_event_images(self,obj):
        request=self.context.get('request')
        urls=[request.build_absolute_uri(img.image.url) for img in obj.event_images.all()]
        for url in urls:
            data=url.split('://')[1]
            url='https://'+data if USE_HTTPS else 'http://'+data 
        return urls
    
    def get_is_favourite(self,obj):
        request=self.context.get('request')
        return True if FavouriteEvents.objects.filter(user=request.user,event=obj) else False
    class Meta:
        model = Events
        fields = "__all__"

class MinorEventSerializer(ModelSerializer):
    image=SerializerMethodField()
    def get_image(self,obj):
        request=self.context.get('request')
        url=request.build_absolute_uri(obj.event_images.first().image.url) if obj.event_images.first() else ""
        if url:
            url=url.split('://')[1]
            return  'https://'+url if USE_HTTPS else 'http://' + url 
        return None
    class Meta:
        model = Events
        fields = ("id","title","image","address","city","latitude","longitude","start_datetime")


class EventHistorySerializer(ModelSerializer):
    image=SerializerMethodField()
    completed=SerializerMethodField()
    def get_completed(self,obj):
        request=self.context.get('request')
        return True if obj.end_datetime < datetime.now() else False
    def get_image(self,obj):
        request=self.context.get('request')
        url=request.build_absolute_uri(obj.event_images.first().image.url) if obj.event_images.first() else ""
        if url:
            url=url.split('://')[1]
            return  'https://'+url if USE_HTTPS else 'http://' + url 
        return None
    class Meta:
        model = Events
        fields = ("id","title","image","start_datetime","address","city","latitude","longitude","price","completed")


class EventRatingReviewSerializer(ModelSerializer):
    user=MinorUserSerializer()
    event=MinorEventSerializer()
    class Meta:
        model = EventRatingReviews
        fields = "__all__"

class BookingSerializer(ModelSerializer):
    inventory=TicketInventroySerializer()
    created_by=MinorUserSerializer()
    class Meta:
        model=Booking
        fields=('id','inventory','created_by','no_of_tickets','payment_status','amount','service_fee','total_amount','created_on','updated_on')


class TransactionSerializer(ModelSerializer):
    
    class Meta:
        model=Transactions
        fields="__all__"


class EventBoostPlanSerializer(ModelSerializer):
    
    class Meta:
        model=EventBoosterPlans
        exclude=('created_by',)


class BoostedEventsSerializer(ModelSerializer):
    expiring_days=SerializerMethodField()
    event=MinorEventSerializer()
    def get_expiring_days(self,obj):
        expiring_days=(obj.created_on + timedelta(days=obj.plan.days))-datetime.now()
        return str(expiring_days.days)+" days"
    class Meta:
        model=BoostedEvents
        exclude=('created_by',)

class TicketSerializer(ModelSerializer):
    user=MinorUserSerializer()
    event=MinorEventSerializer()
    qr_code=SerializerMethodField()
    def get_qr_code(self,obj):
        request=self.context.get('request')
        url=request.build_absolute_uri(obj.qr_code.url) if obj.qr_code else ""
        if url:
            url=url.split('://')[1]
            return  'https://'+url if USE_HTTPS else 'http://' + url 
        return None
    class Meta:
        model=Tickets
        fields="__all__"