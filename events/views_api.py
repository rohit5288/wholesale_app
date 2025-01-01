from accounts.utils import *
from accounts.common_imports import *
from events.serializer import *
from api.helper import *
from.models import *
from itertools import chain

"""
Category Listing
"""
class CategoryListingAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Category Management"],
        operation_id="Category Listing",
        operation_description="Category Listing",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, *args, **kwargs):
        categories=EventCategory.objects.all().order_by('-created_on').only('id')
        start,end,meta_data=GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,categories)
        data=CategorySerializer(categories[start:end],many=True,context={"request":request}).data
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Interested Category Listing
"""
class InterestedCategoryListingAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Category Management"],
        operation_id="Interested Category Listing",
        operation_description="Interested Category Listing",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, *args, **kwargs):
        ids=UserInterestedCategory.objects.filter(user=request.user).values_list('id',flat=True)
        categories=EventCategory.objects.filter(id__in=ids).order_by('-created_on').only('id')
        start,end,meta_data=GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,categories)
        data=CategorySerializer(categories[start:end],many=True,context={"request":request}).data
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Mark Unmark Interested Category
"""
class MarkUnmarkInterestedCategoryAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Category Management"],
        operation_id="Mark/Unmark Interested Category",
        operation_description="Mark/Unmark Interested Category",
        manual_parameters=[
            openapi.Parameter('category_id', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            category=EventCategory.objects.get(id=request.query_params.get('category_id'))
        except:
            return Response({"message":"Category does not exist!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        interested_category,created=UserInterestedCategory.objects.get_or_create(user=request.user,category=category)
        if created:
            message="Category marked as interested."
            CreateUserActivityLog(
            "Category marked as interested",
            f"Category marked as interested.",
            request.user,
            EVENT_ACTIVITY,
            None,
            )
        else:
            interested_category.delete()
            message="Category unmarked as interested."
            CreateUserActivityLog(
            "Category unmarked as interested",
            f"Category unmarked as interested.",
            request.user,
            EVENT_ACTIVITY,
            None,
            )
            
        return Response({"message":message,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Events Listing
"""
class EventsListAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Buyer)"],
        operation_id="Events Listing",
        operation_description="Events Listing",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_NUMBER),
            openapi.Parameter('title', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_QUERY, type=openapi.TYPE_ARRAY,items=openapi.Items(type=openapi.TYPE_STRING)),
            openapi.Parameter('event_type', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,description="PHYSICAL:1,VIRTUAL:2"),
            openapi.Parameter('ticket_type', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,description="FREE:1 , PAID: 2, RSVP:3, DONATION:4"),
            openapi.Parameter('time', openapi.IN_QUERY, type=openapi.TYPE_STRING,description="HH:MM"),
            openapi.Parameter('timezone', openapi.IN_QUERY, type=openapi.TYPE_STRING,description="Timezone"),
            openapi.Parameter('min_distance', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,description="Minimum distance"),
            openapi.Parameter('max_distance', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,description="Maximum distance"),
            openapi.Parameter('latitude', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('longitude', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            user=User.objects.get(id=request.user.id,role_id=BUYER)
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        events=Events.objects.filter(status=ACTIVE).annotate(is_boosted=Exists(BoostedEvents.objects.filter(event_id=OuterRef('id'))))
        
        if request.query_params.getlist('category'):
            ids=request.query_params.getlist('category')[0].split(",")
            events=events.filter(category_id__in=ids)
        
        if request.query_params.get('event_type'):
            events=events.filter(event_type=request.query_params.get('event_type'))
        
        if request.query_params.get('title'):
            events=events.filter(title__icontains=request.query_params.get('title'))
        
        if request.query_params.get('ticket_type'):
            events=events.filter(ticket_type=request.query_params.get('ticket_type'))
        
        if request.query_params.get('time'):
            try:
                start_time=datetime.strptime(request.query_params.get('time'),'%H:%M')
            except:
                return Response({"message":"Please enter valid time!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            
            if not request.query_params.get('timezone'):
                return Response({"message":"Timezone not found!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            
            start_datetime=datetime.combine(datetime.now().date(),start_time.time())
            start_datetime=ConvertToUTC(start_datetime,request.query_params.get('timezone'))
            events=events.filter(start_datetime__time=start_datetime.time())
        
        if request.query_params.get('latitude') and request.query_params.get('longitude'):
            diff_lat = Radians(F('latitude') - float(request.query_params.get('latitude')))
            diff_long = Radians(F('longitude') - float(request.query_params.get('longitude')))
            x = (Power(Sin(diff_lat/2), 2) + Cos(Radians(float(request.query_params.get('latitude')))) 
                * Cos(Radians(F('latitude'))) * Power(Sin(diff_long/2), 2))
            y = 2 * ATan2(Sqrt(x), Sqrt(1-x))
            z = 6371 * y
            events=events.annotate(distance=z)
        
        if request.query_params.get('min_distance'):
            events=events.filter(distance__gte=request.query_params.get('min_distance'))
        
        if request.query_params.get('max_distance'):
            events=events.filter(distance__lte=request.query_params.get('max_distance'))
        data=events
        boosted_events=data.filter(is_boosted=True).order_by('?').only('id')
        unboosted_events=data.exclude(is_boosted=True).order_by('start_datetime').only('id')
        data=list(chain(boosted_events, unboosted_events))
        start,end,meta_data=GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,events)
        data=[MinorEventSerializer(event,context={"request":request}).data for event in data[start:end]]
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Popular Events Listing
"""
class PopularEventsAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Buyer)"],
        operation_id="Popular Events Listing",
        operation_description="Popular Events Listing",
    )
    def get(self, request, *args, **kwargs):
        try:
            user=User.objects.get(id=request.user.id,role_id=BUYER)
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        events=Events.objects.filter(status=ACTIVE).order_by('-average_rating')[:5].only('id')
        data=MinorEventSerializer(events,many=True,context={"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Recently Viewed Events Listing
"""
class RecentlyViewedEventsAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Buyer)"],
        operation_id="Recently Viewed Listing",
        operation_description="Recently Viewed Listing",
    )
    def get(self, request, *args, **kwargs):
        try:
            user=User.objects.get(id=request.user.id,role_id=BUYER)
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        event_ids=list(RecnentlyViewedEvents.objects.filter(user=user).order_by('-updated_on').values_list('event_id',flat=True))
        events=[Events.objects.get(id=id) for id in event_ids if Events.objects.filter(status=ACTIVE,id=id)]
        data=[MinorEventSerializer(event,context={"request":request}).data for event in events]
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Event Details
"""
class EventsDetailsAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Buyer)"],
        operation_id="Event Details",
        operation_description="Events Details",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            event=Events.objects.get(id=request.query_params.get('id'))
        except:
            return Response({"message":"Event does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        event_view,created=EventViews.objects.get_or_create(user=request.user,event=event)
        if created:
            event.views_count+=1
            event.save()
        event_view.save()
        data=EventSerializer(event,context={"request":request}).data
        AddUserRecentViews(request,event)
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Get Tickets
"""
class GetTicketsAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Buyer)"],
        operation_id="Book Tickets",
        operation_description="Book Tickets",
        manual_parameters=[
            openapi.Parameter('ticket_id', openapi.IN_FORM, type=openapi.TYPE_STRING,description="ticket_id"),
            openapi.Parameter('no_of_tickets', openapi.IN_FORM, type=openapi.TYPE_INTEGER,description="Tickets Count")
        ]
    )
    def post(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'ticket_id',"post","Please enter ticket id"),
            RequiredFieldValidations.validate_field(self,request,'no_of_tickets',"post","Please enter tickets count."),
        ]))
        try:
            user=User.objects.get(id=request.user.id,role_id=BUYER)
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            ticket=TicketInventory.objects.get(id=request.data.get('ticket_id'))
        except:
            return Response({"message":"Ticket does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        tickets_count=int(request.data.get('no_of_tickets'))
        if not tickets_count > 0:
            return Response({"message":"Tickets Count should be greater than 0.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if ticket.stock < tickets_count:
            return Response({"message":"Tickets not available!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        booking=Booking.objects.create(
            inventory=ticket,
            no_of_tickets=tickets_count,
            created_by=request.user,
        )
        amount= ticket.price * tickets_count
        try:
            service_amount=AdminServiceFees.objects.first().service_fees if AdminServiceFees.objects.first() else 0
        except:
            service_amount=0
        booking.amount=amount
        booking.service_fee=service_amount
        booking.total_amount=amount + service_amount
        booking.save()
        data=BookingSerializer(booking,context={"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Make Booking Payment
"""
class MakeBookingPayment(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Buyer)"],
        operation_id="Make Payment",
        operation_description="Make Payment",
        manual_parameters=[
            openapi.Parameter('booking_id', openapi.IN_FORM, type=openapi.TYPE_STRING,description="Booking ID"),
            openapi.Parameter('card_token', openapi.IN_FORM, type=openapi.TYPE_STRING,description="card_token"),
        ]
    )
    def post(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'booking_id',"post","Please enter booking id"),
            RequiredFieldValidations.validate_field(self,request,'card_token',"post","Please enter card token."),
        ]))
        try:
            user=User.objects.get(id=request.user.id,role_id=BUYER)
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            booking=Booking.objects.get(id=request.data.get('booking_id'))
        except:
            return Response({"message":"Booking does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        # try:
        #     payment_method=stripe.Token.retrieve(request.POST.get('card_token'))
        #     stripe.Buyer.create_source(request.user.customer_id,source=payment_method.id)
        
        # except Exception as e:
        #     try:
        #         message = str(e).split(': ')[1]
        #     except:
        #         message = str(e)
        
        # stripe_payment=stripe.PaymentIntent.create(
        #     amount=int(booking.total_amount*100),
        #     currency="usd",
        #     payment_method_types=["card"],
        #     customer = request.user.customer_id,
        #     description = "Base",
        # )
        # stripe_payment = stripe.PaymentIntent.confirm(
        #     stripe_payment.id,
        #     payment_method=payment_method.card.id,
        #     return_url="https://base.in/"
        #     )
        # receipt_url = stripe.Charge.retrieve(
        # stripe_payment.latest_charge,
        # )
        
        transaction=Transactions.objects.create(
            transaction_id =GenerateTransactionID(),
            type = BOOKING_TRANS,
            booking= booking,
            amount= booking.total_amount,
            status= True,
            currency = "USD",
            receipt_url = None,
            charge_id="N/A",
            created_by=request.user
        )
        
        booking.payment_status=True
        booking.tickets_booked.set(GenerateTickets(request,booking))
        booking.save()
        data=TransactionSerializer(transaction,context={"request":request}).data
        CreateUserActivityLog(
            "Booking Payment",
            f"Transaction has been created for booking amount {booking.total_amount}.",
            request.user,
            EVENT_ACTIVITY,
            None,
            )
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""Rating & Reviews"""

class EventRatingReviewListingAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Rating & Review"],
        operation_id="Ratings Listing",
        operation_description="Event Rating Review Listing",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER ,description='page'),
            openapi.Parameter('event_id', openapi.IN_QUERY, type=openapi.TYPE_STRING ,description='Event Id'),
        ]
    )
    def get(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'event_id',"get","Please enter event title"),
        ]))
        try:
            event=Events.objects.get(id=request.query_params.get('event_id'))
        except:
            return Response({"message":"Event does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        reviews=EventRatingReviews.objects.filter(event=event).order_by('-created_on').only('id')
        start,end,meta_data=GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,reviews)
        data=EventRatingReviewSerializer(reviews[start:end],many=True,context={"request":request}).data
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)

class EventRatingReviewAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Rating & Review"],
        operation_id="Event Rating Review",
        operation_description="Event Rating Review",
        manual_parameters=[
            openapi.Parameter('event_id', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Event Id'),
            openapi.Parameter('rating', openapi.IN_FORM, type=openapi.TYPE_INTEGER ,description='Rating'),
            openapi.Parameter('review', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Review'),
        ]
    )
    def post(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'event_id',"post","Please enter event id"),
            RequiredFieldValidations.validate_field(self,request,'rating',"post","Please enter Rating"),
            RequiredFieldValidations.validate_field(self,request,'review',"post","Please enter Review"),
        ]))
        try:
            user=User.objects.get(id=request.user.id,role_id=BUYER)
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            event=Events.objects.get(id=request.data.get('event_id'))
        except:
            return Response({"message":"Event does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if float(request.data.get('rating')) > 5.0:
            return Response({"message":"Please enter valid rating.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        rating,created=EventRatingReviews.objects.get_or_create(event=event,user=request.user)
        rating.rating=float(request.data.get('rating'))
        rating.review=request.data.get('review')
        rating.save()
        rates = EventRatingReviews.objects.filter(event = event).values_list('rating',flat=True)
        average_rate = (sum(rates)/rates.count())
        event.average_rating = average_rate
        event.save()
        data=EventRatingReviewSerializer(rating,context={"request":request}).data
        CreateUserActivityLog(
            "Event Rating Added",
            f"Rating and Review has been added for {event.title} event.",
            request.user,
            EVENT_ACTIVITY,
            None,
            )
        if created:
            return Response({"data":data,"message":"Event rated successfully!","status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        else:
            return Response({"data":data,"message":"Rating updated successfully!","status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class DeleteRatingReviewAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Rating & Review"],
        operation_id="Delete Event Review",
        operation_description="Delete Event Review",
        manual_parameters=[
            openapi.Parameter('review_id', openapi.IN_QUERY, type=openapi.TYPE_STRING ,description='Review Id'),
        ]
    )
    def delete(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'review_id',"get","Please enter review id"),
        ]))
        try:
            user=User.objects.get(id=request.user.id,role_id=BUYER)
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            review=EventRatingReviews.objects.get(id=request.data.get('review_id'))
        except:
            return Response({"message":"Review does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        CreateUserActivityLog(
            "Event Rating Removed",
            f"Rating and Review has been removed for {review.event.title} event.",
            request.user,
            EVENT_ACTIVITY,
            None,
            )
        review.delete()
        return Response({"message":"Review deleted successfully!","status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class FavouriteEventListingAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Favourites Management"],
        operation_id="Favourites Listing",
        operation_description="Favourites Listing",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER ,description='Page'),
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            user=User.objects.get(id=request.user.id,role_id=BUYER)
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        ids=FavouriteEvents.objects.filter(user=user).order_by('-created_on').values_list('event',flat=True)
        events=Events.objects.filter(id__in=ids)
        start,end,meta_data=GetPagesData(request.data.get('page') if request.query_params.get('page') else None, events)
        data=EventSerializer(events[start:end],many=True,context={"request":request}).data
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class MarkUnmarkFavouriteEventAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Favourites Management"],
        operation_id="Mark/Unmark Favourite Event",
        operation_description="Mark/Unmark Favourite Event",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_STRING ,description='Event ID'),
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            user=User.objects.get(id=request.user.id,role_id=BUYER)
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            event=Events.objects.get(id=request.query_params.get('id'))
        except:
            return Response({"message":"Event does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not FavouriteEvents.objects.filter(user=user,event=event).exists():
            FavouriteEvents.objects.create(user=user,event=event)
            message="Event marked as favourite."
        else:
            FavouriteEvents.objects.filter(user=user,event=event).delete()
            message="Event unmarked from favourites."          
        CreateUserActivityLog(
            "Marked Favourite Event",
            f"User has Marked Favourite Event",
            request.user,
            EVENT_ACTIVITY,
            None
        )
        return Response({"message":message,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class EventsHistory(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["History Management"],
        operation_id="Events History",
        operation_description="Events History",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER ,description='page'),
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            user=User.objects.get(id=request.user.id,role_id__in=[SELLER,BUYER])
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if user.role_id == SELLER:
            events=Events.objects.filter(created_by=user).order_by('-created_on').only('id')
        else:
            ids=Booking.objects.filter(created_by=user).only('event').distinct().values_list('event_id',flat=True)
            events=Events.objects.filter(id__in=ids).order_by('-created_on').only('id')
        start,end,meta_data=GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,events)
        data=EventHistorySerializer(events[start:end],many=True,context={"request":request}).data
        CreateUserActivityLog(
            "Accessed Events History",
            f"User has accessed Events History",
            request.user,
            EVENT_ACTIVITY,
            None
        )
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


'''
My Bookings Listing
'''
class MyBookingsAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Buyer)"],
        operation_id="My Bookings Listing",
        operation_description="My Bookings Listing",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER ,description='page'),
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            user=User.objects.get(id=request.user.id,role_id=BUYER)
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        bookings=Booking.objects.filter(created_by=user).order_by('-created_on').only('id')
        start,end,meta_data=GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,bookings)
        data=BookingSerializer(bookings[start:end],many=True,context={"request":request}).data
        CreateUserActivityLog(
            "Accessed My Bookings",
            f"User has accessed My Bookings",
            request.user,
            EVENT_ACTIVITY,
            None
        )
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


'''
Booking Tickets
'''
class BookingTicketsAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Buyer)"],
        operation_id="Booking Tickets Listing",
        operation_description="Booking Tickets Listing",
        manual_parameters=[
            openapi.Parameter('booking_id', openapi.IN_QUERY, type=openapi.TYPE_STRING ,description='booking_id'),
        ]
    )
    def get(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'booking_id',"get","Please enter booking id"),
        ]))
        try:
            user=User.objects.get(id=request.user.id,role_id=BUYER)
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            booking=Booking.objects.get(id=request.query_params.get('booking_id'))
        except:
            return Response({"message":"Ticket does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        tickets=booking.tickets_booked.all().order_by('-created_on').only('id')
        start,end,meta_data=GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,tickets)
        data=TicketSerializer(tickets[start:end],many=True,context={"request":request}).data
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


'''
Ticket Details
'''
class TicketDetailsAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Events Management(Buyer)"],
        operation_id="Ticket Details",
        operation_description="Ticket Details",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_STRING ,description='Ticket Id'),
        ]
    )
    def get(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'id',"get","Please enter ticket id"),
        ]))
        try:
            user=User.objects.get(id=request.user.id,role_id=BUYER)
        except:
            return Response({"message":"You are not authorized to do this task!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            ticket=Tickets.objects.get(id=request.query_params.get('id'))
        except:
            return Response({"message":"Ticket does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        CreateUserActivityLog(
            "Accessed Ticket Details",
            f"User has accessed ticket details",
            request.user,
            EVENT_ACTIVITY,
            None
        )
        data=TicketSerializer(ticket,context={"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
