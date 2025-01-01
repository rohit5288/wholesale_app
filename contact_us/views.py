from .models import *
from accounts.views import *


class ContactUsList(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        contacts = ContactUs.objects.all().order_by('-created_on')
        if request.GET.get('full_name'):
            contacts = contacts.filter(full_name__icontains = request.GET.get('full_name').strip())
        if request.GET.get('email'):
            contacts = contacts.filter(email__icontains = request.GET.get('email').strip())
        if request.GET.get('message'):
            contacts = contacts.filter(message__icontains = request.GET.get('message').strip())
        if request.GET.get('created_on'):
            contacts = contacts.filter(created_on__date = request.GET.get('created_on'))
        if request.GET and not contacts:
            messages.error(request, 'No Data Found')
        return render(request, 'contactus/contactus-list.html',{
            "head_title":"Contact Us Management",
            "contacts":get_pagination(request,contacts),
            "full_name":request.GET.get('full_name',''),
            "email":request.GET.get('email',''),
            "message":request.GET.get('message',''),
            "created_on":request.GET.get('created_on',''),
            "contact_details":ContactDetails.objects.last()
        })


class ViewContactUsDetails(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        contact = ContactUs.objects.get(id=self.kwargs['id'])
        replies = ContactUsReply.objects.filter(contact=contact).order_by('-created_on')
        return render(request, 'contactus/view-contactus.html',{"head_title":"Contact Us Management","contact":contact,"replies":replies})
        
    
class ContactUsReplyView(View):
    @method_decorator(admin_only)
    def post(self, request, *args, **kwargs):
        contact = ContactUs.objects.get(id=request.POST.get('id'))
        reply = ContactUsReply.objects.create(
            contact = contact,
            reply_message = request.POST.get('reply_message'),
            created_by = request.user
        )
        BulkSendUserEmail(request,'','EmailTemplates/contactus-reply.html','Contact Us Revert',contact.email,contact.message,reply.reply_message,'Contact Us Revert','')
        messages.success(request,"Reply sent successfully!")
        return redirect('contact_us:view_contact',id=contact.id)
    

class DeleteContactUs(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        ContactUs.objects.get(id=self.kwargs['id']).delete()
        messages.success(request,"Contact Deleted Successfully!")   
        return redirect('contact_us:contactus_list')
        
    
class ContactUsView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('frontend:index')
        return render(request, 'contactus/contact-us.html',{"contact_details":ContactDetails.objects.last()})
        
    def post(self, request, *args, **kwargs):
        ContactUs.objects.create(
            full_name = request.POST.get('full_name'),
            email = request.POST.get('email'),
            subject = request.POST.get('subject'),
            message = request.POST.get('message')
        )
        messages.success(request,"Thank you for contacting us. We will get back to you shortly!")
        return redirect('contact_us:view_contact',id=request.user.id)
    

class UpdateContactDetails(View):
    def get(self, request):
        return render(request, 'contactus/admin-contact-details.html',{
            "contact_details":ContactDetails.objects.last(),
            "head_title":"Contact Us Management",
        })
    
    def post(self, request):
        contact_details = ContactDetails.objects.last()
        if not contact_details:
            contact_details = ContactDetails.objects.create(created_by=request.user)
        if request.POST.get('email'):
            contact_details.email = request.POST.get('email')
        if request.POST.get('address'):
            contact_details.address = request.POST.get('address')
            contact_details.latitude = request.POST.get('latitude')
            contact_details.longitude = request.POST.get('longitude')
        if request.POST.get('mobile_no'):
            contact_details.mobile_no = request.POST.get('mobile_no')
            contact_details.country_code = request.POST.get('country_code')
            contact_details.country_iso_code = request.POST.get('country_iso_code')
        contact_details.save()
        messages.success(request,'Contact details updated successfully!')
        return redirect('contact_us:update_contact_details')
    
class UpdateSocialLinks(View):
    def post(self, request, *args, **kwargs):
        try:
            contact_details = ContactDetails.objects.last()
        except:
            contact_details=ContactDetails.objects.create()
        if request.POST.get('facebook'):
            contact_details.facebook_url = request.POST.get('facebook')
        if request.POST.get('twitter'):
            contact_details.twitter_url = request.POST.get('twitter')
        if request.POST.get('google'):
            contact_details.google_url = request.POST.get('google')
        contact_details.save()
        messages.success(request,"Social Links Updated")
        return redirect('contact_us:update_contact_details')

class ClearSocialLinks(View):
    def get(self, request, *args, **kwargs):
        try:
            contact_details = ContactDetails.objects.last()
        except:
            contact_details=ContactDetails.objects.create()
        contact_details.facebook_url = None
        contact_details.twitter_url = None
        contact_details.google_url = None
        contact_details.save()
        messages.success(request,"Social Links Cleared Successfully")
        return redirect('contact_us:update_contact_details')
    
class ClearAdminDetails(View):
    def get(self, request, *args, **kwargs):
        try:
            contact_details = ContactDetails.objects.last()
        except:
            contact_details=ContactDetails.objects.create()
        contact_details.email = None
        contact_details.country_code = None
        contact_details.country_iso_code = None
        contact_details.mobile_no = None
        contact_details.address = None
        contact_details.latitude = None
        contact_details.longitude = None
        contact_details.save()
        messages.success(request,"Admin Details Cleared Successfully")
        return redirect('contact_us:update_contact_details')