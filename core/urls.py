from django.urls import path
from . import views
from .upload_views import upload_image, upload_test_page

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('discover/', views.discover, name='discover'),
    path('profile/', views.profile_view, name='profile'),
    path('ai-tools/', views.ai_tools, name='ai_tools'),
    path('apply/<int:pk>/', views.apply_opportunity, name='apply'),
    path('save/<int:pk>/', views.save_opportunity, name='save'),
    path('saved/', views.saved_opportunities, name='saved'),
    # Upload
    path('upload-image/', upload_image, name='upload_image'),
    path('upload-test/', upload_test_page, name='upload_test'),
    # Sub-Admin
    path('subadmin/', views.subadmin_dashboard, name='subadmin_dashboard'),
    path('subadmin/users/', views.subadmin_users, name='subadmin_users'),
    path('subadmin/users/<int:pk>/toggle/', views.subadmin_toggle_user, name='subadmin_toggle_user'),
    path('subadmin/opportunities/', views.subadmin_opportunities, name='subadmin_opportunities'),
    path('subadmin/opportunities/<int:pk>/delete/', views.subadmin_delete_opportunity, name='subadmin_delete_opportunity'),
    path('subadmin/courses/', views.subadmin_courses, name='subadmin_courses'),
    path('subadmin/courses/add/', views.subadmin_add_course, name='subadmin_add_course'),
    path('subadmin/courses/<int:pk>/edit/', views.subadmin_edit_course, name='subadmin_edit_course'),
    path('subadmin/courses/<int:pk>/delete/', views.subadmin_delete_course, name='subadmin_delete_course'),
    path('subadmin/manage/', views.subadmin_manage, name='subadmin_manage'),
    # Chatbot
    path('chat/', views.chat_page, name='chat'),
    path('chat/api/', views.chat_api, name='chat_api'),
    # Password Reset
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
]
