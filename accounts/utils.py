import requests
import environ
import logging
import pytz
import random
import string
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core.mail import EmailMultiAlternatives,EmailMessage,get_connection
from pyfcm import FCMNotification
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from accounts.models import *
from logger.models import *
from threading import Thread
from accounts.constants import *
from datetime import datetime,date,timedelta
from django.db.models import Q 
from django.core.mail.backends.smtp import EmailBackend
from rest_framework.authtoken.models import Token 
import json
import csv
import stripe
import qrcode
import os
from django.core.mail import get_connection
from credentials.models import *
from sellers.models import *
from twilio.rest import Client
from typing import List
from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer,VerticalBarsDrawer,GappedSquareModuleDrawer,SquareModuleDrawer
from qrcode.image.styles.colormasks import HorizontalGradiantColorMask


db_logger = logging.getLogger('db')
env = environ.Env()
environ.Env.read_env()

def BulkSendUserEmail(request,user,template_name,mail_subject,to_email,token,description,title,password,temp=True):
     Thread(target=SendUserEmail,args=(request,user,template_name,mail_subject,to_email,token,description,title,password,temp)).start()

def SendUserEmail(request,user,template_name,mail_subject,to_email,token,description,title,password,temp):
    try:
        current_site = get_current_site(request)
        site_name = current_site.name
        context = {                                                                                                                     
            'domain':current_site.domain,                                                                                                                                                                   
            'site_name': site_name,
            'protocol': 'https' if USE_HTTPS else 'http',
            'user':user if user else None,
            'email':to_email if to_email else None,
            'token':token if token else "",
            'description':description if description else "",
            'title':title if title else "",
            'password':password if password else "",
        }
        ##Overriding env variable from_email with smtp cred email 
        smtp=SMTPSetting.objects.filter(is_active=True).first()
        from_email=smtp.email_host_user if smtp else env('FROM_EMAIL')
        
        message = render_to_string(str(template_name), context)        
        email_message = EmailMultiAlternatives(mail_subject, message, from_email, [to_email])
        html_email = render_to_string(str(template_name),context)
        email_message.attach_alternative(html_email, 'text/html')
        # status=True
        if settings.DEBUG:
            status = None
            try:
                status = email_message.send()
            except Exception as exception:
                status = None
                db_logger.exception(exception)
        else:
            status = None
            email_message.send()
            status = True
        EmailLogger.objects.create(
            reciever = user if temp else None,
            email_subject = mail_subject,
            email_template = html_email,
            recievers_email = to_email,
            sender_email = from_email,
            sent_status = True if status else False
        )
    except Exception as exception:
        db_logger.exception(exception)


def get_pagination(request,data,**kwagrs):
	page_size = int(kwagrs['required_page_size']) if  'required_page_size' in kwagrs.keys() else PAGE_SIZE
	page = request.GET.get('page', 1)
	paginator = Paginator(data, page_size)
	try:
		data = paginator.page(page)
	except PageNotAnInteger:
		data = paginator.page(1)
	except EmptyPage:
		data = paginator.page(paginator.num_pages)
	except Exception as e:
		data = None 
	return data 

def get_pagination1(request,data,number):
    if not number:
        number=""
    page = request.GET.get(f'{number}page', 1)
    paginator = Paginator(data, PAGE_SIZE)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    except Exception as e:
        data = None 
    return data

def CreateLoginHistory(request,user_email,mobile_no,status,country_code):
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'  
    url = f"{protocol}://"+request.META.get("REMOTE_ADDR")+request.path   
    LoginHistory.objects.create(
        user_ip = request.META.get("REMOTE_ADDR"),
        user_agent = request.META['HTTP_USER_AGENT'],
        status = status,
        url = url,
        user_email=user_email,
        mobile_no = mobile_no,
        country_code = country_code 
    )


def ConvertToUTC(data,user_timezone):
    local_tz = pytz.timezone(user_timezone if user_timezone else DEFAULT_TIMEZONE)
    UTC_tz = pytz.timezone("UTC")
    return datetime.strptime(str(UTC_tz.normalize(local_tz.localize(data).astimezone(UTC_tz))).split("+")[0], "%Y-%m-%d %H:%M:%S")


def UserAuthenticate(email,country_code,password):
    user = User.objects.filter(Q(email=email)|Q(username=email)|Q(mobile_no=email,country_code = country_code)).order_by('created_on').last()
    if user.check_password(password):
        return user
    else:
        return None


def ConvertToLocalTimezone(time_zone,date_time):
    try:
        local_tz = pytz.timezone("UTC")
        UTC_tz = pytz.timezone(time_zone)
        return datetime.strptime(str(UTC_tz.normalize(local_tz.localize(date_time).astimezone(UTC_tz))).split("+")[0], "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        db_logger.exception(e)


def GetPagesData(page, data):
	if page:
		if str(page) == '1':
			start = 0
			end = start + API_PAGINATION
		else:
			start = API_PAGINATION * (int(page)-1)
			end = start + API_PAGINATION
	else:
		start = 0
		end = start + API_PAGINATION
	page_data_value = Paginator(data, API_PAGINATION)	
	last_page = True if page_data_value.num_pages == int(page if page else 1) else False
	meta_data = { 
		"page_count": page_data_value.num_pages,
		"total_results": data.count(),
		"current_page_no": int(page if page else 1),
		"limit": API_PAGINATION,
		"last_page": last_page
	}
	return start,end,meta_data


def BulkSendNotification(created_by:User,created_for:List[User],title:str,description:str,notification_type:int,obj_id:str):
     Thread(target=SendNotification,args=(created_by,created_for,title,description,notification_type,obj_id)).start()

def SendNotification(created_by:User,created_for:List[User],title:str,description:str,notification_type:int,obj_id:str):
    try:
        for user in created_for:
            if user.notification_enable:
                notification = Notifications.objects.create(
                    title = title,
                    description = description,
                    created_for = user,
                    obj_id = obj_id,
                    notification_type = notification_type,
                    created_by = created_by,
                )
                push_service = FCMNotification(api_key=env('FCM_SERVER_KEY'))
                device = Device.objects.filter(user = user).order_by('created_on').last()
                token= Token.objects.filter(user=user).last()
                if device:
                    push_service.notify_single_device(
                        registration_id = device.device_token if device else "",
                        message_title = title, 
                        message_body = description,
                        sound = "default",
                        badge = 1,
                        data_message = {
                            "title":title,
                            "description":description,
                            "notification_id":str(notification.id),
                            "obj_id":str(notification.obj_id),
                            "sender_id":str(notification.created_by.id),
                            "access_token":str(token.key),
                            "notification_type":int(notification_type if notification_type else 0),
                        } 
                    )
    except Exception as exception:
        db_logger.exception(exception)
    return None

def DefaultSubscriptions():
    default_plans = [
        {
        "title": "Basic Plan",
        "description":"Basic Plan Description",
        "price":100,
        "validity":1
        },
        {
        "title": "Premium Plan",
        "description":"Premium Plan Description",
        "price":200,
        "validity":1
        }
    ]
    return default_plans

def DefaultBoosterPlans():
    default_plans = [
        {
        "title": "Booster Plan 1",
        "description":"Basic Plan Description",
        "price":100,
        "days":15
        },
        {
        "title": "Booster Plan 2",
        "description":"Basic Plan Description",
        "price":200,
        "days":30
        },
        {
        "title": "Booster Plan 3",
        "description":"Premium Plan Description",
        "price":300,
        "days":60
        },
    ]
    return default_plans

"""
Send text message through twilio.
"""
def SendtextMessage(body, to_num):  
    account_sid = env('ACCOUNT_SID')
    auth_token = env('AUTH_TOKEN')
    from_num = env('FROM_NUM')
    body = body
    client = Client(account_sid, auth_token) 
    try:
        message = client.messages.create( 
                                from_= from_num, 
                                body =body, 
                                to = to_num
                            ) 
    except Exception as e:
        db_logger.exception(e)
    return body 

def GetCategories():
    default_categories = [
        {
        "title": "Musical Events",
        },
        {
        "title": "Sports Events",
        },
        {
        "title": "Carnivals",
        },
        {
        "title": "Auto Expo",
        },   
        {
        "title": "Exhibition Event",
        },  
    ]
    return default_categories

# def GenerateTransactionID():
#     rand_digits = str(random.randint(1000000000, 9999999999))
#     rand_lower_string = "".join(str(random.choice(string.ascii_lowercase)) for i in range(8))
#     rand_upper_string = "".join(str(random.choice(string.ascii_uppercase)) for i in range(6))
#     code=list(rand_lower_string+rand_upper_string+rand_digits)
#     random.shuffle(code)
#     generated_id="txn_"+"".join(code)
#     if Transactions.objects.filter(transaction_id = generated_id):
#         GenerateTransactionID()
#     else:
#         return generated_id
    
def GeneratePromoCode():
    try:
        code = list("".join(str(random.choice(string.ascii_uppercase)) for i in range(8)))
        random.shuffle(code)
        if PromoCodes.objects.filter(ticket_id=code):
            GeneratePromoCode()
        else:
            return "".join(code)
    except Exception as e:
         db_logger.exception(e)
         return None


def GenerateQRCode(ticket):
    try:
        Logo_link = './static/admin-assets/images/logo.jpg'
        logo = Image.open(Logo_link)
        basewidth = 50
        wpercent = (basewidth/float(logo.size[0]))
        hsize = int((float(logo.size[1])*float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.Resampling.LANCZOS)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            # error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=4,
        )
        ticket_id = str(ticket.ticket_id)
        qr.add_data(ticket_id)
        qr.make(fit=True)
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=SquareModuleDrawer(),
            color_mask=HorizontalGradiantColorMask(left_color=(30, 132, 91),right_color=(221, 153, 51)),
        ).convert('RGB')
        pos = ((img.size[0] - logo.size[0]) // 2,
            (img.size[1] - logo.size[1]) // 2)
        img.paste(logo, pos)
        path = settings.BASE_DIR
        if not os.path.exists(f"{path}/media/qr_code/"):
            os.makedirs(f"{path}/media/qr_code/")
        img.save(f"{path}/media/qr_code/" + ticket_id + '.png')
        ticket.qr_code = f"qr_code/{ticket_id}.png"
        ticket.save()
        return True
    except Exception as e:
        db_logger.exception(e)
        booking=ticket.booking.first()
        if booking:
             booking.no_of_tickets -=1
             booking.save()
        ticket.delete()
        return False  

    tickets=[]
    for i in range(booking.no_of_tickets):
        ticket_id=GenerateTicketID()
        ticket=Tickets.objects.create(
            user=request.user,
            inventory=booking.inventory,
            is_paid = True,
            ticket_id = ticket_id if ticket_id else "",
        )
        GenerateQRCode(ticket)
        tickets.append(ticket)
    return tickets


def GetWeekDates():
    today_date = date.today()
    weekday = today_date.isoweekday()
    start = today_date - timedelta(days=weekday)
    return [start + timedelta(days=d) for d in range(7)]

def GetStripeKey():
    try:
        api_key = StripeSetting.objects.get(is_active=True)
    except:
        try:
            api_key,created = StripeSetting.objects.get_or_create(test_secretkey=env('STRIPE_TEST_KEY'),test_publishkey=env('STRIPE_PUBLISH_KEY'),is_active=True,created_by__role_id=1)
        except:
            api_key=None
    return api_key.test_secretkey if api_key else None


def CreateUserActivityLog(title:str,description:str,user:User,activity_type:int,object_id:str):
     try:
        Activities.objects.create(
            title = title,
            description = description,
            user = user,
            activity_type = activity_type,
            object_id = object_id
        )
     except Exception as e:
        db_logger.exception(e)

