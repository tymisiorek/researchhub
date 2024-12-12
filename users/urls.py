from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),                         # Home page
    path('logout/', views.logout_view, name='logout_view'),    # Logout page
    path('calendar/<int:team_id>/', views.calendar_view, name='calendar_view'),
    path('calendar/<int:team_id>/data/', views.get_availability_data, name='get_availability_data'),
    path('calendar/<int:team_id>/add/', views.add_availability, name='add_availability'),
    path('calendar/<int:team_id>/delete/<int:availability_id>/', views.delete_availability, name='delete_availability'),
    path('profile/', views.profile, name='profile'),           # Profile page
    path('uploads/', views.uploads, name='uploads'),           # Uploads page
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
