import csv
import time
from accounts.views import *
from accounts.common_imports import *
from io import BytesIO
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


'''
Downloads Buyer Report
'''
class DownLoadBuyerReports(View):
    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        role = BUYER if int(request.GET.get('role_id')) == 2 else SELLER
        file_name = 'customer_data' if int(request.GET.get('role_id')) == 2 else 'seller_data'
        users = User.objects.filter(role_id=role).order_by('-created_on').only('id')
        status =[]
        for user in users:
            if user.status == ACTIVE:
                status.append('Active')
            elif user.status == INACTIVE:
                status.append('Inactive')
            elif user.status == DELETED:
                status.append('Deleted')
            else:
                status.append('--')
        data = pd.DataFrame({
            "Full Name": [user.full_name if user.full_name else '--' for user in users],
            "Email": [user.email if user.email else '-' for user in users],
            "Mobile No": [str(user.country_code)+str(user.mobile_no) if user.mobile_no else '-' for user in users],
            "Created on": [ConvertToLocalTimezone(request.POST.get('timezone'),datetime.strptime(user.created_on.strftime('%Y-%m-%d %H:%M:%S'),"%Y-%m-%d %H:%M:%S")) if user.created_on else '-' for user in users],
            "User Status": status
        })
        if not users:
            messages.success(request,'No Buyers For Export')
            return redirect('users:customers_list')
        return ConvertDataCSV(data,file_name)
        



