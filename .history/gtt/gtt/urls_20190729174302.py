from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
import notifications.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path(settings.API + 'oauth2/', include('rest_framework_social_oauth2.urls')),
    path('', include(('posts.urls', 'posts'), namespace='posts')),
    path('', include(('users.urls', 'users'), namespace='users')),
    path(settings.API + 'inbox/notifications', include(notifications.urls, namespace='notifications')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
