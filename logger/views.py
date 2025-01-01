from .models import *
from accounts.utils import get_pagination
from accounts.common_imports import *
from django_db_logger .models import StatusLog
from .serializer import *
"""
Error Logs Management 
"""
class ErrorLogsList(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        error_logs = StatusLog.objects.all().order_by('-create_datetime')
        if request.GET.get('message'):
            error_logs = error_logs.filter(msg__icontains = request.GET.get('message').strip())
        if request.GET.get('trace'):
            error_logs = error_logs.filter(trace__icontains = request.GET.get('message').strip())
        if request.GET.get('created_on'):
            error_logs = error_logs.filter(create_datetime__date = request.GET.get('created_on'))
        return render(request, 'logger/error-logs-list.html',{
            "head_title":"Website Error Logs Management",
            "error_logs":get_pagination(request,error_logs),
            "message":request.GET.get('message',""),
            "trace":request.GET.get('trace',""),
            "created_on":request.GET.get('created_on',"")
        })



class DeleteAllLogs(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        StatusLog.objects.all().delete()
        messages.success(request,"Error logs deleted Successfully!")
        return redirect('logger:error_logs_list')


class DeleteErrorLog(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        StatusLog.objects.get(id=self.kwargs['id']).delete()
        messages.success(request,"Error log deleted successfully!")
        return redirect('logger:error_logs_list')



class ViewErrorLog(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        error_log = StatusLog.objects.get(id=self.kwargs['id'])
        return render(request, 'logger/view-error-log.html',{"head_title":"Website Error Logs Management","error_log":error_log})





"""
Email Logs Management
"""

class EmailLogsList(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        email_logs = EmailLogger.objects.all().order_by('-created_on').only('id')
        if request.GET.get('recievers_email'):
            email_logs = email_logs.filter(recievers_email__icontains=request.GET.get('recievers_email').strip())
        if request.GET.get('sender_email'):
            email_logs = email_logs.filter(sender_email__icontains=request.GET.get('sender_email').strip())
        if request.GET.get('email_subject'):
            email_logs = email_logs.filter(email_subject__icontains=request.GET.get('email_subject').strip())
        if request.GET.get('sent_status'):
            email_logs = email_logs.filter(sent_status=request.GET.get('sent_status'))
        if request.GET.get('created_on'):
            email_logs = email_logs.filter(created_on__date=request.GET.get('created_on'))
        if request.GET and not email_logs:
            messages.error(request, 'No Data Found')
        email_logs = get_pagination(request,email_logs)
        return render(request, 'email-logger/email-logs-list.html',{
            "head_title":"Email Logs Management",
            "email_logs":email_logs,
            "recievers_email":request.GET.get('recievers_email') if request.GET.get('recievers_email') else "",
            "sender_email":request.GET.get('sender_email') if request.GET.get('sender_email') else "",
            "email_subject":request.GET.get('email_subject') if request.GET.get('email_subject') else "",
            "sent_status":request.GET.get('sent_status') if request.GET.get('sent_status') else "",
            "created_on":request.GET.get('created_on') if request.GET.get('created_on') else "",
        })
    


class ViewEmailLog(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        email_log = EmailLogger.objects.get(id=self.kwargs['id'])
        return render(request, 'email-logger/view-email-log.html',{"head_title":"Email Logs Management","email_log":email_log})



class DeleteEmailLogs(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        if EmailLogger.objects.all():
            EmailLogger.objects.all().delete()
            messages.success(request,"Email logs deleted successfully!")
        else:
            messages.error(request,"No Email Logs Found!")
        return redirect('logger:email_logs_list')


class DeleteEmailLog(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        EmailLogger.objects.get(id=self.kwargs['id']).delete()
        messages.success(request, 'Email log deleted successfully!')
        return redirect('logger:email_logs_list')








class CrashLogs(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        logs = ApplicationCrashLogs.objects.all().order_by('-created_on')
        if request.GET.get('error'):
            logs = logs.filter(error__icontains = request.GET.get('error'))
        if request.GET.get('link'):
            logs = logs.filter(link__icontains = request.GET.get('link'))
        if request.GET.get('referrer_link'):
            logs = logs.filter(referer_link__icontains = request.GET.get('referrer_link'))
        if request.GET.get('user_ip'):
            logs = logs.filter(user_ip__icontains = request.GET.get('user_ip'))
        if request.GET.get('created_on'):
            logs = logs.filter(created_on__date = request.GET.get('created_on'))
        return render(request, 'application-logger/application-logs-list.html',{
            "head_title":"Application Error Logs Management",
            "logs":get_pagination(request,logs),
            "error":request.GET.get('error',""),
            "link":request.GET.get('link',""),
            "referrer_link":request.GET.get('referrer_link',""),
            "user_ip":request.GET.get('user_ip',""),
            "created_on":request.GET.get('created_on',"")
        })

class ViewCrashLog(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        log = ApplicationCrashLogs.objects.get(id=self.kwargs['id'])
        return render(request, 'application-logger/view-application-log.html',{"head_title":"Application Error Logs Management","log":log})


class DeleteAllCrashLogs(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        if ApplicationCrashLogs.objects.all():
            ApplicationCrashLogs.objects.all().delete()
            messages.success(request,"Logs deleted successfully!")
        else:
            messages.error(request,"No error logs Found!")
        return redirect('logger:crash_logs')




class DeleteCrashLog(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        ApplicationCrashLogs.objects.get(id=self.kwargs['id']).delete()
        messages.success(request, 'Log deleted successfully!')
        return redirect('logger:crash_logs')



"""
Application Crash Log Management
"""

class CreateCrashLog(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]
    @swagger_auto_schema(
        operation_description="Create application crash log",
        manual_parameters=[
            openapi.Parameter('error', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('link', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('referer_link', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('user_ip', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ],
        tags=['Application Crash log'],
        operation_id="Create application crash log",
    )
    def post(self, request, *args, **kwargs):
        try:
            ApplicationCrashLogs.objects.create(
                error = request.data.get('error'),
                link = request.data.get('link'),
                referer_link = request.data.get('referer_link'),
                user_ip = request.data.get('user_ip'),
                description = request.data.get('description')
            )
        except Exception as e:
            db_logger.exception(e)
        return Response({"message":"Crash Log Created Successfully!","status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class GetCrashLog(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]
    @swagger_auto_schema(
        operation_description="Get application crash log",
        # manual_parameters=[
        #     openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_STRING)
        # ],
        tags=['Application Crash log'],
        operation_id="Get application crash log",
    )
    def get(self, request, *args, **kwargs):
        try:
            log=ApplicationCrashLogs.objects.all().order_by('-created_on').first()
        except Exception as e:
            db_logger.exception(e)
            return Response({"message":"Crash Log not found!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if log:
            data=ApplicationCrashLogsSerializer(log,context={"request":request}).data
            return Response({"data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
        else:
            return Response({"data":[],"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)