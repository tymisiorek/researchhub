'''
*  REFERENCES
*  Title: ChatGPT
*  Author: OpenAI
*  Date: 11/16/2024
*
*  Used to add docstrings and comments  to functions and write boilerplate for the
functions in this view.
'''

# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Availability
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
import json
import datetime
from project_b_07.models import Team, TeamMembership, TeamFile, TeamChatMessage
from roadmap.models import Milestone

@login_required
def home(request):
    """
    View function to render the home page with user's teams, messages, milestones, and files.
    """
    # Check user's role
    user = request.user
    
    # Check if the user belongs to the 'admin' or 'common' group
    user_profile = request.user.profile
    is_admin = user_profile.role == 'admin'
    is_common_user = user_profile.role == 'common'

    # Fetch user's teams
    user_teams = Team.objects.filter(memberships__user=user, memberships__status='accepted')

    # Fetch messages related to user's teams
    user_messages = TeamChatMessage.objects.filter(team__in=user_teams).order_by('-created_at')[:10]

    # Fetch milestones for user's teams
    user_milestones = Milestone.objects.filter(team__in=user_teams).order_by('end_date')[:10]

    # Fetch files uploaded to user's teams
    user_files = TeamFile.objects.filter(team__in=user_teams).order_by('-uploaded_at')[:10]

    return render(request, 'home.html', {
        'is_admin': is_admin,
        'is_common_user': is_common_user,
        'user_teams': user_teams,
        'user_messages': user_messages,
        'user_milestones': user_milestones,
        'user_files': user_files,
    })


def logout_view(request):
    """
    Logs out the current user and redirects them to the homepage.
    """
    logout(request)
    return redirect("/")


@login_required
def calendar_view(request, team_id):
    """
    Renders the calendar view for a specific team.
    PMA Administrators can access any team's calendar.
    """
    team = get_object_or_404(Team, id=team_id)
    user_profile = request.user.profile
    is_pma_admin = user_profile.role == 'admin'

    # Fetch all availability events for the team
    availabilities = Availability.objects.filter(team=team)

    return render(request, 'calendar.html', {
        'team': team,  # Pass the team object to the template
        'availabilities': availabilities,  # Pass availability data to the template if needed
        'is_pma_admin': is_pma_admin,  # Pass admin status to the template
    })


@login_required
def add_availability(request, team_id):
    """
    Adds a new availability event for a team.
    """
    team = get_object_or_404(Team, id=team_id)

    # Check if the user is a team member
    is_member = TeamMembership.objects.filter(
        user=request.user,
        team=team,
        status='accepted'
    ).exists() or team.created_by == request.user

    user_profile = request.user.profile
    is_pma_admin = user_profile.role == 'admin'

    if is_pma_admin:
        messages.error(request, "You do not have permission to add availability.")
        return redirect('calendar_view', team_id=team.id)

    if not is_member:
        messages.error(request, "You must be a team member to add availability.")
        return redirect('calendar_view', team_id=team.id)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date = data.get('date')
            start_time = data.get('start_time')
            end_time = data.get('end_time')

            # Validate inputs
            if not date or not start_time or not end_time:
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            start_datetime = datetime.datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")

            if start_datetime >= end_datetime:
                return JsonResponse({'error': 'End time must be after start time.'}, status=400)

            # Create availability
            Availability.objects.create(
                user=request.user,
                team=team,
                date=start_datetime.date(),
                start_time=start_datetime.time(),
                end_time=end_datetime.time()
            )
            return JsonResponse({'success': True})
        except ValueError:
            return JsonResponse({'error': 'Invalid date/time format.'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def delete_availability(request, team_id, availability_id):
    """
    Deletes an availability event for a team.
    PMA Administrators can delete any availability, team owners can delete their team members’ availability,
    and individual users can delete their own availability.
    """
    team = get_object_or_404(Team, id=team_id)
    availability = get_object_or_404(Availability, id=availability_id, team=team)
    user = request.user
    user_profile = request.user.profile
    is_pma_admin = user_profile.role == 'admin'

    # Check permissions
    is_authorized = availability.user == user or team.created_by == user

    if not is_authorized:
        return JsonResponse({'error': 'You do not have permission to delete this availability.'}, status=403)

    if request.method == 'DELETE':
        availability.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required
def get_availability_data(request, team_id):
    """
    Retrieves all availability data for a specific team.
    """
    team = get_object_or_404(Team, id=team_id)
    user = request.user
    user_profile = request.user.profile
    is_pma_admin = user_profile.role == 'admin'

    # Check if the user has access to the team's data
    is_member = TeamMembership.objects.filter(user=user, team=team, status='accepted').exists() or is_pma_admin

    if not is_member:
        return JsonResponse({'error': 'You do not have access to this team.'}, status=403)

    # Retrieve and format availability data
    availabilities = Availability.objects.filter(team=team).select_related('user')
    event_list = [
        {
            'id': availability.id,
            'title': f"{availability.user.username}'s Availability",
            'start': datetime.datetime.combine(availability.date, availability.start_time).isoformat(),
            'end': datetime.datetime.combine(availability.date, availability.end_time).isoformat(),
            'owner': availability.user.username,
        }
        for availability in availabilities
    ]
    return JsonResponse(event_list, safe=False)

@login_required
def profile(request):
    """
    Renders the user's profile page.
    This can be extended to display more user-specific information.
    """
    return render(request, 'profile.html', {'user': request.user})

@login_required
def uploads(request):
    """
    Renders a page showing the user's uploaded files or documents.
    Adjust this view according to the actual model handling file uploads.
    """
    documents = Availability.objects.filter(user=request.user) 
    return render(request, 'uploads.html', {'documents': documents})
