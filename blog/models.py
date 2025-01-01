from django.db import models
from accounts.models import *


class BlogImages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image=models.ImageField(upload_to='blog-images/',null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    class Meta:
        managed=True
        db_table='tbl_blog_images'


class Blogs(CommonInfo):
    title=models.CharField(max_length=255,null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    images=models.ManyToManyField(BlogImages)
    status =  models.PositiveIntegerField(default=ACTIVE_BLOG,choices=BLOG_STATUS)

    class Meta:
        managed=True
        db_table='tbl_blogs'
