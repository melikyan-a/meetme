from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from users import api as users_api


router = DefaultRouter()
router.register(r'', users_api.EAViewSet, base_name='event_and_activity')
router.register(r'', users_api.UserRelationViewSet, base_name='user_rel')


urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('social_django.urls', namespace='social')),
    path('register-by-token/<backend>/', users_api.register_by_access_token, name='register_by_access_token'),
    path('api-token-auth/', users_api.CustomAuthToken.as_view()),
    path('change-password/', users_api.ChangePasswordView.as_view()),
    path('user-profile/', users_api.MeetUserProfile.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

