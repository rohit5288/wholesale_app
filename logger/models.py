from accounts.models import *
from accounts.models import *


class EmailLogger(CommonInfo):
    reciever = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    email_template = models.TextField(null=True, blank=True)
    email_subject = models.TextField(null=True, blank=True)
    recievers_email = models.CharField(null=True, blank=True, max_length=100)
    sender_email = models.CharField(null=True, blank=True, max_length=100)
    sent_status = models.BooleanField(default=False)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'tbl_email_logger'

class ApplicationCrashLogs(CommonInfo):
    error = models.TextField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    referer_link = models.TextField(null=True, blank=True)
    user_ip = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'tbl_application_crash_logs'
        permissions = ()
