import calendar
from accounts.common_imports import *
from calendar import monthrange, month_name

class SellerList(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        users = User.objects.filter(role_id=SELLER).order_by('-created_on').only('id')
        if request.GET.get('username'):
            users = users.filter(username__icontains = request.GET.get('username').strip())
        if request.GET.get('full_name'):
            users = users.filter(full_name__icontains = request.GET.get('full_name').strip())
        if request.GET.get('email'):
            users = users.filter(email__icontains = request.GET.get('email').strip())
        if request.GET.get('mobile_no'):
            users = users.filter(id__in=[i.id for i in users if request.GET.get('mobile_no').strip() in str(i.country_code)+str(i.mobile_no)])
        if request.GET.get('created_on_from'):
            users = users.filter(created_on__date__gte = request.GET.get('created_on_from'))
        if request.GET.get('created_on_to'):
            users = users.filter(created_on__date__lte = request.GET.get('created_on_to'))
        if request.GET.get('status'):
            users = users.filter(status=request.GET.get('status'))
        if request.GET and not users:
            messages.error(request, 'No Data Found!')
        return render(request,'users/sellers/sellers.html',{
            "head_title":'Sellers Management',
            "users" : get_pagination(request, users),
            "full_name":request.GET.get('full_name') if request.GET.get('full_name') else "",
            "username":request.GET.get('username') if request.GET.get('username') else "",
            "email":request.GET.get('email') if request.GET.get('email') else "",
            "mobile_no":request.GET.get('mobile_no') if request.GET.get('mobile_no') else "",
            "created_on_from":request.GET.get('created_on_from') if request.GET.get('created_on_from') else "",
            "created_on_to":request.GET.get('created_on_to') if request.GET.get('created_on_to') else "",
            "status":request.GET.get('status') if request.GET.get('status') else "",
            "scroll_required":True if request.GET else False,

        })
    

class SellersGraph(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        data = {"data":[],'Sellers_count':[],'active_Sellers_count':[],'inactive_Sellers_count':[],'deleted_Sellers_count':[],'month_name':[]}
        selected_year = request.GET.get('year') if request.GET.get('year') else datetime.now().year
        selected_month = request.GET.get('month') if request.GET.get('month') else None
        if selected_month:
            days = [i for i in range(1,monthrange(int(selected_year), int(selected_month))[1]+1)]
            data['data'] = [day for day in days]
            data['Sellers_count']= [User.objects.filter(role_id=SELLER, created_on__month = selected_month,created_on__day = day,created_on__year = selected_year).count() for day in days]
            data['active_Sellers_count']=  [User.objects.filter(role_id=SELLER,created_on__month = selected_month,created_on__day = day,created_on__year = selected_year,status=ACTIVE).count() for day in days  ]
            data['inactive_Sellers_count']= [User.objects.filter(role_id=SELLER,created_on__month = selected_month,created_on__day = day,created_on__year = selected_year,status=INACTIVE).count() for day in days  ]
            data['deleted_Sellers_count']= [User.objects.filter(role_id=SELLER,created_on__month = selected_month,created_on__day = day,created_on__year = selected_year,status=DELETED).count() for day in days  ]
            data['month_name']=calendar.month_name[int(selected_month)]   
        else:
            data['data'] = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            data['Sellers_count']= [User.objects.filter(role_id=SELLER,created_on__month = i,created_on__year = selected_year,).count() for i in range(1,13)]
            data['active_Sellers_count'] = [User.objects.filter(role_id=SELLER,created_on__month=i,created_on__year=selected_year,status=ACTIVE).count() for i in range(1,13)  ]
            data['inactive_Sellers_count'] = [User.objects.filter(role_id=SELLER,created_on__month=i,created_on__year=selected_year,status=INACTIVE).count() for i in range(1,13)  ]
            data['deleted_Sellers_count'] = [User.objects.filter(role_id=SELLER,created_on__month=i,created_on__year=selected_year,status=DELETED).count() for i in range(1,13)  ]

        chart = {
            'title': {
                'text': ''
            },
            'xAxis': { 
                'categories': data['data'],
                'lineWidth': 0,
            },
            'yAxis': {
                'min': 0,
                'max': 5 if max(data['Sellers_count']) <= 5 else max(data['Sellers_count'])+10,
                'allowDecimals': False,
                'align': 'left',
                'x': 10,
                'lineWidth': 0,
                'gridLineWidth': 1,
                'title': {
                    'enabled': False,
                },
            },    
            'colors': ["#407BFF","#229b09","#ffc107","#e80303"],
            'series': [
                {
                    'type': 'spline',
                    'name': 'Sellers Registered',
                    'data': data['Sellers_count'],
                }, 
                {
                    'type': 'column',
                    'name': 'Active Sellers',
                    'data': data['active_Sellers_count'],
                }, 
                {
                    'type': 'column',
                    'name': 'Inactive Sellers',
                    'data': data['inactive_Sellers_count'],
                }, 
                {
                    'type': 'column',
                    'name': 'Deleted Sellers',
                    'data': data['deleted_Sellers_count'],
                }, 
              
            ],
            'accessibility': {
                'enabled': False
            },
        }

        data['users']=chart   
        data['selected_year']=selected_year
        return JsonResponse(data)
    
