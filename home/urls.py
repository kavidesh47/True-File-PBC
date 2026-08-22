from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('chart/', views.chart, name='chart'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),

    # Admin
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-register/', views.admin_register, name='admin_register'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('upload-document/', views.upload_document, name='upload_document'),
    path('blockchain-ledger/', views.blockchain_ledger, name='blockchain_ledger'),
    path('verification-reports/', views.verification_reports, name='verification_reports'),

    # User
    path('user-login/', views.user_login, name='user_login'),
    path('user-register/', views.user_register, name='user_register'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('upload-verification/', views.upload_verification, name='upload_verification'),
    path('verification-result/', views.verification_result, name='verification_result'),
    path('digilocker/', views.digilocker, name='digilocker'),
    path('verification-history/', views.verification_history, name='verification_history'),
    path('verify/', views.upload_verification, name='verify'),
    # Contact
    path('contact/', views.contact, name='contact'),

    path('user-logout/', views.user_logout, name='user_logout'),

    path('admin-logout/', views.admin_logout, name='admin_logout'),

    path(
    'delete-document/<int:id>/',
    views.delete_document,
    name='delete_document'
),
    path(
    "upload-digilocker/",
    views.upload_digilocker,
    name="upload_digilocker"
),

]