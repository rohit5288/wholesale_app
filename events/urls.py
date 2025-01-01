import os
import environ
from django.contrib import admin
from django.urls import re_path
from .views_api import *
from .views_exports import *
from .views import *
env = environ.Env()
environ.Env.read_env()

admin.autodiscover()
app_name = 'events'


urlpatterns = [
    ## Category Management Admin Panel
    re_path(r'^categories-listing/$',CategoriesListing.as_view(),name="event_category_list"),
    re_path(r'^add-default-categories/$',AddDefaultCategory.as_view(),name="add_default_categories"),
    re_path(r'^view-category/(?P<id>[-\w]+)/$',ViewCategory.as_view(),name="view_category"),
    re_path(r'^update-category/$',UpdateCategory.as_view(),name="update_category"),
    re_path(r'^delete-category/(?P<id>[-\w]+)/$',DeleteCategory.as_view(),name="delete_category"),
    re_path(r'^import-categories-data/$',ImportCategoriesdata.as_view(),name="import_categories_data"),

    #Export data Admin Panel
    re_path(r'^export-categories-data/$',ExportCategories.as_view(),name="export_categories_data"),
    re_path(r'^export-events-data/$',ExportEvents.as_view(),name="export_events_data"),
    
    ## Events Management Admin Panel
    re_path(r'^events-listing/$',EventsListing.as_view(),name="event_list"),
    re_path(r'^view-event/(?P<id>[-\w]+)/$',ViewEventDetails.as_view(),name="view_event_details"),
    re_path(r'^event-ratings/(?P<id>[-\w]+)/$',RatingandReviewsList.as_view(),name="event_ratings"),
    re_path(r'^deactivate-event/(?P<id>[-\w]+)/$',InactivateEvent.as_view(), name='inactivate_event'),
    re_path(r'^activate-vent/(?P<id>[-\w]+)/$',ActivateEvent.as_view(), name='activate_event'),
    re_path(r'^delete-event/(?P<id>[-\w]+)/$',DeleteEvent.as_view(), name='delete_event'),
    
    
    ## Bookings Management Admin Panel
    re_path(r'^bookings-listing/$',BookingsListing.as_view(),name="bookings_list"),
    re_path(r'^view-booking/(?P<id>[-\w]+)/$',ViewBookingDetails.as_view(),name="view_booking"),

    #Transactions Management Admin Panel
    re_path(r'^subscription-transaction-listing/$',SubscriptionTransactionsList.as_view(),name="subscription_transaction_list"),
    re_path(r'^booking-transaction-listing/$',EventBookingTransactionsList.as_view(),name="booking_transaction_list"),
    re_path(r'^booster-transaction-listing/$',BoosterTransactionsList.as_view(),name="booster_transaction_list"),
    re_path(r'^transaction-details/(?P<id>[-\w]+)/$', TransactionDetail.as_view(), name='transaction_detail'),
    
    ## Events 
    re_path(r'^list-events/$',EventsListAPI.as_view(),name="events_list_api"),
    re_path(r'^popular-events/$',PopularEventsAPI.as_view(),name="popular_events_api"),
    re_path(r'^recently-viewed-events/$',RecentlyViewedEventsAPI.as_view(),name="recently_viewed_events_api"),
    re_path(r'^event-details/$',EventsDetailsAPI.as_view(),name="event_details_api"),
    re_path(r'^get-tickets/$',GetTicketsAPI.as_view(),name="get_tickets_api"),
    re_path(r'^make-booking-payment/$',MakeBookingPayment.as_view(),name="make_booking_payment_api"),
    
    ## Bookings APIs
    re_path(r'^my-bookings/$',MyBookingsAPI.as_view(),name="my_bookings_api"),
    re_path(r'^bookings-tickets-list/$',BookingTicketsAPI.as_view(),name="booking_tickets_api"),
    re_path(r'^ticket-details/$',TicketDetailsAPI.as_view(),name="ticket_details_api"),
    

    ##Events Category
    re_path(r'^category-list/$',CategoryListingAPI.as_view(),name="category_list_api"),
    re_path(r'^interested-category-list/$',InterestedCategoryListingAPI.as_view(),name="interested_category_list_api"),
    re_path(r'^mark-unmark-interested-category/$',MarkUnmarkInterestedCategoryAPI.as_view(),name="mark_unmark_interested_category"),
    
    ## Rating & Reviews
    re_path(r'^event-rating-list/$',EventRatingReviewListingAPI.as_view(),name="event_rating_list_api"),
    re_path(r'^rate-event/$',EventRatingReviewAPI.as_view(),name="rate_event_api"),
    re_path(r'^delete-review/$',DeleteRatingReviewAPI.as_view(),name="delete_review_api"),
    
    ## Favourite event management
    re_path(r'^favourites-list/$',FavouriteEventListingAPI.as_view(),name="event_rating_list_api"),
    re_path(r'^mark-unmark-favourite/$',MarkUnmarkFavouriteEventAPI.as_view(),name="mark_unmark_favourite"),

    ##Event History
    re_path(r'^events-history/$',EventsHistory.as_view(),name="events_history_api"),

]