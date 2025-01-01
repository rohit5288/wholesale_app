import os
import logging
import environ
from accounts.models import *
import time
from backup .models import Backup
from datetime import date
from datetime import datetime, timedelta
from accounts.views import *
from django_db_logger .models import StatusLog
from haversine import haversine, Unit
env = environ.Env()
environ.Env.read_env()
db_logger = logging.getLogger('db')


"""
Create Backup Every Day
"""
def WeeklyDataBaseBackup():
    try:
        database = env('DB_NAME')
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if not os.path.exists(f"{path}/media/backup_files"):
            os.makedirs(f"{path}/media/backup_files")
        name = database + time.strftime('%Y%m%d-%H%M%S') + ".sql"
        file_path = f'{path}/media/backup_files/' + name
        os.system("mysqldump -h " + env('DB_HOST') + " -u " + env('DB_USER') + " -p" + env('DB_PASSWORD') + " " + database + " > " + file_path)
        Backup.objects.create(name = name,size = os.path.getsize(file_path),is_schema = False,backup_file = 'backup_files/'+name)
    except Exception as e:
        db_logger.exception(e)


"""
Delete Unnecessary Data
"""
def DeleteUnnecessaryData():
    StatusLog.objects.filter(create_datetime__lt = datetime.now()-timedelta(days=15)).delete()   
    EmailLogger.objects.filter(created_on__lt = datetime.now() - timedelta(days=15)).delete()

"""
Expire Subscription Plans
"""
def ExpireSubscriptionPlan():
    expired_plans=UserPlanPurchased.objects.filter(created_on__date__lt=(datetime.now()-timedelta(days=30)).date()).exclude(is_active=False)
    send_mail=expired_plans
    expired_plans.update(is_active=False)
    #send notifications to updrade your plan
    for user in send_mail:
        BulkSendUserEmail("",user.purchased_by,'EmailTemplates/notify_plan_upgrade.html',"Plan Updrade",user.purchased_by.email,"","","","",temp=True)

"""
Expire Event Boosted Plans
"""
def ExpireEventBoosterPlan():
    expired_booster_events=BoostedEvents.objects.filter(created_on__date__lt=(datetime.now()-timedelta(days=30)).date()).exclude(is_active=False)
    send_mail=expired_booster_events
    expired_booster_events.update(is_active=False)
    #send notifications to updrade your plan
    for user in send_mail:
        BulkSendUserEmail("",user.created_by,'EmailTemplates/notify_plan_upgrade.html',"Plan Updrade",user.purchased_by.email,"","","","",temp=True)
