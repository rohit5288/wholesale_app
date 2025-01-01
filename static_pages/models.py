from django.utils.html import strip_tags
from ckeditor_uploader.fields import RichTextUploadingField
from accounts.models import *
from accounts.constants import *


class Pages(CommonInfo):
    title = models.CharField(max_length=255,blank=True, null=True)
    content = RichTextUploadingField()
    type_id = models.PositiveIntegerField(choices=PAGE_TYPE)
    is_active = models.BooleanField(default=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['content'] = strip_tags(instance.content)
        return data

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'static_pages'


class FAQs(CommonInfo):
    question = models.CharField(max_length=255,null=True,blank=True)
    answer = models.TextField(null=True,blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'faqs'
