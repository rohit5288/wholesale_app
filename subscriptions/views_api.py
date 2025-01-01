from api.views_authentication import *
from subscriptions.models import *
from .serializer import *

"""
Subscripotions List
"""
class SubscriptionListing(APIView):

    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Subscriptions"],
        operation_id="Subscription List",
        operation_description="Subscription List",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY,description="page",type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING,description=('Search')),
        ],
    )

    def get(self, request, *args, **kwargs):
        subscriptions=SubscriptionPlans.objects.all().order_by('-created_on').only('id')
        start,end,meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None, subscriptions)
        data = SubscriptionSerializer(subscriptions[start : end],many=True,context = {"request":request}).data
        Activities.objects.create(user=request.user,title='Accessed Plan List',description='User has Accessed Plan List')
        return Response({"data":data,"meta":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)

"""
Purchase subscription plan
"""
class SubscriptionPurchase(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Subscriptions"],
        operation_id="Subscription Plan Purchase",
        operation_description="Subscription Plan Purchase",
        manual_parameters=[
            openapi.Parameter('Plan_id', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ],
    )

    def post(self, request, *args, **kwargs):
        if request.user.role_id == SELLER:
            try:
                subscription_plan = SubscriptionPlans.objects.get(id=request.data.get('Plan_id'))
            except:
                return Response({"message":"Subscription plan not found.","status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST) 
            if UserPlanPurchased.objects.filter(subscription_plan=subscription_plan,purchased_by=request.user,is_active=True).exists():
                data = SubscriptionSerializer(subscription_plan,context = {"request":request}).data
                return Response({"message":"Plan already purchased and not expired yet!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)  
            UserPlanPurchased.objects.filter(purchased_by=request.user).update(is_active=False)    
            plan_purchase=UserPlanPurchased.objects.create(subscription_plan=subscription_plan,
                                            purchased_by=request.user,
                                            is_active=True,
                                            amount_paid = subscription_plan.price,
                                            plan_title = subscription_plan.title,
                                            features = subscription_plan.features,
                                            validity = subscription_plan.validity
                                        )  

            #implement in-app purchase for transaction.
 
            Transactions.objects.create(
                type = SUBSCRIPTION_TRANS,
                transaction_id=GenerateTransactionID(),
                amount=subscription_plan.price,
                status=True,
                created_by=request.user,
                plan_purchased = plan_purchase
            )
            User.objects.filter(id=request.user.id).update(is_plan_purchased=True)  
            data = SubscriptionSerializer(subscription_plan,context = {"request":request}).data
            Activities.objects.create(user=request.user,title='Purchased Plan',description='User has Purchased Plan')
            return Response({"message":"Plan purchased successfully!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
            
        else:
            return Response({"message":"Buyer can not purchase subscription plan","status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST) 

