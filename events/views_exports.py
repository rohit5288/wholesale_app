import csv
import time
from accounts.common_imports import *
from .models import *
import pandas as pd
from django.http import HttpResponse



def ConvertDataCSV(data,file_name):
    DATETIME = time.strftime('%Y%m%d-%H%M%S')
    name= file_name + DATETIME
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename= '+ name +".csv"
    writer = csv.writer(response)
    writer.writerow([column for column in data.columns])
    writer.writerows(data.values.tolist())
    return response

class ExportCategories(View):
    def post(self,request,*args,**kwargs):
        catgories = EventCategory.objects.all().order_by('-created_on').only('id')
        data = pd.DataFrame({
            "Title": [cat.title if cat.title else '--' for cat in catgories],
            "Descrioption": [cat.description if cat.description else '-' for cat in catgories],
            "Created on": [ConvertToLocalTimezone(request.POST.get('timezone'),datetime.strptime(cat.created_on.strftime('%Y-%m-%d %H:%M:%S'),"%Y-%m-%d %H:%M:%S")) if cat.created_on else '-' for cat in catgories],
        })
        if not catgories:
            messages.success(request,'No Categories For Export')
            return redirect('events:event_category_list')
        return ConvertDataCSV(data,'categories_data')

class ExportEvents(View):
    def post(self,request,*args,**kwargs):
        events = Events.objects.all().order_by('-created_on').only('id')
        data = pd.DataFrame({
            "Title": [event.title if event.title else '--' for event in events],
            "Descrioption": [event.description if event.description else '-' for event in events],
            "Created on": [ConvertToLocalTimezone(request.POST.get('timezone'),datetime.strptime(event.created_on.strftime('%Y-%m-%d %H:%M:%S'),"%Y-%m-%d %H:%M:%S")) if event.created_on else '-' for event in events],
        })
        if not events:
            messages.success(request,'No Events For Export')
            return redirect('events:event_list')
        return ConvertDataCSV(data,'events_data')
