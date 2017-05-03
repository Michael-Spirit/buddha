from django.conf.urls import url

from accounts.views import RegisterView, LoginView, UserAPI

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserAPI, base_name='users')

urlpatterns = [
    url(r'^auth/registration/', RegisterView.as_view(), name='register'),
    url(r'^auth/login/', LoginView.as_view(), name='login'),
]

urlpatterns += router.urls
