from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as auth_views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from uniphoto import views as uniphoto_views


urlpatterns = [
  path('registration', uniphoto_views.UserRegistration.as_view()),
  path('api-token-auth', auth_views.obtain_auth_token),
  path('user-details', uniphoto_views.UserDetails.as_view()),
  path('trial-license-check', uniphoto_views.TrialLicenseCheck.as_view()),
  path('user-files', uniphoto_views.UserFilesList.as_view()),
  path('all-files', uniphoto_views.AllFilesList.as_view()),
  path('post-file', uniphoto_views.PostFile.as_view()),
  path('delete-file/<int:pk>', uniphoto_views.DeleteFile.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = format_suffix_patterns(urlpatterns)