from django.urls import path
from . import views

urlpatterns = [
    path('team/<int:team_id>/roadmap/', views.team_roadmap, name='team_roadmap'),
    path('team/<int:team_id>/roadmap/add/', views.add_team_milestone, name='add_team_milestone'),    path('team/<int:team_id>/roadmap/<int:milestone_id>/edit/', views.edit_team_milestone, name='edit_team_milestone'),
    path('team/<int:team_id>/roadmap/<int:milestone_id>/delete/', views.delete_team_milestone, name='delete_team_milestone'),
    path('team/<int:team_id>/milestone/<int:milestone_id>/complete/', views.mark_milestone_complete, name='mark_milestone_complete'),
]
