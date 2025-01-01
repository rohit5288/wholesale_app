from .models import *
from accounts.common_imports import *
from events.models import *
from accounts.models import *
from events.serializer import *
from .serializer import *
import stripe
stripe.api_key=GetStripeKey()

"""
My Events Listing
"""
class MyEventsListAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Seller)"],
        operation_id="Events Listing",
        operation_description="Events Listing",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('title', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            user=User.objects.get(id=request.user.id,role_id=SELLER)
        except:
            return Response({"message":"You are not allowed to perform this action!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        events=Events.objects.filter(created_by=user).order_by('-created_on')
        if request.query_params.get('title'):
            events=events.filter(title=request.query_params.get('title'))
        start,end,meta_data=GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,events)
        data=EventSerializer(events[start:end],many=True,context={"request":request}).data
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    
"""
Add Event
"""
class AddEventAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Seller)"],
        operation_id="Add Event",
        operation_description="Add Event",
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Title'),
            openapi.Parameter('timezone', openapi.IN_FORM, type=openapi.TYPE_STRING,description=('Timezone')),
            openapi.Parameter('date', openapi.IN_FORM, type=openapi.TYPE_STRING,description=('YYYY-MM-DD')),
            openapi.Parameter('start_time', openapi.IN_FORM, type=openapi.TYPE_STRING,description=('HH:MM')),
            openapi.Parameter('end_time', openapi.IN_FORM, type=openapi.TYPE_STRING,description=('HH:MM')),
            openapi.Parameter('event_type', openapi.IN_FORM, type=openapi.TYPE_NUMBER , description='Physical:1 and Virtual:2'),
            # Address
            openapi.Parameter('address', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Address'),
            openapi.Parameter('city', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='City'),
            openapi.Parameter('latitude', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Latitude'),
            openapi.Parameter('longitude', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Longitude'),
            
            openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Event Description'),
            openapi.Parameter('event_pictures', openapi.IN_FORM, type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_FILE),description=('Event Pictures')),
            openapi.Parameter('category', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('instructions', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Additional instructions'),
            openapi.Parameter('event_link', openapi.IN_FORM, type=openapi.TYPE_NUMBER , description='Link for Virtual Events.'),
            openapi.Parameter('tickets', openapi.IN_FORM, type=openapi.TYPE_OBJECT , description='Tickets Json'),

            openapi.Parameter('ticket_type', openapi.IN_FORM, type=openapi.TYPE_NUMBER , description='Free:1 , Paid: 2, RSVP:3 and Donation:4'),
            openapi.Parameter('tickets_count', openapi.IN_FORM, type=openapi.TYPE_INTEGER),
            openapi.Parameter('price', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ]
    )
    
    def post(self, request, *args, **kwargs):
        ## Validate Required Fields
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'title',"post","Please enter event title"),
            RequiredFieldValidations.validate_field(self,request,'timezone',"post","Please enter timezone"),
            RequiredFieldValidations.validate_field(self,request,'date',"post","Please enter event date"),
            RequiredFieldValidations.validate_field(self,request,'start_time',"post","Please enter event start time"),
            RequiredFieldValidations.validate_field(self,request,'end_time',"post","Please enter event end time"),
            RequiredFieldValidations.validate_field(self,request,'event_type',"post","Please select event type"),
            #Address
            RequiredFieldValidations.validate_field(self,request,'address',"post","Please enter address"),
            RequiredFieldValidations.validate_field(self,request,'latitude',"post","Please enter latitude"),
            RequiredFieldValidations.validate_field(self,request,'longitude',"post","Please enter longitude"),
            
            RequiredFieldValidations.validate_field(self,request,'description',"post","Please enter description"),
            RequiredFieldValidations.validate_field(self,request,'event_pictures',"post","Please select event picture"),
            RequiredFieldValidations.validate_field(self,request,'category',"post","Please select category"),
            RequiredFieldValidations.validate_field(self,request,'instructions',"post","Please enter event policies."),
            
            RequiredFieldValidations.validate_field(self,request,'tickets',"post","Please enter ticket details."),
            
        ]))
        try:
            user=User.objects.get(id=request.user.id,role_id=SELLER)
        except:
            return Response({"message":"You are not allowed to perform this action!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            category=EventCategory.objects.get(id=request.data.get('category'))
        except:
            return Response({"message":"Category does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            event_date=datetime.strptime(request.data.get('date'),'%Y-%m-%d')
        except:
            return Response({"message":"Please enter valid event date!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            start_time=datetime.strptime(request.data.get('start_time'),'%H:%M')
        except:
            return Response({"message":"Please enter valid event time!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            end_time=datetime.strptime(request.data.get('end_time'),'%H:%M')
        except:
            return Response({"message":"Please enter valid event time!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            tickets_data=json.loads(request.data.get('tickets'))
        except Exception as e:
            db_logger.exception(e)
            return Response({"message":"Invalid tickets data format!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        start_datetime=datetime.combine(event_date.date(),start_time.time())
        start_datetime=ConvertToUTC(start_datetime,request.data.get('timezone'))
        
        end_datetime=datetime.combine(event_date.date(),end_time.time())
        end_datetime=ConvertToUTC(end_datetime,request.data.get('timezone'))

        if start_datetime < datetime.now():
            return Response({"message":"You cannot add events with past date and time.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        if Events.objects.filter(title=request.data.get('title')).exists():
            return Response({"message":"Event already exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        event = Events.objects.create(
            title = request.data.get('title'),
            start_datetime = start_datetime,
            end_datetime = end_datetime,
            event_type = int(request.data.get('event_type')),
            address = request.data.get('address'),
            city = request.data.get('city') if request.data.get('city') else "",
            latitude = float(request.data.get('latitude')),
            longitude = float(request.data.get('longitude')),
            description = request.data.get('description'),
            category = category,
            instructions = request.data.get('instructions'),
            event_link=request.data.get('event_link') if request.data.get('event_link') else "",
            created_by=request.user,
        )
        try:
            for ticket in tickets_data:
                inventory_obj,created=TicketInventory.objects.get_or_create(
                    event = event,
                    ticket_type = ticket['ticket_type'],
                    title = ticket['title'],
                )
                inventory_obj.stock = int(ticket['tickets_count'])
                inventory_obj.price = float(ticket['price'])
                inventory_obj.save()
        except Exception as e:
            event.delete()
            db_logger.exception(e)
            return Response({"message":"Invalid tickets data format!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        for i in request.data.getlist('event_pictures'):   
            event.event_images.add(EventImages.objects.create(image=i))
        CreateUserActivityLog(
            "Event Created",
            f"New Event: {event.title} created by {request.user.full_name if request.user.full_name else request.user.email.split('@')[0]}",
            request.user,
            EVENT_ACTIVITY,
            event.id
        )
        data = EventSerializer(event,context = {"request":request}).data
        return Response({"message":"Event Created Successfully!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Update Event
"""
class UpdateEventAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Seller)"],
        operation_id="Update Event",
        operation_description="Update Event",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Id'),
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Title'),
            openapi.Parameter('timezone', openapi.IN_FORM, type=openapi.TYPE_STRING,description=('Timezone')),
            openapi.Parameter('date', openapi.IN_FORM, type=openapi.TYPE_STRING,description=('YYYY-MM-DD')),
            openapi.Parameter('start_time', openapi.IN_FORM, type=openapi.TYPE_STRING,description=('HH:MM')),
            openapi.Parameter('end_time', openapi.IN_FORM, type=openapi.TYPE_STRING,description=('HH:MM')),
            openapi.Parameter('event_type', openapi.IN_FORM, type=openapi.TYPE_NUMBER , description='Physical:1 and Virtual:2'),
            # Address
            openapi.Parameter('address', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Address'),
            openapi.Parameter('city', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='City'),
            openapi.Parameter('latitude', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Latitude'),
            openapi.Parameter('longitude', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Longitude'),
            
            openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Event Description'),
            openapi.Parameter('event_pictures', openapi.IN_FORM, type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_FILE),description=('Event Pictures')),
            openapi.Parameter('category', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('instructions', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Additional instructions'),
            openapi.Parameter('event_link', openapi.IN_FORM, type=openapi.TYPE_NUMBER , description='Link for Virtual Events.'),
            openapi.Parameter('tickets', openapi.IN_FORM, type=openapi.TYPE_OBJECT , description='Tickets Json'),

            openapi.Parameter('ticket_type', openapi.IN_FORM, type=openapi.TYPE_NUMBER , description='FREE:1 , PAID: 2, RSVP:3, DONATION:4'),
            openapi.Parameter('tickets_count', openapi.IN_FORM, type=openapi.TYPE_INTEGER),
            openapi.Parameter('price', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ]
    )
    
    def patch(self, request, *args, **kwargs):
        try:
            user=User.objects.get(id=request.user.id,role_id=SELLER)
        except:
            return Response({"message":"You are not allowed to perform this action!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            event=Events.objects.get(id=request.data.get('id'))
        except:
            return Response({"message":"Event does not exists!","status":status.HTTP_400_BAD_REQUEST})
        if event.status in [ACTIVE,DELETED]:
            return Response({"message":"Sorry! you cannot edit active event.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        if Events.objects.filter(title=request.data.get('title')).exclude(id=event.id).exists():
            return Response({"message":"Event already exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        if request.data.getlist('title'):
            event.title = int(request.data.get('title'))

        if request.data.getlist('description'):
            event.description = request.data.get('description')
        try:
            tickets_data=json.loads(request.data.get('tickets'))
        except:
            return Response({"message":"Invalid tickets data format!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('date') and request.data.get('start_time') and request.data.get('timezone'):
            try:
                event_date=datetime.strptime(request.data.get('date'),'%Y-%m-%d')
            except:
                return Response({"message":"Please enter valid event date!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            try:
                start_time=datetime.strptime(request.data.get('start_time'),'%H:%M')
            except:
                return Response({"message":"Please enter valid event start time!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            start_datetime=datetime.combine(event_date.date(),start_time.time())
            start_datetime=ConvertToUTC(start_datetime,request.data.get('timezone'))
            
            if start_datetime != event.start_datetime and start_datetime < datetime.now():
                return Response({"message":"You cannot add events with past date and time.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            event.start_datetime = start_datetime
        
        if request.data.get('date') and request.data.get('end_time') and request.data.get('timezone'):
            try:
                event_date=datetime.strptime(request.data.get('date'),'%Y-%m-%d')
            except:
                return Response({"message":"Please enter valid event date!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            try:
                end_time=datetime.strptime(request.data.get('end_time'),'%H:%M')
            except:
                return Response({"message":"Please enter valid event end time!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            end_datetime=datetime.combine(event_date.date(),end_time.time())
            end_datetime=ConvertToUTC(end_datetime,request.data.get('timezone'))
            
            if end_datetime < event.start_datetime:
                return Response({"message":"End time should be greater than start time.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            event.end_datetime = end_datetime
        
        if request.data.getlist('event_type'):
            event.event_type = int(request.data.get('event_type'))
        
        if request.data.getlist('address'):
            event.address = request.data.get('address')
        
        if request.data.getlist('city'):
            event.city = request.data.get('city')

        if request.data.getlist('latitude'):
            event.latitude = float(request.data.get('latitude'))

        if request.data.getlist('longitude'):
            event.longitude = float(request.data.get('longitude'))
        
        if request.data.getlist('event_link'):
            event.event_link = request.data.get('event_link')

        if request.data.getlist('category'):
            try:
                category=EventCategory.objects.get(id=request.data.get('category'))
            except:
                return Response({"message":"Category does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            event.category = category

        if request.data.getlist('instructions'):
            event.instructions = request.data.get('instructions')
        if request.data.get('tickets'):
            try:
                for ticket in tickets_data:
                    if 'id' not in ticket:
                        inventory_obj,created=TicketInventory.objects.get_or_create(event=event,ticket_type=ticket['ticket_type'],title = ticket['title'])
                    else:
                        try:
                            inventory_obj=TicketInventory.objects.get(id=ticket['id'],event=event)
                        except:
                            return Response({"message":"Ticket Not Found!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
                    inventory_obj.ticket_type = ticket['ticket_type']
                    inventory_obj.title = ticket['title']
                    inventory_obj.stock = int(ticket['tickets_count'])
                    inventory_obj.price = float(ticket['price'])
                    inventory_obj.save()
            except:
                return Response({"message":"Invalid tickets data format!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)        
        if request.data.getlist('event_pictures'):
            event.event_images.clear()
            for i in request.data.getlist('event_pictures')[0].split(','):   
                event.event_images.add(EventImages.objects.create(image=i))
        event.save()
        CreateUserActivityLog(
            "Event Modified",
            f"Event: {event.title} modified by {request.user.full_name if request.user.full_name else request.user.email.split('@')[0]}",
            request.user,
            EVENT_ACTIVITY,
            event.id
        )
        data = EventSerializer(event,context = {"request":request}).data
        return Response({"message":"Event Updated Successfully!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    

class DeleteEventAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Seller)"],
        operation_id="Delete Event",
        operation_description="Delete Event",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_STRING ,description='Id'),
        ]
    )
    
    def delete(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'id',"get","Please enter event id"),            
        ]))
        try:
            user=User.objects.get(id=request.user.id,role_id=SELLER)
        except:
            return Response({"message":"You are not allowed to perform this action!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            event=Events.objects.get(id=request.query_params.get('id'))
        except:
            return Response({"message":"Event does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        event.status=DELETED
        event.save()
        CreateUserActivityLog(
            "Event Deleted",
            f"Event: {event.title} deleted by {request.user.full_name if request.user.full_name else request.user.email.split('@')[0]}",
            user,
            EVENT_ACTIVITY,
            event.id
        )
        return Response({"message":"Event Deleted Successfully!","status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class ChangeEventStatusAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Seller)"],
        operation_id="Change Event Status",
        operation_description="Change Event Status",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_STRING ,description='Id'),
        ]
    )
    def get(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'id',"get","Please enter event id"),            
        ]))
        try:
            user=User.objects.get(id=request.user.id,role_id=SELLER)
        except:
            return Response({"message":"You are not allowed to perform this action!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            event=Events.objects.get(id=request.query_params.get('id'))
        except:
            return Response({"message":"Event does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if event.status==ACTIVE:
            event.status=INACTIVE
            event.save()
            message="Event deactivated successfully!"
            log_description="Active => Inactive."
        else:
            event.status=ACTIVE
            event.save()
            message="Event activated successfully!"
            log_description="Inactive => Active."
        CreateUserActivityLog(
            "Event Status Changed",
            f"Event: {event.title} status changed by {request.user.full_name if request.user.full_name else request.user.email.split('@')[0]} from {log_description}",
            user,
            EVENT_ACTIVITY,
            event.id
        )
        return Response({"message":message,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Boost Plans Listing
"""
class EventBoostPlansListAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Seller)"],
        operation_id="Event Boost Plans",
        operation_description="Event Boost Plans",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            user=User.objects.get(id=request.user.id,role_id=SELLER)
        except:
            return Response({"message":"You are not allowed to perform this action!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        plans=EventBoosterPlans.objects.all().order_by('-created_on').only('id')
        start,end,meta_data=GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,plans)
        data=EventBoostPlanSerializer(plans[start:end],many=True,context={"request":request}).data
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    

class BoostEventAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Seller)"],
        operation_id="Boost Event",
        operation_description="Boost Event",
        manual_parameters=[
            openapi.Parameter('plan_id', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Plan ID'),
            openapi.Parameter('event_id', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Event ID'),
            openapi.Parameter('card_token', openapi.IN_FORM, type=openapi.TYPE_STRING,description="card_token"),

        ]
    )
    def post(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'event_id',"post","Please enter event id"),            
            RequiredFieldValidations.validate_field(self,request,'plan_id',"post","Please enter plan id"),            
            RequiredFieldValidations.validate_field(self,request,'card_token',"post","Please enter plan id"),            
        ]))
        try:
            user=User.objects.get(id=request.user.id,role_id=SELLER)
        except:
            return Response({"message":"You are not allowed to perform this action!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            event=Events.objects.get(id=request.data.get('event_id'))
        except:
            return Response({"message":"Event does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            plan=EventBoosterPlans.objects.get(id=request.data.get('plan_id'))
        except:
            return Response({"message":"Event Boost Plan does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if BoostedEvents.objects.filter(event=event).exists():
            return Response({"message":"Event is already boosted.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            boosted_event=None
            boosted_event=BoostedEvents.objects.create(
                event=event,
                plan=plan,
                created_by=user,
            )
            # try:
            #     payment_method=stripe.Token.retrieve(request.POST.get('card_token'))
            #     stripe.Buyer.create_source(request.user.customer_id,source=payment_method.id)
            
            # except Exception as e:
            #     try:
            #         message = str(e).split(': ')[1]
            #     except:
            #         message = str(e)
            
            #     stripe_payment=stripe.PaymentIntent.create(
            #         amount=int(plan.price*100),
            #         currency="usd",
            #         payment_method_types=["card"],
            #         customer = request.user.customer_id,
            #         description = "Base",
            #     )
            #     stripe_payment = stripe.PaymentIntent.confirm(
            #         stripe_payment.id,
            #         payment_method=payment_method.card.id,
            #         return_url="https://go/"
            #         )
            #     receipt_url = stripe.Charge.retrieve(
            #     stripe_payment.latest_charge,
            #     )
            
            Transactions.objects.create(
                transaction_id = GenerateTransactionID(),
                type = BOOST_EVENT_TRANS,
                amount= plan.price,
                status= True,
                currency = "USD",
                receipt_url = None,
                charge_id="N/A",
                created_by=user,
                boosted_event=boosted_event
            )
            data=BoostedEventsSerializer(boosted_event,context={"request":request}).data
            CreateUserActivityLog(
                "Event Boosted",
                f"Event: {event.title} boosted by {request.user.full_name if request.user.full_name else request.user.email.split('@')[0]}.",
                user,
                EVENT_ACTIVITY,
                event.id
            )
            return Response({"message":"Event Boosted Successfully!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        except Exception as e:
            db_logger.exception(e)
            if boosted_event:
                boosted_event.delete()
            return Response({"message":"Something went wrong!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)


class BoostedEventsAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Seller)"],
        operation_id="Boosted Events",
        operation_description="Boosted Events",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER ,description='page'),
        ]
    )
    def get(self, request, *args, **kwargs):

        try:
            user=User.objects.get(id=request.user.id,role_id=SELLER)
        except:
            return Response({"message":"You are not allowed to perform this action!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        boosted_events=BoostedEvents.objects.filter(created_by=user)
        start,end,meta_data=GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,boosted_events)
        data=BoostedEventsSerializer(boosted_events[start:end],many=True,context={"request":request}).data
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    


class ScanTicketAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Seller)"],
        operation_id="Scan Ticket",
        operation_description="Scan Ticket",
        manual_parameters=[
            openapi.Parameter('ticket_id', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Ticket ID'),

        ]
    )
    def post(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'ticket_id',"post","Please enter ticket id"),            
        ]))
        try:
            user=User.objects.get(id=request.user.id,role_id=SELLER)
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            ticket=Tickets.objects.get(ticket_id=request.data.get('ticket_id'))
        except:
            return Response({"message":"Ticket Not Found!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if ticket.is_scanned:
            return Response({"message":"Ticket Not Found!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        ticket.is_scanned=True
        ticket.save()
        CreateUserActivityLog(
            "Ticket Scanned",
            f"Ticket: {ticket.ticket_id} scanned by {request.user.full_name if request.user.full_name else request.user.email.split('@')[0]}.",
            user,
            EVENT_ACTIVITY,
            ticket.booking.first() if ticket.booking.first() else None,
        )
        data=TicketSerializer(ticket,context={"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    

class PromoCodesList(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["PromoCodes(Seller)"],
        operation_id="PromoCodes Listing",
        operation_description="PromoCodes Listing",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )

    def get(self, request, *args, **kwargs):
        try:
            promo_codes=PromoCodes.objects.filter(user=request.user,user__role_id=SELLER).order_by('-created_on').only('id')
        except:
            return Response({"message":"PromoCodes Not Found!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        start,end,meta_data=GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,promo_codes)
        data=PromoCodesSerializer(promo_codes[start:end],many=True,context={"request":request}).data
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class AddPromoCode(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["PromoCodes(Seller)"],
        operation_id="Add PromoCodes",
        operation_description="Add PromoCodes",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Code Name'),
            openapi.Parameter('discount', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Discount'),
        ]
    )

    def post(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'name',"post","Please enter promo name"),
            RequiredFieldValidations.validate_field(self,request,'discount',"post","Please enter discount"),
        ]))
        try:
            user=User.objects.get(id=request.user.id,role_id=SELLER)
        except:
            return Response({"message":"You are not allowed to perform this action!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not PromoCodes.objects.filter(name=request.data.get('name'),user = request.user):
            promo_code = PromoCodes.objects.create(name=request.data.get('name'),
                                    discount=request.data.get('discount'),
                                    user = request.user,
                                    code = GeneratePromoCode()
                                    )
        data = PromoCodesSerializer(promo_code,context = {"request":request}).data
        CreateUserActivityLog(
            "Promo Code Added",
            f"Promo code added.",
            user,
            EVENT_ACTIVITY,
            None,
        )
        return Response({"message":"Promo Code Added Successfully!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class UpdatePromoCode(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["PromoCodes(Seller)"],
        operation_id="Update Promo Code",
        operation_description="Update Promo Code",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Id'),
            openapi.Parameter('name', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Title'),
            openapi.Parameter('discount', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Discount'),
        ]
    )
    
    def patch(self, request, *args, **kwargs):
        try:
            promo_code=PromoCodes.objects.get(id=self.kwargs['id'],user__role_id=SELLER)
        except:
            return Response({"message":"PromoCode does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
    
        if PromoCodes.objects.filter(name=request.data.get('name')).exclude(id=promo_code.id).exists():
            return Response({"message":"Promo Code already exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        if request.data.getlist('name'):
            promo_code.name = int(request.data.get('name'))

        if request.data.getlist('discount'):
            promo_code.discount = request.data.get('discount')
        promo_code.save()
        data = PromoCodesSerializer(promo_code,context = {"request":request}).data
        CreateUserActivityLog(
            "Promo Code Updated",
            f"Promo code updated.",
            request.user,
            EVENT_ACTIVITY,
            None,
        )
        return Response({"message":"Promo Code Updated Successfully!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    
class DeletePromoCode(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["PromoCodes(Seller)"],
        operation_id="Update Promo Code",
        operation_description="Update Promo Code",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Id'),
            openapi.Parameter('name', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Title'),
            openapi.Parameter('discount', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Discount'),
        ]
    )
    
    def delete(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'id',"get","Please enter promo code id"),            
        ]))
        try:
            user=User.objects.get(id=request.user.id,role_id=SELLER)
        except:
            return Response({"message":"You are not allowed to perform this action!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            promo_code=PromoCodes.objects.get(id=request.query_params.get('id'))
        except:
            return Response({"message":"Promo Code does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        promo_code.status=DELETED
        promo_code.save()
        CreateUserActivityLog(
            "Promo Code Deleted",
            f"Promo code deleted.",
            request.user,
            EVENT_ACTIVITY,
            None,
        )
        return Response({"message":"Promo Code Deleted Successfully!","status":status.HTTP_200_OK},status=status.HTTP_200_OK)
