from accounts.utils import get_pagination
from .models import *
from accounts.common_imports import *
import time


"""
Back Up Management
"""


class BackupsList(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        records = Backup.objects.all().order_by('-created_on').only('id')
        if request.GET.get('name'):
            records = records.filter(name__icontains =request.GET.get('name'))
        if request.GET.get('database_type'):
            records = records.filter(is_schema = request.GET.get('database_type'))
        if request.GET.get('created_on'):
            records = records.filter(created_on__date =request.GET.get('created_on'))
        if request.GET and not records:
            messages.error(request, 'No Data Found')
        return render(request, 'backup/backup.html',{
            "records":get_pagination(request,records),
            "head_title":"Backup Management",
            "name":request.GET.get('name',''),
            'database_type' : request.GET.get("database_type"),
            "created_on":request.GET.get('created_on',""),
        })
	

class CreateDBBackup(View):
	@method_decorator(admin_only)
	def get(self, request, *args, **kwargs):
		database = env('DB_NAME')
		path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
		if not os.path.exists(f"{path}/media/backup_files"):
			os.makedirs(f"{path}/media/backup_files")
		name = database + time.strftime('%Y%m%d-%H%M%S') + ".sql"
		file_path = f'{path}/media/backup_files/' + name
		os.system("mysqldump -h " + env('DB_HOST') + " -u " + env('DB_USER') + " -p" + env('DB_PASSWORD') + " " + database + " > " + file_path)
		Backup.objects.create(
			name = name,
			size = os.path.getsize(file_path),
			is_schema = False,
			backup_file = 'backup_files/'+name
		)
		messages.success(request, 'Database backup created successfully!')
		return redirect('backup:backup')

class CreateDBSchema(View):
	@method_decorator(admin_only)
	def get(self, request, *args, **kwargs):
		database = env('DB_NAME')
		path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
		if not os.path.exists(f"{path}/media/backup_files"):
			os.makedirs(f"{path}/media/backup_files")
		name = database + time.strftime('%Y%m%d-%H%M%S') + ".json"
		file_path = f'{path}/media/backup_files/' + name
		os.system("mysqldump -h " + env('DB_HOST') + " -u " + env('DB_USER') + " -p" + env('DB_PASSWORD') + " --no-data " + database + " > " + file_path)
		Backup.objects.create(
			name = name,
			size = os.path.getsize(file_path),
			is_schema = True,
			backup_file = 'backup_files/'+name
		)
		messages.success(request, 'Database structure created successfully!')
		return redirect('backup:backup')


class DeleteBackup(View):
    @method_decorator(admin_only)
    def get(self, request, *args, **kwargs):
        Backup.objects.get(id=self.kwargs['id']).delete()
        messages.error(request, 'File deleted successfully!')
        return redirect('backup:backup')


