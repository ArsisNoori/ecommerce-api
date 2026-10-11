from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenBlacklistView, TokenObtainPairView, TokenRefreshView
)
from . import views
router = SimpleRouter()
router.register('addresses', views.AddressViewSet, basename='addresses')

app_name = 'accounts'

urlpatterns = [
    path('', include(router.urls)),
    path('', include(router.urls)),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', TokenBlacklistView.as_view(), name='logout'),
    path('auth/me/', views.MeView.as_view(), name='me'),
    path('auth/change_password/', views.ChangePasswordView.as_view(), name='change_password'),
]