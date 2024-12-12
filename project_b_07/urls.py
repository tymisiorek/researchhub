from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from . import views
from .views import (
    upload_confirmation,
    team_list,
    create_team,
    join_team,
    team_detail,
    upload_team_file,
    view_team_files,
    delete_team,
    accept_membership_request,
    reject_membership_request,
    serve_file,
    PublicTeamListView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("users.urls")),
    
    # Uploads
    path('upload-confirmation/<str:file_name>/', upload_confirmation, name='upload_confirmation'),
    
    # Teams
    path('teams/', team_list, name='team_list'),
    path('teams/create/', create_team, name='create_team'),
    path('teams/<int:team_id>/join/', join_team, name='join_team'),
    path('teams/<int:team_id>/', team_detail, name='team_detail'),
    path('teams/<int:team_id>/upload/', upload_team_file, name='upload_team_file'),
    path('teams/<int:team_id>/files/', view_team_files, name='view_team_files'),
    path('teams/<int:team_id>/delete/', delete_team, name='delete_team'),
    path('teams/<int:team_id>/leave/', views.leave_team, name='leave_team'),
    path('team/<int:team_id>/chat/', views.team_chat, name='team_chat'),
    path('team/<int:team_id>/chat/post/', views.post_chat_message, name='post_chat_message'),

    # Membership requests
    path('teams/<int:team_id>/membership/<int:membership_id>/accept/', views.accept_membership_request, name='accept_membership_request'),
    path('teams/<int:team_id>/membership/<int:membership_id>/reject/', views.reject_membership_request, name='reject_membership_request'),
    
    # File preview and serving
    path('file/serve/<int:file_id>/', serve_file, name='serve_file'),  # New URL pattern for serving files
    
    # Roadmap
    path('roadmap/', include('roadmap.urls')),

    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
   
    path('teams/public/', PublicTeamListView.as_view(), name='public_team_list'),
    path('teams/<int:team_id>/moderate/', views.moderate_project, name='moderate_project'),

    path('teams/<int:team_id>/membership/<int:membership_id>/reject/', views.reject_membership_request, name='reject_membership_request'),

    path('anonymous_login/', views.anonymous_login, name='anonymous_login'),

    path('delete-file/<int:file_id>/', views.delete_file, name='delete_file'),

]