"""busrs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.signin, name='signin'),
    url(r'^signin', views.signin, name='signin'),
    url(r'^signup/', views.signup, name='signup'),
    url(r'^signout/', views.signout, name='signout'),
    url(r'^reset/', views.reset, name='reset'),
    url(r'^about-us/', views.about, name='about'),
    url(r'^reset-new/', views.resetNew, name='resetnew'),
    url(r'^homebrs/', views.homebrs, name='homebrs'),
    url(r'^admin-home-BRS/', views.adminhomebrs, name='adminhomebrs'),
    url(r'^admin-user-delete/', views.adminUserDelete, name='adminuserdelete'),
    url(r'^admin-bus-delete/', views.adminBusDelete, name='adminbusdelete'),
    url(r'^admin-bus-add/', views.adminBusAdd, name='adminbusadd'),
    url(r'^admin-sql/', views.adminSQL, name='adminsql'),
    url(r'addbus_private',views.addbus,name='addbus'),
#    url(r'resetconfirm_private', views.resetconfirm, name='resetconfirm'),
    url(r'^bookinghistory/', views.bookinghistory, name='bookinghistory'),
    url(r'^upcomingtrips/', views.upcomingtrips, name='upcomingtrips'),
    url(r'^bus_schedule/', views.bus_schedule, name='bus_schedule'),
    url(r'^bookticket/', views.bookticket, name='bookticket'),
    url(r'^cancellation/',views.cancellation,name='cancellation'),
    url(r'^passengerinfo',views.passengerinfo_ticket,name='passengerinfo')
]
