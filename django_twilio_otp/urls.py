from django.conf.urls import url, include
from rest_framework import routers
from django_twilio_otp import views

router = routers.DefaultRouter()

""" Urls in Versionwised, In future any make updation for any views please update it as v2..etc """

urlpatterns = [
    
    url(r'^', include(router.urls)),

    url(r'^api/v1/user-signup/$', views.UserSignupView.as_view(), name="user_signup_view"),
    url(r'^api/v1/verify-token/$', views.VerifyToken.as_view(), name="VerifyToken"),
    url(r'^api/v1/resend-token/$', views.ResendCode.as_view(), name="ResendCode"),

    
    
]

