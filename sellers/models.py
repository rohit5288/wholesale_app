from django.db import models
from accounts.models import *

class PromoCodes(CommonInfo):
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    status=models.BooleanField(default=True)
    discount = models.FloatField(default=0.0,null=True, blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)

    class Meta:
        managed=True
        db_table = 'promo_codes'
