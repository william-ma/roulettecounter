"""probability URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework import routers

from . import views

app_name = "roulettecounter"

router = routers.DefaultRouter()
router.register('api/users', views.UserViewSet)

urlpatterns = [
    path('', views.home_request, name="home"),
    # path('visualize', views.visualize, name="visualize"),
    path('signup', views.signup, name="signup"),
    path('logout', views.logout_request, name="logout"),
    path('login', views.login_request, name="login"),
    path('start_session', views.start_session_request, name="start_session"),
    path('end_session', views.end_session_request, name="end_session"),
    path('number/<int:number>', views.number_request, name="number"),
    path('delete_most_recent', views.delete_most_recent_request, name="delete_most_recent"),
    path('history', views.history_request, name="history"),
    path('mobile', views.mobile_request, name="mobile"),
    path('', include(router.urls))
]
