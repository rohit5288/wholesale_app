import random
import logging
from accounts.models import *
import string
from rest_framework import status
from rest_framework.exceptions import ValidationError
db_logger = logging.getLogger('db')


def SendOTPSMS(user):
    user.temp_otp = GenerateOTP()
    user.save()
    try:
        return True
    except Exception as e:
        db_logger.exception(e)
        return False

def GenerateOTP():
    generated_otp = random.randint(1111,9999)
    if User.objects.filter(temp_otp = generated_otp):
        GenerateOTP()
    else:
        return generated_otp
    return TEMP_OTP

class RequiredFieldValidations():
    def validate_field(self,request,field_name,method,error_message):
        if method.lower() == "post":
            if not request.data.get(f'{field_name}'):
                raise ValidationError({"message": error_message, "status": status.HTTP_400_BAD_REQUEST})
                # return {"message":f"{error_message}"}
        else:
            if not request.query_params.get(f'{field_name}'):
                # return {"message":f"{error_message}"}
                raise ValidationError({"message": error_message, "status": status.HTTP_400_BAD_REQUEST}) 
