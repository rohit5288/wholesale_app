from django import template
from accounts.views import *
from events.models import *
from contact_us.models import *
register = template.Library()
import environ
env = environ.Env()
environ.Env.read_env()


@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()


@register.simple_tag
def order_by(queryset,field):
	'''
		Order by QuerySet in template
	'''
	try:
		return queryset.order_by(field)
	except Exception as e:
		print(e)
		return queryset
	
@register.filter(name='total_customers')
def total_customers(key):
	return User.objects.filter(role_id=BUYER).count()

@register.filter(name='notifications_list')
def notifications_list(key):
	admin = User.objects.get(is_superuser=True, role_id=ADMIN)
	return Notifications.objects.filter(created_for=admin, is_read=False).order_by('-created_on')

@register.filter(name="unread_notifications_count")
def unread_notifications_count(request):
	if 'n_id' in request.GET.keys():
		try:
			Notifications.objects.filter(id=request.GET['n_id']).update(is_read=True)
		except:
			pass
	admin = User.objects.get(is_superuser=True, role_id=ADMIN)
	return Notifications.objects.filter(created_for=admin, is_read=False).count()


#Dashboard template tags start
@register.filter(name='users_count')
def users_count(key):
	count=0
	if key=='active_user':
		count=User.objects.filter(role_id=BUYER,status=ACTIVE).count()
	elif key=='inactive_user':
		count=User.objects.filter(role_id=BUYER,status=INACTIVE).count()
	elif key=='deleted_user':
		count=User.objects.filter(role_id=BUYER,status=DELETED).count()
	elif key=='total_user':
		count=User.objects.filter(role_id=BUYER).count()
	return count

@register.filter(name='sellers_count')
def sellers_count(key):
	count=0
	if key=='active_user':
		count=User.objects.filter(role_id=SELLER,status=ACTIVE).count()
	elif key=='inactive_user':
		count=User.objects.filter(role_id=SELLER,status=INACTIVE).count()
	elif key=='deleted_user':
		count=User.objects.filter(role_id=SELLER,status=DELETED).count()
	elif key=='total_user':
		count=User.objects.filter(role_id=SELLER).count()
	return count


@register.filter(name='events_count')
def events_count(key):
	events_count = 0
	if key == 'total_events':
		events_count = Events.objects.all().count()
	if key == 'active_events':
		events_count = Events.objects.filter(status=ACTIVE).count()
	if key == 'completed_events':
		events_count = Events.objects.filter(created_on__lt = datetime.now()).count()
	return events_count

@register.filter(name='contact_us_count')
def contact_us_count(key):
	contact_us_count = ContactUs.objects.all().count()	
	return contact_us_count

@register.filter(name='dashboard_data')
def dashboard_data(key):
	if key == "customers_today":
		return User.objects.filter(created_on__date=datetime.now().date()).exclude(role_id=ADMIN)[0:3]
	if key == "card_today":
		return 0

@register.filter(name='total_revenue')
def total_revenue(key):
	transactions = Transactions.objects.filter(status=True).order_by('-created_on').only('id')
	subscription_revenue = transactions.filter(type = SUBSCRIPTION_TRANS).aggregate(Sum("amount",default=0))['amount__sum']
	booster_revenue = transactions.filter(type = BOOST_EVENT_TRANS).aggregate(Sum("amount",default=0))['amount__sum']
	booking_service_fee = Transactions.objects.filter(type=BOOKING_TRANS).aggregate(Sum("booking__service_fee",default=0))['booking__service_fee__sum']
	admin_revenue = subscription_revenue + booster_revenue + booking_service_fee
	return admin_revenue
#Dashboard template tags end

@register.filter(name='today_date')
def today_date(key):
	return datetime.now()


@register.simple_tag
def date_format(key):
	date= str(key)
	return datetime.strptime(date, '%Y-%m-%d')

@register.filter(name='notifications')
def notifications(user):
	return Notifications.objects.filter(created_for=user,is_read=False).order_by('-created_on')[0:5]

@register.filter(name='notification_count')
def notification_count(user):
	return Notifications.objects.filter(created_for=user,is_read=False).count()

@register.filter(name='unread_notifications')
def unread_notifications(key):
	return Notifications.objects.filter(created_for_id=key).order_by('-id')[0:5]


@register.filter(name='project_logo')
def project_logo(key):
	project_logo = ProjectLogo.objects.all().last()
	if project_logo:
		if key==1:
			data = project_logo.logo.url if project_logo.logo else None
		if key==2:
			data  = project_logo.favicon.url if project_logo.favicon else None
	else:
		data=None
	return data