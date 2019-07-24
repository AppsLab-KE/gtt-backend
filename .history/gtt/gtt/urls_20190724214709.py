from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path(settings.API + 'oauth/', include('rest_framework_social_oauth2.urls')),
    path('', include(('posts.urls', 'post'), namespace='posts')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)