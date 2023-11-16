from django.urls import include, path
from taskmangement.users.api.views import (
    OrganizationViewSet,
    UserLogin, 
    UserLogout, 
    UserRegister,
    UserChangePassword,
    UserViewSet,
    
)
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path("register", UserRegister.as_view()),
    path("login", UserLogin.as_view()),
    path("logout",UserLogout.as_view()),
    path("change_password", UserChangePassword.as_view()),
    path("password_reset/", include("django_rest_passwordreset.urls", namespace="password_reset")),
]

app_name = "users"
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"organization", OrganizationViewSet, basename="organization")


urlpatterns += router.urls
