from django.db import models
import uuid
from accounts.models import *


class SubscriptionPlans(CommonInfo):
    title = models.CharField(max_length=255, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    features = models.TextField(null=True, blank=True)
    validity = models.PositiveIntegerField(default=1,null=True, blank=True, choices=PLAN_VALIDITY)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'tbl_subscription_plans'
        managed = True
        default_permissions = () 

class EventBoosterPlans(CommonInfo):
    title = models.CharField(max_length=255, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    features = models.TextField(null=True, blank=True)
    days = models.IntegerField(null=True,blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'tbl_boosted_plans'
        managed = True
        default_permissions = () 

class UserPlanPurchased(CommonInfo):
    subscription_plan = models.ForeignKey(SubscriptionPlans, null=True, blank=True, on_delete=models.CASCADE)
    purchased_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    amount_paid = models.FloatField(null=True, blank=True)
    plan_title = models.CharField(max_length=255, null=True, blank=True)
    features = models.TextField(null=True, blank=True)
    validity = models.PositiveIntegerField(null=True, blank=True, choices=PLAN_VALIDITY)
    
    class Meta:
        managed = True
        db_table = 'tbl_user_plan_purchased'
        default_permissions = ()