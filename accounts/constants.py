USE_HTTPS = False
DEFAULT_TIMEZONE='Asia/Kolkata'
DEFAULT_SEARCH_RADIUS_KM=20
TEMP_OTP = 1234
MAX_ACTIVE_BANNER = 5
SHOW_MORE_COUNT = 5
DEFAULT_SERVICE_FEES = 5

"""
User role type name
"""
USER_ROLE = ((1, "Admin"),(2, "Buyer"),(3, "Seller"))
ADMIN = 1
BUYER = 2
SELLER = 3


"""
Event Type
"""
EVENT_TYPE = ((1, "Physical"),(2, "Virtual"))
PHYSICAL = 1
VIRTUAL = 2

"""
Ticket Type
"""
TICKET_TYPE = ((1, "Free"),(2, "Paid"),(3,'Rsvp'),(4,'Donation'))
FREE = 1
PAID = 2
RSVP = 3
DONATION = 4

"""
Event Status 
"""
EVENT_STATUS = ((1, "Active"),(2,"Inactive"),(3,"Deleted"))
ACTIVE = 1
INACTIVE = 2
DELETED = 3

"""
Blog Status 
"""
BLOG_STATUS = ((1, "Active"),(2,"Inactive"))
ACTIVE_BLOG = 1
INACTIVE_BLOG = 2

"""
User Status 
"""
USER_STATUS = ((1, "Active"),(2,"Inactive"),(3,"Deleted"))
ACTIVE = 1
INACTIVE = 2
DELETED = 3

"""
GENDER
"""
GENDER = ((1, 'Male'),(2,'Female'),(3,'Other'))
MALE = 1
FEMALE = 2
OTHER= 3

"""
Device
"""
DEVICE_TYPE  = ((1,"Android"),(2,"IOS"))
ANDROID = 1
IOS = 2

"""
PAGE SIZE
"""
PAGE_SIZE = 15
API_PAGINATION = 10


"""
PLAN_VALIDITY
"""
PLAN_VALIDITY = ((1,'Monthly'),(2,'Yearly'))
MONTHLY_PLAN = 1
YEARLY_PLAN = 2

"""
PLAN_STATUS
"""
PLAN_STATUS = ((1,'Active_Plan'),(2,'Expired_Plan'),(3,'Cancelled_Plan'))
ACTIVE_PLAN = 1
EXPIRED_PLAN = 2
CANCELLED_PLAN = 3

"""
PAYMENT_STATUS
"""
PAYMENT_STATUS = ((1,'Success'),(2,'Failure'))
PAYMENT_SUCCESS = 1
PAYMENT_FAILURE = 2


"""
LOGIN_STATE
"""
LOGIN_STATE = ((1,'Login Success'),(2,'Login Failure'))
LOGIN_SUCCESS = 1
LOGIN_FAILURE = 2

"""
Page Type
"""
PAGE_TYPE =  ((1,"Terms_And_Condition"),(2,"Privacy_Policy"),(3, "About_Us"),(4, "How_it_works"),(5, "Cookie_Policy"))
TERMS_AND_CONDITION = 1
PRIVACY_POLICY = 2
ABOUT_US = 3
HOW_IT_WORKS = 4
COOKIE_POLICY = 5

"""
SOCIAL TYPE
"""
SOCIAL_TYPE = ((1,'Google'),(2,'Facebook'),(6,'Others'))
GOOGLE = 1
FACEBOOK = 2
APPLE = 3
INSTAGRAM = 4
LINKEDIN = 5
OTHERS = 6



NOTIFICATION_TYPE = ((1,'New Event Posted'),(2,'New Blog Posted'),(3,'Admin Notification'))
NEW_EVENT_POSTED = 1
NEW_BLOG_POSTED = 2
ADMIN_NOTIFICATION=3

'''
Transactions Type
'''
TRANSACTIONS_TYPE = ((1,'Subscription Plan'),(2,'Event Boost'),(3,'Event Booking'))
SUBSCRIPTION_TRANS = 1
BOOST_EVENT_TRANS = 2
BOOKING_TRANS=3


'''
Job amount type
'''
JOB_AMOUNT_TYPE = ((1,'Amount_hourly'),(2,'Amount_daily'))
AMOUNT_HOURLY = 1
AMOUNT_DAILY = 2


"""
User Activities Type
"""
USER_ACTIVITY_TYPE = ((1,'Event_Activity'),)
EVENT_ACTIVITY=1