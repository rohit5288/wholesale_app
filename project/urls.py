from django.contrib import admin
from frontend.views import *
from accounts.views import  *
from django.conf import settings
from django.urls import include, re_path
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import  AdminLoginView
from django.views.static import serve

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg.generators import OpenAPISchemaGenerator


class SchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super(SchemaGenerator, self).get_schema(request, public)
        schema.basePath = os.path.join(schema.basePath, '')
        schema.schemes = ["http", "https"]
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title = "<ProjectName>'s API's",
        description = "API documentation for <ProjectName> Project",
        default_version = "1.0.0",
        terms_of_service = env('BASE_URL')+"/terms-and-conditions/",
        contact = openapi.Contact(email=""),
        license = openapi.License(name="<ProjectName>"),
    ),
    public = True,
    permission_classes = (permissions.AllowAny,),
    generator_class = SchemaGenerator
)



urlpatterns = [
    re_path(r'^admin/login/', AdminLoginView.as_view()),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'',include('frontend.urls')),

    ## Documentation Swagger
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^documentation/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    re_path(r'^accounts/', include('accounts.urls',)),
    re_path(r'^api/', include('api.urls',)),
    re_path(r'^accounts/', include('django.contrib.auth.urls')),
    re_path(r'^logger/', include('logger.urls',)),
    re_path(r'^users/', include('users.urls',)),
    re_path(r'^static-pages/', include('static_pages.urls',)),
    re_path(r'^backup/', include('backup.urls',)),
    re_path(r'^contact-us/', include('contact_us.urls',)),
    re_path(r'^credentials/', include('credentials.urls',)),
    re_path(r'^sellers/', include('sellers.urls',)),
    # re_path(r'^chat/', include('chat.urls',)),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 
]

if settings.DEBUG is False:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

handler404 = 'frontend.views.handler404'
handler500 = 'frontend.views.handler500'
handler403 = 'frontend.views.handler403'
handler400 = 'frontend.views.handler400'