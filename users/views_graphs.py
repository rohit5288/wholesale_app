import calendar
from accounts.decorators import *
from accounts.utils import *
from django.http import JsonResponse
from calendar import monthrange, month_name
from accounts.common_imports import *



class UserGraph(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        data = {"data":[],'customers_count':[],'active_customers_count':[],'inactive_customers_count':[],'deleted_customers_count':[],'month_name':[]}
        selected_year = request.GET.get('year') if request.GET.get('year') else datetime.now().year
        selected_month = request.GET.get('month') if request.GET.get('month') else None
        if selected_month:
            days = [i for i in range(1,monthrange(int(selected_year), int(selected_month))[1]+1)]
            data['data'] = [day for day in days]
            data['customers_count']= [User.objects.filter(role_id=BUYER, created_on__month = selected_month,created_on__day = day,created_on__year = selected_year).count() for day in days]
            data['active_customers_count']=  [User.objects.filter(role_id=BUYER,created_on__month = selected_month,created_on__day = day,created_on__year = selected_year,status=ACTIVE).count() for day in days  ]
            data['inactive_customers_count']= [User.objects.filter(role_id=BUYER,created_on__month = selected_month,created_on__day = day,created_on__year = selected_year,status=INACTIVE).count() for day in days  ]
            data['deleted_customers_count']= [User.objects.filter(role_id=BUYER,created_on__month = selected_month,created_on__day = day,created_on__year = selected_year,status=DELETED).count() for day in days  ]
            data['month_name']=calendar.month_name[int(selected_month)]   
        else:
            data['data'] = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            data['customers_count']= [User.objects.filter(role_id=BUYER,created_on__month = i,created_on__year = selected_year,).count() for i in range(1,13)]
            data['active_customers_count'] = [User.objects.filter(role_id=BUYER,created_on__month=i,created_on__year=selected_year,status=ACTIVE).count() for i in range(1,13)  ]
            data['inactive_customers_count'] = [User.objects.filter(role_id=BUYER,created_on__month=i,created_on__year=selected_year,status=INACTIVE).count() for i in range(1,13)  ]
            data['deleted_customers_count'] = [User.objects.filter(role_id=BUYER,created_on__month=i,created_on__year=selected_year,status=DELETED).count() for i in range(1,13)  ]

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
                'max': 5 if max(data['customers_count']) <= 5 else max(data['customers_count'])+10,
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
                    'name': 'Users Registered',
                    'data': data['customers_count'],
                }, 
                {
                    'type': 'column',
                    'name': 'Active Users',
                    'data': data['active_customers_count'],
                }, 
                {
                    'type': 'column',
                    'name': 'Inactive Users',
                    'data': data['inactive_customers_count'],
                }, 
                {
                    'type': 'column',
                    'name': 'Deleted Users',
                    'data': data['deleted_customers_count'],
                }, 
              
            ],
            'accessibility': {
                'enabled': False
            },
        }

        data['users']=chart   
        data['selected_year']=selected_year
        return JsonResponse(data)


class UserAnalyticGraphdata(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        data={'Inactive':0,'Deleted':0,'Unverified':0}
        year=request.GET.get('year')
        month=request.GET.get('month')
        if not request.GET.get('month'):
            data['Inactive'] = User.objects.filter(created_on__year = year,status=INACTIVE,role_id=BUYER).count()
            data['Deleted'] =  User.objects.filter(created_on__year = year,status=DELETED,role_id=BUYER).count()
            data['Unverified'] = User.objects.filter(is_mobile_verified=False,created_on__year = year,status=ACTIVE,role_id=BUYER).count()
            data['Active'] = User.objects.filter(created_on__year = year,role_id=BUYER,status=ACTIVE).count()
            return JsonResponse(data)
        else:
            data['Inactive'] = User.objects.filter(created_on__year = year,status=INACTIVE,role_id=BUYER,created_on__month=month).count()
            data['Deleted'] =  User.objects.filter(created_on__year = year,status=DELETED,role_id=BUYER,created_on__month=month).count()
            data['Unverified'] = User.objects.filter(is_mobile_verified=False,created_on__year = year,status=ACTIVE,role_id=BUYER,created_on__month=month).count()
            data['Active'] = User.objects.filter(created_on__year = year,role_id=BUYER,status=ACTIVE,created_on__month=month).count()
        return JsonResponse(data)
        

class RevenueGraphWeekly(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        days = {'Sunday':'1','Monday':'2','Tuesday':'3','Wednesday':'4','Thursday':'5','Friday':'6','Saturday':'7'}
        revenue = []
        selected_year = str(request.GET.get('year')) if request.GET.get('year') else str(datetime.now().year)
        week_dates = GetWeekDates()

        for i in days.keys():
            amount = Transactions.objects.filter(
                status=True,
                created_on__week_day=days[i],
                created_on__date__in=week_dates,
                created_on__year=selected_year
                ).aggregate(Sum("amount",default=0))['amount__sum']
            
            revenue.append(
                round(amount,2)
            )
        
        chart = {
            'chart': {'type': 'bar'}, 
            'title': {'text': 'Earning for this week'},
            'xAxis': { 'categories': [i.upper() for i in days.keys()]},
            'colors': ["#36D1DC", "#5B86E5", "#f7a35c"],
            'series': [
                {
                    'name': 'Total Transactions ($)',
                    'data':revenue
                },
            ],
            'accessibility': {
                'enabled': False
            },
        }
        return JsonResponse({"chart":chart,"selected_year":selected_year},safe=False)


class RevenueGraph(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        months = {'jan':'1','feb':'2','mar':'3','apr':'4','may':'5','jun':'6','jul':'7','aug':'8','sep':'9','oct':'10','nov':'11','dec':'12'}
        revenue,subscription,boost_events,booking = [],[],[],[]
        selected_year = str(request.GET.get('year')) if request.GET.get('year') else str(datetime.now().year)
        selected_month = request.GET.get('month_year')
        if selected_month and selected_year:
            selected_month = int(selected_month)
            selected_year = int(selected_year)
            days = [i for i in range(1,monthrange(selected_year, selected_month)[1]+1)]  
            for day in days:
                amount = Transactions.objects.filter(
                    status=True,
                    created_on__date=datetime(year=selected_year, month=selected_month, day=int(day)),
                    ).aggregate(Sum("amount",default=0))['amount__sum']     
                subscription_amount = Transactions.objects.filter(
                    status=True,
                    type=SUBSCRIPTION_TRANS,
                    created_on__date=datetime(year=selected_year, month=selected_month, day=int(day)),
                    ).aggregate(Sum("amount",default=0))['amount__sum']
                booster_amount = Transactions.objects.filter(
                    status=True,
                    type=BOOST_EVENT_TRANS,
                    created_on__date=datetime(year=selected_year, month=selected_month, day=int(day)),
                    ).aggregate(Sum("amount",default=0))['amount__sum']  
                booking_amount = Transactions.objects.filter(
                    status=True,
                    type=BOOKING_TRANS,
                    created_on__date=datetime(year=selected_year, month=selected_month, day=int(day)),
                    ).aggregate(Sum("amount",default=0))['amount__sum']      
                revenue.append(round(amount,2))
                subscription.append(round(subscription_amount,2))
                boost_events.append(round(booster_amount,2))
                booking.append(round(booking_amount,2))
            formate_date = datetime(selected_year, selected_month, 1).strftime("%B %Y")
            chart = {
                'title': {
                    'text': f'Earning for {formate_date}'
                },
                'xAxis': { 
                    'categories': days,
                    'lineWidth': 0,
                    'crosshair': True
                },
                'yAxis': {
                    'align': 'left',
                    'x': 10,
                    'lineWidth': 0,
                    'gridLineWidth': 1,
                    'title': {
                        'enabled': False,
                    },
                },
                'tooltip': {
                'headerFormat': '<span style="font-size:10px">{point.key}</span><table>',
                'footerFormat': '</table>',
                # 'shared': True,
                'useHTML': True
            },
                'plotOptions': {
                'line': {
                    'dataLabels': {
                        'enabled': True
                    },
                    'enableMouseTracking': False
                    }
                },
                'colors': ["#36D1DC", "#5B86E5", "#f7a35c","#31a8f6"],
                'series': [
                    {
                        'type': 'spline',
                        'name': 'Total Transactions ($)',
                        'data': revenue,
                        'maxPointWidth': 40,
                    },
                    {
                        'name': 'Total Subscriptions ($)',
                        'data':subscription,
                        'type': 'column',
                    },
                    {
                        'name': 'Total Boosters ($)',
                        'data':boost_events,
                        'type': 'column',
                    },
                    {
                        'name': 'Total Bookings ($)',
                        'data':booking,
                        'type': 'column',
                    },
                ],
                'accessibility': {
                    'enabled': False
                },
            }
            return JsonResponse({"chart":chart,"selected_year":selected_year},safe=False)
        else:
            for i in months.keys():
                amount = Transactions.objects.filter(
                    status=True,
                    created_on__month= months[i],
                    created_on__year=selected_year,
                    ).aggregate(Sum("amount",default=0))['amount__sum']

                subscription_amount = Transactions.objects.filter(
                    status=True,
                    type=SUBSCRIPTION_TRANS,
                    created_on__month= months[i],
                    created_on__year=selected_year,
                    ).aggregate(Sum("amount",default=0))['amount__sum']
                booster_amount = Transactions.objects.filter(
                    status=True,
                    type=BOOST_EVENT_TRANS,
                    created_on__month= months[i],
                    created_on__year=selected_year,
                    ).aggregate(Sum("amount",default=0))['amount__sum']
                booking_amount = Transactions.objects.filter(
                    status=True,
                    type=BOOKING_TRANS,
                    created_on__month= months[i],
                    created_on__year=selected_year,
                    ).aggregate(Sum("amount",default=0))['amount__sum']     
                revenue.append(round(amount,2))
                subscription.append(round(subscription_amount,2))
                boost_events.append(round(booster_amount,2))
                booking.append(round(booking_amount,2))

            chart = {
                # 'chart': {'type': 'spline'}, 
                'title': {'text': f'Earning for {selected_year}'},
                'xAxis': { 'categories': [i.upper() for i in months.keys()]},
                'colors': ["#36D1DC", "#5B86E5", "#f7a35c","#31a8f6"],
                'series': [
                    {
                        'name': 'Total Transactions ($)',
                        'data':revenue,
                        'type': 'spline'
                        
                    },
                    {
                        'name': 'Total Subscriptions ($)',
                        'data':subscription,
                        'type': 'column',
                    },
                    {
                        'name': 'Total Boosters ($)',
                        'data':boost_events,
                        'type': 'column',
                    },
                    {
                        'name': 'Total Bookings ($)',
                        'data':booking,
                        'type': 'column',
                    },
                ],
                'accessibility': {
                    'enabled': False
                },
            }
            return JsonResponse({"chart":chart,"selected_year":selected_year},safe=False)



class TicketBookingGraph(View):
    @method_decorator(admin_only)
    def get(self,request,*args,**kwargs):
        months = {'jan':'1','feb':'2','mar':'3','apr':'4','may':'5','jun':'6','jul':'7','aug':'8','sep':'9','oct':'10','nov':'11','dec':'12'}
        booking,service_fee = [],[]
        selected_year = str(request.GET.get('year')) if request.GET.get('year') else str(datetime.now().year)
        selected_month = request.GET.get('month_year')
        if selected_month and selected_year:
            selected_month = int(selected_month)
            selected_year = int(selected_year)
            days = [i for i in range(1,monthrange(selected_year, selected_month)[1]+1)]  
            for day in days:
                booking_amount = Transactions.objects.filter(
                    status=True,
                    type=BOOKING_TRANS,
                    created_on__date=datetime(year=selected_year, month=selected_month, day=int(day)),
                    ).aggregate(Sum("amount",default=0))['amount__sum']    
                booking_service_fees = Transactions.objects.filter(
                    status=True,
                    type=BOOKING_TRANS,
                    created_on__date=datetime(year=selected_year, month=selected_month, day=int(day)),
                    ).aggregate(Sum("booking__service_fee",default=0))['booking__service_fee__sum']  
                booking.append(round(booking_amount,2))
                service_fee.append(round(booking_service_fees,2))
            formate_date = datetime(selected_year, selected_month, 1).strftime("%B %Y")
            chart = {
                'title': {
                    'text': f'Earning for {formate_date}'
                },
                'xAxis': { 
                    'categories': days,
                    'lineWidth': 0,
                    'crosshair': True
                },
                'yAxis': {
                    'align': 'left',
                    'x': 10,
                    'lineWidth': 0,
                    'gridLineWidth': 1,
                    'title': {
                        'enabled': False,
                    },
                },
                'tooltip': {
                'headerFormat': '<span style="font-size:10px">{point.key}</span><table>',
                'footerFormat': '</table>',
                # 'shared': True,
                'useHTML': True
            },
                'plotOptions': {
                'line': {
                    'dataLabels': {
                        'enabled': True
                    },
                    'enableMouseTracking': False
                    }
                },
                'colors': ["#36D1DC", "#5B86E5", "#f7a35c","#31a8f6"],
                'series': [
                    {
                        'type': 'spline',
                        'name': 'Total Bookings ($)',
                        'data': booking,
                        'maxPointWidth': 40,
                    },
                    {
                        'name': 'Service Fees ($)',
                        'data':service_fee,
                        'type': 'column',
                    },
                  
                ],
                'accessibility': {
                    'enabled': False
                },
            }
            return JsonResponse({"chart":chart,"selected_year":selected_year},safe=False)
        else:
            for i in months.keys():

                booking_amount = Transactions.objects.filter(
                    status=True,
                    type=BOOKING_TRANS,
                    created_on__month= months[i],
                    created_on__year=selected_year,
                    ).aggregate(Sum("amount",default=0))['amount__sum']    
                booking_service_fees = Transactions.objects.filter(
                    status=True,
                    type=BOOKING_TRANS,
                   created_on__month= months[i],
                    created_on__year=selected_year,
                    ).aggregate(Sum("booking__service_fee",default=0))['booking__service_fee__sum']  
                booking.append(round(booking_amount,2))
                service_fee.append(round(booking_service_fees,2))

            chart = {
                # 'chart': {'type': 'spline'}, 
                'title': {'text': f'Bookings Earning for {selected_year}'},
                'xAxis': { 'categories': [i.upper() for i in months.keys()]},
                'colors': ["#36D1DC", "#5B86E5", "#f7a35c","#31a8f6"],
                'series': [
                    {
                        'type': 'spline',
                        'name': 'Total Bookings ($)',
                        'data': booking,
                        'maxPointWidth': 40,
                    },
                    {
                        'name': 'Service Fees ($)',
                        'data':service_fee,
                        'type': 'column',
                    },
                  
                ],
                'accessibility': {
                    'enabled': False
                },
            }
            return JsonResponse({"chart":chart,"selected_year":selected_year},safe=False)