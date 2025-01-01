from accounts.utils import *
from contact_us.models import *
from static_pages.models import *
from accounts.common_imports import *
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout,login,authenticate
from .serializer import *
from api.helper import *
from threading import Thread
import re

stripe.api_key=GetStripeKey()

"""
Authentication Management
"""
class UserSignupView(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Authentication API's"],
        operation_id="user_signup",
        operation_description="User Signup",
        manual_parameters=[
            openapi.Parameter('first_name', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='First Name'),
            openapi.Parameter('last_name', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Last Name'),
            openapi.Parameter('role_id', openapi.IN_FORM, type=openapi.TYPE_NUMBER,description='2 for Buyer and 3 for Seller'),
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Email Address'),
            openapi.Parameter('mobile_no', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Mobile Number'),
            openapi.Parameter('country_code', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Country Code'),
            openapi.Parameter('country_iso_code', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Country ISO Code'),
            # openapi.Parameter('dob', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Format: YYYY-MM-DD'),
            
            # #Address
            # openapi.Parameter('address', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Address'),
            # openapi.Parameter('latitude', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Latitude'),
            # openapi.Parameter('longitude', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Longitude'),

            openapi.Parameter('password', openapi.IN_FORM, type=openapi.TYPE_STRING,description='Password'),
            openapi.Parameter('confirm_password', openapi.IN_FORM, type=openapi.TYPE_STRING,description='Confirm Password'),
            # openapi.Parameter('device_type', openapi.IN_FORM, type=openapi.TYPE_NUMBER , description='1 for Android and 2 for IOS'),
            # openapi.Parameter('device_name', openapi.IN_FORM, type=openapi.TYPE_STRING),
            # openapi.Parameter('device_token', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ]
    )
    
    def post(self, request, *args, **kwargs):
        ## Validate Required Fields
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'first_name',"post","Please enter first name"),
            RequiredFieldValidations.validate_field(self,request,'last_name',"post","Please enter last name"),
            RequiredFieldValidations.validate_field(self,request,'role_id',"post","Please select role"),
            RequiredFieldValidations.validate_field(self,request,'email',"post","Please enter email"),
            RequiredFieldValidations.validate_field(self,request,'mobile_no',"post","Please enter mobile number"),
            RequiredFieldValidations.validate_field(self,request,'country_code',"post","Please enter country code"),
            RequiredFieldValidations.validate_field(self,request,'country_iso_code',"post","Please enter country iso code"),
            # RequiredFieldValidations.validate_field(self,request,'dob',"post","Please enter date of birth"),
            # RequiredFieldValidations.validate_field(self,request,'address',"post","Please enter address"),
            # RequiredFieldValidations.validate_field(self,request,'latitude',"post","Please enter latitude"),
            # RequiredFieldValidations.validate_field(self,request,'longitude',"post","Please enter longitude"),
            RequiredFieldValidations.validate_field(self,request,'password',"post","Please enter password"),
            RequiredFieldValidations.validate_field(self,request,'confirm_password',"post","Please enter confirm password"),
            # RequiredFieldValidations.validate_field(self,request,'device_type',"post","Please enter device type"),
            # RequiredFieldValidations.validate_field(self,request,'device_name',"post","Please enter device name"),
            # RequiredFieldValidations.validate_field(self,request,'device_token',"post","Please enter device token"),
        ]))
        
        if User.objects.filter(status=ACTIVE,email=request.data.get('email')):
            return Response({"message":"There is already a registered user with this email.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(status=ACTIVE,mobile_no=request.data.get('mobile_no'),country_code=request.data.get('country_code')):
            return Response({"message":"There is already a registered user with this mobile no.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        if not request.data.get('password') == request.data.get('confirm_password'):
            return Response({"message":"Password and Confirm password doesn't match!.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        # try:
        #     dob=datetime.strptime(request.data.get('dob'),"%Y-%m-%d").date()
        # except:
        #     return Response({"message":"Please enter a valid date of birth!.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create(
            role_id = int(request.data.get('role_id')),
            first_name = request.data.get('first_name'),
            last_name = request.data.get('last_name'),
            full_name = request.data.get('first_name')+' '+request.data.get('last_name'),
            email = request.data.get('email'),
            mobile_no = request.data.get('mobile_no'),
            country_code = request.data.get('country_code'),
            country_iso_code = request.data.get('country_iso_code'),
            # dob = dob,
            password = make_password(request.data.get('password')),
            status = ACTIVE,
        )
        # if request.data.get('address'):
        #     user.address=request.data.get('address')
        #     user.latitude= request.data.get('latitude') if request.data.get('latitude') else None
        #     user.longitude= request.data.get('longitude') if request.data.get('longitude') else None
        user.save()
        BulkSendUserEmail(request,user,'EmailTemplates/registration-success.html','Welcome To Base',request.POST.get("email"),"","","","")
        try:
            token=Token.objects.get(user = user)
        except:
            token=Token.objects.create(user = user)
        try:
            OTP = GenerateOTP()
            user.temp_otp =  OTP
            user.save()
            to_num = user.country_code + user.mobile_no
            # SendtextMessage(f"Enter {OTP} on <ProjectName> to verify your account.", to_num )
            message=f"An OTP {user.temp_otp} has been sent on registered mobile number to verify your account"
            if user.email:
                BulkSendUserEmail(request,user,'EmailTemplates/ResetPassword.html','Account Verification',request.POST.get("email"),user.temp_otp,"","","")
                message=f"An OTP {user.temp_otp} has been sent on your email to verify your account."
        except Exception as e:
            db_logger.exception(e)
        data = UserSerializer(user,context = {"request":request}).data
        return Response({"message":f"User registered successfully! {message}","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


'''
Verify Otp
'''
class VerifyOTP(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Authentication API's"],
        operation_id="verify_otp",
        operation_description="Verify OTP",
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('mobile_no', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('country_code', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('otp', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ]
    )
    def post(self, request, *args, **kwargs):
        if request.data.get('email'):
            try:
                # user = User.objects.get(id=request.user.id)
                user = User.objects.get(status=ACTIVE,email = request.data.get('email'))
            except:
                return Response({"message":"User doesn't exist!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                # user = User.objects.get(id=request.user.id)
                user = User.objects.get(status=ACTIVE,mobile_no = request.data.get('mobile_no'),country_code=request.data.get('country_code'))
            except:
                return Response({"message":"User doesn't exist!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('otp'):
            return Response({"message":"Please enter otp","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if user.temp_otp == request.data.get('otp'):
            user.temp_otp = ''
            user.is_verified = True
            user.save()
            Token.objects.filter(user=user).delete()
            data = UserSerializer(user,context = {"request":request}).data
            return Response({"message":"OTP Verified Successfully.","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        else:
            return Response({"message":"Incorrect OTP","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)


'''
Resend Otp
'''
class ResendOTP(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Authentication API's"],
        operation_id="resend_otp",
        operation_description="Resend OTP",
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('mobile_no', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('country_code', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ]
    )
    def post(self, request, *args, **kwargs):
        if request.data.get('email'):
            try:
                user = User.objects.get(status=ACTIVE,email = request.data.get('email'))
                # user = User.objects.get(id=request.user.id)
            except:
                return Response({"message":"User doesn't exist!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            try:
                OTP = GenerateOTP()
                user.temp_otp =  OTP
                user.save()
                # SendtextMessage(f"Enter {OTP} on <ProjectName> to verify your account.", to_num )
                if user.email:
                    BulkSendUserEmail(request,user,'EmailTemplates/VerifyOTP.html','Account Verification',request.POST.get("email"),"","",user.temp_otp,"")
                message=f"An OTP {user.temp_otp} has been sent on your email to verify your account."
            except Exception as e:
                db_logger.exception(e)
                return Response({"message":"Something went wrong!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                user = User.objects.get(status=ACTIVE,mobile_no = request.data.get('mobile_no'),country_code = request.data.get('country_code'))
            except:
                return Response({"message":"User doesn't exist!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            try:
                OTP = GenerateOTP()
                user.temp_otp =  OTP
                user.save()
                to_num = user.country_code + user.mobile_no
                # SendtextMessage(f"Enter {OTP} on <ProjectName> to verify your account.", to_num )
                message=f"An OTP {user.temp_otp} has been sent on your mobile number to verify your account."
            except Exception as e:
                db_logger.exception(e)
                return Response({"message":"Something went wrong!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":message,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Check User Email
"""
class CheckUserEmail(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Authentication API's"],
        operation_id="check_user_email",
        operation_description="Check User Email",
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Email Address')
        ]
    )

    def post(self, request, *args, **kwargs):
        ## Validate Required Fields
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'email',"post","Please enter email"),
        ]))

        if User.objects.filter(status=ACTIVE,email=request.data.get('email')):
            return Response({"is_exists":True,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        else:
            return Response({"is_exists":False,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Authentication API's"],
        operation_id="user_login",
        operation_description="User Login",
        manual_parameters=[
            openapi.Parameter('role_id', openapi.IN_FORM, type=openapi.TYPE_NUMBER,description='2 for Buyer and 3 for Seller'),
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING,description='Email Address'),
            openapi.Parameter('mobile_no', openapi.IN_FORM, type=openapi.TYPE_STRING,description='Mobile Number'),
            openapi.Parameter('country_code', openapi.IN_FORM, type=openapi.TYPE_STRING,description='Country Code'),
            openapi.Parameter('password', openapi.IN_FORM, type=openapi.TYPE_STRING,description='Password'),
            # openapi.Parameter('device_type', openapi.IN_FORM, type=openapi.TYPE_NUMBER, description=('1 for Android and 2 for IOS')),
            # openapi.Parameter('device_name', openapi.IN_FORM, type=openapi.TYPE_STRING),
            # openapi.Parameter('device_token', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ]
    )

    def post(self, request, *args, **kwargs):
        if not request.data.get('email') and not request.data.get('mobile_no'):
            return Response({"message":"Please login using mobile number or email","status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        
        ## Validate Required Fields
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'role_id',"post","Please enter role id"),
            RequiredFieldValidations.validate_field(self,request,'password',"post","Please enter password"),
        ]))
        if request.data.get("mobile_no"):
            if not request.data.get("country_code"):
                return Response({"message":"Please enter country code","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('email'):
            try:
                user = UserAuthenticate(email = request.data.get("email").strip(),country_code=None,password = request.data.get("password").strip())
            except:
                CreateLoginHistory(request,request.data.get('email'),None,LOGIN_FAILURE,None)
                return Response({"message":"Invalid Login Credentials.", "status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                user = UserAuthenticate(email = request.data.get("mobile_no").strip(),country_code=request.data.get("country_code").strip(),password = request.data.get("password").strip())
            except:
                CreateLoginHistory(request,None, request.data.get("mobile_no").strip(),LOGIN_FAILURE,request.data.get("country_code").strip())
                return Response({"message":"Invalid Login Credentials.", "status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)    
        if not user:
            if request.data.get('email'):
                CreateLoginHistory(request,request.data.get('email'),None,LOGIN_FAILURE,None)
            if request.data.get('mobile_no'):
                CreateLoginHistory(request,None, request.data.get("mobile_no").strip(),LOGIN_FAILURE,request.data.get("country_code").strip())
            return Response({"message":"Invalid Login Credentials.", "status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        if user.status == INACTIVE:
            return Response({"message":"Your account has been inactivated. Please contact admin.","status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        
        elif user.status == DELETED:
            return Response({"message":"Your account has been deleted. Please contact admin.","status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        
        elif user.status == ACTIVE:
            if user.role_id == ADMIN:
                return Response({"message":"Invalid Login Credentials.","status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            if not user.is_verified and (user.role_id == BUYER or user.role_id == SELLER):
                try:
                    OTP = GenerateOTP()
                    user.temp_otp =  OTP
                    user.save()
                    if request.data.get('mobile_no'):
                        to_num = user.country_code + user.mobile_no
                        SendtextMessage(f"Your OTP to verify your account is {OTP}.", to_num )
                        message=f"An OTP ({user.temp_otp}) has been sent to your registered mobile number."
                    if request.data.get('email'):
                        BulkSendUserEmail(request,user,'EmailTemplates/VerifyOTP.html','Account Verification',request.POST.get("email"),"","",user.temp_otp,"")
                        message=f"An OTP {user.temp_otp} has been sent on your email to verify your account."
                except Exception as e:
                    db_logger.exception(e)
                data = UserSerializer(user,context = {"request":request}).data
                return Response({"message":message,"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
            
            # Device.objects.filter(device_token=request.data['device_token']).delete()
            # try:
            #     device = Device.objects.get(user = user)
            # except Device.DoesNotExist:
            #     device = Device.objects.create(user = user)
            # device.device_type = request.data['device_type']
            # device.device_name = request.data['device_name']
            # device.device_token = request.data['device_token']
            # device.save()
            Token.objects.filter(user=user).delete()
            user.role_id=int(request.data.get('role_id'))
            user.save()
            user.refresh_from_db()
            login(request,user)
            if request.data.get('email'):
                CreateLoginHistory(request,request.data.get('email'),None,LOGIN_SUCCESS,None)
            if request.data.get('mobile_no'):
                CreateLoginHistory(request,None, request.data.get("mobile_no").strip(),LOGIN_SUCCESS,request.data.get("country_code").strip())
        data = UserSerializer(user,context = {"request":request}).data
        return Response({"message":"Logged in successfully","data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class UserCheckView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Authentication API's"],
        operation_id="user_check",
        operation_description="User Check",
        manual_parameters=[]
    )
    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message":"User doesn't exist!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)  
        if user.role_id == BUYER:
            data = UserSerializer(user,context = {"request":request}).data
        elif user.role_id == SELLER:
            data = SellerSerializer(user,context = {"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
    


class LogoutView(APIView): 
    permission_classes = (permissions.IsAuthenticated,) 
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Authentication API's"],
        operation_id="logout",
        operation_description="Logout",
        manual_parameters=[]
    )
    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message": "User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)  
        Token.objects.filter(user=user).delete()
        Device.objects.filter(user=user).delete()
        logout(request)       
        return Response({"message":"Logout Successfully!","status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class ForgotPassword(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Authentication API's"],
        operation_id="forgot_password",
        operation_description="Forgot Password",
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('mobile_no', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('country_code', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ],
    )
    def post(self, request, *args, **kwargs):
        if not request.data.get('email') and not request.data.get('mobile_no'):
            return Response({"message": "Please enter a email or mobile_no","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('email'):
            try:
                user=User.objects.get(status=ACTIVE,email=request.data.get("email"))
            except:
                return Response({"message": "Please enter a registered email address","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            user.temp_otp=GenerateOTP()
            user.save()
            BulkSendUserEmail(request,user,'EmailTemplates/ResetPassword.html','Reset Password',request.POST.get("email"),user.temp_otp,"","","")
            message=f"An OTP {user.temp_otp} has been sent on your email to reset your password."
        else:
            try:
                user=User.objects.get(status=ACTIVE,mobile_no=request.data.get("mobile_no"),country_code=request.data.get("country_code"))
            except:
                return Response({"message": "Please enter a registered mobile number","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            user.temp_otp=GenerateOTP()
            user.save()
            to_num = user.country_code + user.mobile_no
            #SendtextMessage(f"Your OTP to verify your account is {OTP}.", to_num )
            message=f"An OTP {user.temp_otp} has been sent on your mobile number to reset your password."
        return Response({"message":message,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    
# class ForgotPassword(APIView):
#     permission_classes = (permissions.AllowAny,)
#     parser_classes = [MultiPartParser]

#     @swagger_auto_schema(
#         tags=["Authentication API's"],
#         operation_id="forgot_password",
#         operation_description="Forgot Password",
#         manual_parameters=[
#             openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING),
#         ],
#     )
#     def post(self, request, *args, **kwargs):
#         if not request.data.get('email'):
#             return Response({"message": "Please enter a email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
#         try:
#             user=User.objects.get(status=ACTIVE,email=request.data.get("email"))
#         except:
#             return Response({"message": "Please enter a registered email address","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
#         try:
#             token = Token.objects.get(user=user)
#         except:
#             token = Token.objects.create(user=user)
#         BulkSendUserEmail(request,user,'EmailTemplates/ResetPassword.html','Reset Password',request.POST.get("email"),token,"","","")
#         message="A link has been sent on your email to reset your password."
#         return Response({"message":message,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


'''
Forgot Password Resend Otp
'''
class ForgotPasswordResendOTP(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Authentication API's"],
        operation_id="forgot_password_resend_otp",
        operation_description="Forgot Password Resend OTP",
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('mobile_no', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('country_code', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ]
    )
    def post(self, request, *args, **kwargs):
        if request.data.get('email'):
            try:
                user = User.objects.get(status=ACTIVE,email = request.data.get('email'))
            except:
                return Response({"message":"User doesn't exist!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            try:
                OTP = GenerateOTP()
                user.temp_otp =  OTP
                user.save()
                to_num = user.country_code + user.mobile_no
                # SendtextMessage(f"Enter {OTP} on <ProjectName> to verify your account.", to_num )
                BulkSendUserEmail(request,user,'EmailTemplates/ResetPassword.html','Reset Password',request.POST.get("email"),user.temp_otp,"","","")
                message=f"An OTP {user.temp_otp} has been sent on your email to reset your password."
            except Exception as e:
                db_logger.exception(e)
                return Response({"message":"Something went wrong!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                user = User.objects.get(status=ACTIVE,mobile_no = request.data.get('mobile_no'),country_code = request.data.get('country_code'))
            except:
                return Response({"message":"User doesn't exist!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            try:
                OTP = GenerateOTP()
                user.temp_otp =  OTP
                user.save()
                to_num = user.country_code + user.mobile_no
                # SendtextMessage(f"Enter {OTP} on <ProjectName> to verify your account.", to_num )
                message=f"An OTP {user.temp_otp} has been sent on your mobile number to reset your password."
            except Exception as e:
                db_logger.exception(e)
                return Response({"message":"Something went wrong!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        return Response({"message":message,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Authentication API's"],
        operation_id="reset_password ",
        operation_description="Reset Password ",
        manual_parameters=[
            openapi.Parameter('new_password', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('confirm_password', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ]
    )
    def post(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'new_password',"post","Please enter new password"),
            RequiredFieldValidations.validate_field(self,request,'confirm_password',"post","Please enter confirm password"),
        ]))
        try:
            user = User.objects.get(id=request.user.id) 
        except:
            return Response({"message": "User doesn't exist!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        
        if user.check_password(request.data.get("new_password")):
            return Response({"message": "New password should be different from current password.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        if not (request.data.get("new_password") == request.data.get("confirm_password")):
            return Response({"message": "Passwords do not match!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        
        user.password = make_password(request.data.get("new_password"))
        user.save()
        Token.objects.filter(user=user).delete()
        Device.objects.filter(user=user).delete()
        logout(request)
        return Response({"message":"Password reset successfully!","status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


    

##Security Management
class ChangePassword(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Security Setting API's"],
        operation_id="change_password",
        operation_description="Change Password",
        manual_parameters=[
            openapi.Parameter('current_password', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('new_password', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('confirm_password', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ]
    )
    def post(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'current_password',"post","Please enter current password"),
            RequiredFieldValidations.validate_field(self,request,'new_password',"post","Please enter new password"),
            RequiredFieldValidations.validate_field(self,request,'confirm_password',"post","Please enter confirm password"),
        ]))
        
        try:
            user = User.objects.get(id=request.user.id) 
        except:
            return Response({"message": "User doesn't exist!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        
        if not user.check_password(request.data.get("current_password")):
            return Response({"message": "Sorry, you entered incorrect current password","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        
        if request.data.get("new_password") == request.data.get("current_password"):
            return Response({"message": "New password should be different from current password.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        
        if not (request.data.get("new_password") == request.data.get("confirm_password")):
            return Response({"message": "Passwords do not match!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        user.password = make_password(request.data.get("new_password"))
        user.save()
        Token.objects.filter(user=user).delete()
        Device.objects.filter(user=user).delete()
        logout(request)
        return Response({"message":"Password updated successfully!","status":status.HTTP_200_OK}, status=status.HTTP_200_OK)

class DeleteAccount(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Authentication API's"],
        operation_id="delete_account",
        operation_description="Delete Account",
        manual_parameters=[]
    )
    def delete(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message": "User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)  
        user.status=DELETED
        if user.username:
            user.username = user.username + str(user.id)
        user.save()
        Token.objects.filter(user=user).delete()
        Device.objects.filter(user=user).delete()
        logout(request)       
        return Response({"message":"User Account Deleted Successfully!","status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
    

class DeactivateAccount(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Authentication API's"],
        operation_id="deactivate_account",
        operation_description="Deactivate Account",
        manual_parameters=[]
    )
    def get(self,request):
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message":"User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        user.status=INACTIVE
        user.save()
        Token.objects.filter(user=user).delete()
        Device.objects.filter(user=user).delete()
        logout(request)
        return Response({"message":"User Account Deactivated successfully!","status":status.HTTP_200_OK},status=status.HTTP_200_OK)

"""
Static Pages
"""
class StaticPages(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Flat Pages"],
        operation_id="static_pages_data",
        operation_description="Flat Pages Data",
        manual_parameters=[
            openapi.Parameter('type_id', openapi.IN_FORM, type=openapi.TYPE_INTEGER, description='1 : Terms&Conditions, 2 : PrivacyPolicy, 3 : AboutUs, 4: How it works, 5: Cookie Policy'),
        ],
    )
    def post(self, request, *args, **kwargs):
        if not request.data.get('type_id'):
            return Response({"message": "Please enter page type.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        try:
            page = Pages.objects.get(type_id=request.data.get('type_id'))
        except:
            return Response({"data":[],"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        data = PagesSerializer(page,context = {"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)




"""
Faq Management
"""
class FaqList(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Faq Management"],
        operation_id="faqs",
        operation_description="Faq's",
        manual_parameters=[
            openapi.Parameter('page',openapi.IN_QUERY,description='page',type=openapi.TYPE_INTEGER),
        ],
    )

    def get(self,request,*args,**kwargs):
        faqs=FAQs.objects.all().order_by("-created_on")
        start,end,meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None, faqs)
        data = FaqSeializer(faqs[start : end],many=True,context={"request":request}).data  
        return Response({"data":data,"meta":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


"""
Contact Us
"""
class ContactUsView(APIView):
    permission_classes = [permissions.AllowAny,]
    parser_classes = [MultiPartParser]
    @swagger_auto_schema(
        tags=['Contact Us'],
        operation_id="contact_us",
        operation_description="Contact Us",
        manual_parameters=[
            openapi.Parameter('full_name', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('message', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ],
    )
    def post(self, request, *args, **kwargs):
        if not request.data.get('full_name'):
            return Response({"message": "Please enter the full name","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('email'):
            return Response({"message": "Please enter the email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('message'):
            return Response({"message": "Please enter the message","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            contact_us = ContactUs.objects.get(
                full_name = request.data.get('full_name'),
                email = request.data.get('email'),
                message = request.data.get('message'),
            )
            data = ContactUsSerializer(contact_us,context={"request":request}).data
            return Response({"message":"You have already raised the same query before!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK) 
        except:
            contact_us = ContactUs.objects.create(
                full_name = request.data.get('full_name'),
                email = request.data.get('email'),
                message = request.data.get('message'),
            )
            data = ContactUsSerializer(contact_us,context={"request":request}).data
            return Response({"message":"Thank you for contacting us. We will get back to you shortly!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK) 
        

"""
Notification Management
"""
class NotificationsList(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=['Notifications'],
        operation_id="notifications_list",
        operation_description="Notifications List",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
        ],
    )
    def get(self, request, *args, **kwargs):
        notifications = Notifications.objects.filter(created_for=request.user).order_by('-created_on').only('id')
        start,end,meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None, notifications.order_by('-created_on'))
        data = NotificationSerializer(notifications.order_by('-created_on')[start : end],many=True,context={"request":request}).data
        return Response({"data":data,"meta":meta_data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class ClearAllNotifications(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=['Notifications'],
        operation_id="clear_all_notifications",
        operation_description="Clear All Notifications",
        manual_parameters=[],
    )
    def delete(self, request, *args, **kwargs):
        notifications = Notifications.objects.filter(created_for=request.user)
        if notifications:
            notifications.delete()
            return Response({"message":"Notifications Deleted Successfully!","status": status.HTTP_200_OK}, status = status.HTTP_200_OK)
        else:
            return Response({"message":"No Notifications to Delete!","status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class DeleteNotification(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=['Notifications'],
        operation_id="delete_notification",
        operation_description="Delete Notification",
        manual_parameters=[
            openapi.Parameter('notification_id', openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ],
    )
    def delete(self, request, *args, **kwargs):
        required_fields = list(filter(None, [
            RequiredFieldValidations.validate_field(self,request,'notification_id',"get","Please enter notification id"),
        ]))
        try:
            notification = Notifications.objects.get(id=request.query_params.get('notification_id'))
        except:
            return Response({"message": "Invalid Notification Id","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        notification.delete()
        return Response({"message":"Notification Deleted Successfully!","status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class MarkReadNotification(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=['Notifications'],
        operation_id="read_notification",
        operation_description="Read Notification",
        manual_parameters=[
            openapi.Parameter('notification_id', openapi.IN_FORM, type=openapi.TYPE_STRING)
        ],
    )
    def patch(self, request, *args, **kwargs):
        try:
            notification = Notifications.objects.get(id=request.data.get('notification_id'))
        except:
            return Response({"message": "Invalid Notification Id","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        notification.is_read = True
        notification.save()
        return Response({"message":"Notification Marked As Read Successfully!","status": status.HTTP_200_OK}, status = status.HTTP_200_OK)
    


class UpdateNotificationSettings(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Notifications"],
        operation_id="notification_settings",
        operation_description="Notification Settings",
        manual_parameters=[]
    )
    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.user.id) 
        except:
            return Response({"message": "User doesn't exist!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)  
        if user.notification_enable:
            user.notification_enable = False
            user.save()
            message = "Notification disabled successfully"
        else:
            user.notification_enable = True
            user.save()
            message = "Notification enabled successfully"
        data = UserSerializer(user,context = {"request":request}).data
        return Response({"message":message,"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    
"""
Profile Management
"""
class UserProfileDetails(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Profile Management"],
        operation_id="user_profile",
        operation_description="User Profile",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request):
        if request.query_params.get('user_id'):
            try:
                user = User.objects.get(id=request.query_params.get('user_id'))
            except:
                return Response({"message":"User doesn't exist!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        else:
            user = User.objects.get(id=request.user.id)
        if user.role_id == BUYER:
            data = UserSerializer(user,context = {"request":request}).data
        elif user.role_id == SELLER:
            data = SellerSerializer(user,context = {"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class UpdateProfileDetails(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Profile Management"],
        operation_id="update_profile_buyer",
        operation_description="Update Profile ( Buyer )",
        manual_parameters=[
            openapi.Parameter('profile_pic', openapi.IN_FORM, type=openapi.TYPE_FILE,description='Profile Pic'),
            openapi.Parameter('first_name', openapi.IN_FORM, type=openapi.TYPE_STRING,description='first name'),
            openapi.Parameter('last_name', openapi.IN_FORM, type=openapi.TYPE_STRING,description='last name'),
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING,description='email'),
            openapi.Parameter('mobile_no', openapi.IN_FORM, type=openapi.TYPE_STRING,description='mobile_no'),
            openapi.Parameter('country_code', openapi.IN_FORM, type=openapi.TYPE_STRING,description='country_code'),
            openapi.Parameter('country_iso_code', openapi.IN_FORM, type=openapi.TYPE_STRING,description='country_iso_code'),
            openapi.Parameter('gender', openapi.IN_FORM, type=openapi.TYPE_STRING,description='Male:1 Female:2, Other:3 '),
            openapi.Parameter('dob', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Format: YYYY-MM-DD'),
            #Address
            openapi.Parameter('address', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Address'),
            openapi.Parameter('latitude', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Latitude'),
            openapi.Parameter('longitude', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Longitude'),
        ],
    )
    def patch(self, request, *args, **kwargs):
        try:
            user=User.objects.get(id=request.user.id)
        except:
            return Response({"message":"User not Found!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('first_name'):
            user.first_name = request.data.get('first_name')
        if request.data.get('last_name'):
            user.last_name = request.data.get('last_name')
        if request.data.get('email'):
            if User.objects.filter(status=ACTIVE,email=request.data.get('email')).exclude(id=user.id):
                return Response({"message":"There is already a registered user with this email.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            user.email = request.data.get('email')
        if request.data.get('mobile_no'):
            if User.objects.filter(status=ACTIVE,mobile_no=request.data.get('mobile_no'),country_code=request.data.get('country_code') if request.data.get('country_code') else user.country_code ).exclude(id=user.id):
                return Response({"message":"There is already a registered user with this mobile no.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            user.mobile_no = request.data.get('mobile_no')
        if request.data.get('country_code'):
            if User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),mobile_no=request.data.get('mobile_no') if request.data.get('mobile_no') else user.mobile_no ,country_code=request.data.get('country_code')).exclude(id=user.id):
                return Response({"message":"There is already a registered user with this mobile no.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            user.country_code = request.data.get('country_code')
        if request.data.get('country_iso_code'):
            user.country_iso_code = request.data.get('country_iso_code')
        if request.data.get('gender'):
            user.gender = int(request.data.get('gender'))
        if request.data.get('dob'):
            try:
                dob=datetime.strptime(request.data.get('dob'),"%Y-%m-%d").date()
            except:
                return Response({"message":"Please enter a valid date of birth!.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            user.dob = dob
        if request.FILES.get('profile_pic'):
            user.profile_pic = request.FILES.get('profile_pic')
        
        if request.data.get('address'):
            user.address=request.data.get('address')
            user.latitude= request.data.get('latitude') if request.data.get('latitude') else None
            user.longitude= request.data.get('longitude') if request.data.get('longitude') else None

        if request.data.get('first_name') or request.data.get('last_name'):
            user.full_name=" ".join([user.first_name,user.last_name])
        if not user.is_profile_setup:
            user.is_profile_setup=True
            message="Profile setup completed successfully!"
        else:
            message="Profile updated successfully!"
        user.save()
        data = UserSerializer(user,context = {"request":request}).data
        return Response({"message":message,"data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


# class UpdateMobileNumberView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     parser_classes = [MultiPartParser]

#     @swagger_auto_schema(
#         tags=["Profile Management"],
#         operation_id="change_mobile_number_send_otp",
#         operation_description="Change Mobile Number Send OTP",
#         manual_parameters=[            
#             openapi.Parameter('mobile_no', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Mobile number'),
#             openapi.Parameter('country_code', openapi.IN_FORM, type=openapi.TYPE_STRING,description='Country Code'),
#             openapi.Parameter('country_iso_code', openapi.IN_FORM, type=openapi.TYPE_STRING,description='Country ISO Code'),

#         ]
#     )
#     def post(self, request, *args, **kwargs):
#         ## Validate Required Fields
#         required_fields = list(filter(None, [
#             RequiredFieldValidations.validate_field(self,request,'mobile_no',"post","Please enter mobile number"),
#             RequiredFieldValidations.validate_field(self,request,'country_code',"post","Please enter country code"),
#             RequiredFieldValidations.validate_field(self,request,'country_iso_code',"post","Please enter country iso code"),
#         ]))
#         user=request.user
#         mob_no= request.data.get('mobile_no') if not request.data.get('mobile_no')[0]=='0' else request.data.get('mobile_no')[1:]
#         if User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),mobile_no=mob_no).exclude(id=user.id):
#             return Response({"message":"There is already a registered user with this mobile number.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        

#         ## set mobile number on user session and otp
#         user = request.user
#         # OTP = GenerateOTP()

#         # TempOtpValidation.objects.filter(mobile_no = request.data.get('mobile_no'),country_code = request.data.get('country_code')).delete()
#         # mobile_validate = TempOtpValidation.objects.create(
#         #     mobile_no = request.data.get('mobile_no'),
#         #     country_code = request.data.get('country_code'),
#         #     country_iso_code = request.data.get('company_country_iso_code'),
#         #     temp_otp = OTP
#         # )
#         user.mobile_no = mob_no
#         user.country_code = request.data.get('country_code')
#         user.country_iso_code = request.data.get('country_iso_code')
#         user.save()
#         # message = f"An OTP {OTP} has been sent on registered mobile number to verify account."
#         data = UserSerializer(user,context = {"request":request}).data
#         return Response({"message":"Contact number updated successfully!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)




# class VerifyMobileNumberView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     parser_classes = [MultiPartParser]

#     @swagger_auto_schema(
#         tags=["Profile Management"],
#         operation_id="change_mobile_number_verify_otp",
#         operation_description="Change Mobile Number Verify OTP",
#         manual_parameters=[            
#             openapi.Parameter('mobile_no', openapi.IN_FORM, type=openapi.TYPE_STRING ,description='Mobile number'),
#             openapi.Parameter('country_code', openapi.IN_FORM, type=openapi.TYPE_STRING,description='Country Code'),
#             openapi.Parameter('otp', openapi.IN_FORM, type=openapi.TYPE_STRING,description='OTP'),

#         ]
#     )
#     def post(self, request, *args, **kwargs):
#         ## Validate Required Fields
#         required_fields = list(filter(None, [
#             RequiredFieldValidations.validate_field(self,request,'otp',"post","Please enter country OTP"),
#             RequiredFieldValidations.validate_field(self,request,'mobile_no',"post","Please enter mobile number"),
#             RequiredFieldValidations.validate_field(self,request,'country_code',"post","Please enter country code"),
#         ]))
#         user = request.user
#         if User.objects.filter(status=ACTIVE,mobile_no=request.data.get('mobile_no')).exclude(id=user.id):
#             return Response({"message":"There is already a registered user with this mobile number.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
#         ## verify otp 
#         mobile_validate = TempOtpValidation.objects.filter(
#             mobile_no = request.data.get('mobile_no'),
#             country_code = request.data.get('country_code'),
#         ).order_by('created_on').last()

#         otp = int(user.temp_otp)
#         if otp == int(request.data.get('otp')):
#             user.mobile_no = mobile_validate.mobile_no
#             user.country_code = mobile_validate.country_code
#             user.country_iso_code = mobile_validate.country_iso_code
#             user.temp_otp = None
#             user.save()
#             mobile_validate.delete()
#         else:
#             return Response({"message":"Incorrect OTP.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
#         data = UserSerializer(user,context = {"request":request}).data
#         return Response({"message":"Mobile number updated successfully","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


# class UpdatEmailAddressView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     parser_classes = [MultiPartParser]

#     @swagger_auto_schema(
#         tags=["Profile Management"],
#         operation_id="update_email_address",
#         operation_description="Update Email Address ( Buyer )",
#         manual_parameters=[
#             openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING,description='Email Address'),
            
#         ],
#     )
#     def post(self, request, *args, **kwargs):
#         ## Validate Required Fields
#         required_fields = list(filter(None, [
#             RequiredFieldValidations.validate_field(self,request,'email',"post","Please enter email"),
#         ]))

        
#         user = request.user
#         if User.objects.filter(status=ACTIVE,email=request.data.get('email')).exclude(id=user.id):
#             return Response({"message":"There is already a registered user with this email.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
#         if request.data.get('email'):
#             user.email = request.data.get('email')
        
#         user.save()
#         data = UserSerializer(user,context = {"request":request}).data
#         return Response({"message":"Email updated successfully","data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)