from django.urls import path
from . import views

# urlpatterns = [
#     path('reset_password/<str:user_id>/', views.reset_password, name='resetpassword'),
#     path('register/', views.register, name='register'),
#     path('user/verify/<int:uid>/', views.verify, name='verify'),
#     path('login/', views.login_page, name='login'),
#     path('logout/', views.logout, name='logout'),
#     path('admin_userlist/', views.admin_userlist, name='adminuserlist'),
#     path('adminuser/edit/<int:user_id>/', views.admin_user_edit, name='adminuseredit'),
#     path('forgotpassword/', views.forgot_password, name='forgotpassword'),
#     path('<int:uid>/otp_fp/verify/', views.otp_fp_verify, name='otpfpverify'),
    
# ]

urlpatterns = [
    path('reset_password/<str:user_id>/', views.reset_password, name='resetpassword'),
    path('user/verify/<int:uid>/', views.verify, name='verify'),
    path('<int:uid>/otp_fp/verify/', views.otp_fp_verify, name='otpfpverify'),
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout, name='logout'),
    path('admin_userlist/', views.admin_userlist, name='adminuserlist'),
    path('adminuser/edit/<int:user_id>/', views.admin_user_edit, name='adminuseredit'),
    path('forgotpassword/', views.forgot_password, name='forgotpassword'),
]