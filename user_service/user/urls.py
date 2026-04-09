
from django.contrib import admin
from django.urls import path
from user.userApp.views import RegisterView, get_user_data, internal_user_detail, my_profile, update_profile, profile_detail, list_profiles
from rest_framework_simplejwt.views import TokenRefreshView
from user.userApp.views import CustomTokenObtainPairView


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/register/', RegisterView.as_view()),
    path('api/login/', CustomTokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),

    path('api/me/', get_user_data),
    path('internal/users/<uuid:user_id>/', internal_user_detail),
    
    path('api/profile/me/', my_profile),
    path('profile/me/update/', update_profile, name='update-profile'),
    path('profile/other/<uuid:profile_id>/', profile_detail, name='profile-detail'),
    path('profile/all/', list_profiles, name='list-profiles'),
]
