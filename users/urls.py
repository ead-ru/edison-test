from django.urls import path
from users import views


app_name = 'users'
urlpatterns = [
    path('register/', views.UserRegister.as_view(), name='register'),
    path('ready/', views.list_ready_users, name='ready_users')
]
