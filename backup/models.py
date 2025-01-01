import uuid
from django.db import models


class Backup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=True, blank=True,max_length=255)
    size = models.CharField(null=True, blank=True,max_length=255)
    backup_file = models.FileField(upload_to='backup_files/',null=True, blank=True, max_length=2000)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_schema = models.BooleanField(default=False)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'tbl_db_backup'
