'''
*  REFERENCES
*  Title: ChatGPT
*  Author: OpenAI
*  Date: 12/3/2024
*  Code version: GPT-4
*  URL: https://openai.com
*
*  Use: ChatGPT-generated comments and explanations for Django views and models. Wrote boilerplate for many of the methods
'''

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Milestone
from .forms import MilestoneForm
from project_b_07.models import Team, TeamMembership
from django.contrib import messages

@login_required
def team_roadmap(request, team_id):
    """
    Renders the roadmap view for a specific team.
    PMA Administrators can access any team's roadmap.
    """
    team = get_object_or_404(Team, id=team_id)
    user_profile = request.user.profile
    is_pma_admin = user_profile.role == 'admin'

    # Fetch all milestones for the team
    milestones = Milestone.objects.filter(team=team).order_by('end_date')

    return render(request, 'roadmap/roadmap.html', {
        'team': team,  # Pass the team object to the template
        'milestones': milestones,  # Pass the milestones to the template
        'is_pma_admin': is_pma_admin  # Pass admin status to the template if needed
    })

@login_required
def add_team_milestone(request, team_id):
    """Add a new milestone for a team."""
    team = get_object_or_404(Team, id=team_id)
    user = request.user
    user_profile = request.user.profile
    is_pma_admin = user_profile.role == 'admin'

    if is_pma_admin:
        messages.error(request, "PMA Admins are not allowed to add milestones.")
        return redirect('team_detail', team_id=team.id)
    
    # Check if user is a team member
    is_member = TeamMembership.objects.filter(
        user=request.user,
        team=team,
        status='accepted'
    ).exists() or team.created_by == request.user

    if not is_member:
        messages.error(request, "You must be a team member to add milestones.")
        return redirect('team_detail', team_id=team.id)

    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.user = request.user
            milestone.team = team
            milestone.save()
            messages.success(request, "Milestone added successfully.")
            return redirect('team_roadmap', team_id=team.id)
    else:
        form = MilestoneForm()
    
    return render(request, 'roadmap/add_milestone.html', {
        'form': form,
        'team': team
    })

@login_required
def edit_team_milestone(request, team_id, milestone_id):
    """Edit an existing team milestone."""
    team = get_object_or_404(Team, id=team_id)
    milestone = get_object_or_404(Milestone, id=milestone_id, team=team)
    user = request.user
    user_profile = request.user.profile
    is_pma_admin = user_profile.role == 'admin'

    # PMA Admins cannot edit milestones
    if is_pma_admin:
        messages.error(request, "PMA Administrators cannot edit milestones.")
        return redirect('team_roadmap', team_id=team.id)
    
    # Check if user is a team owner or milestone creator
    is_authorized = team.created_by == user or milestone.user == user

    if not is_authorized:
        messages.error(request, "You must be the team owner or milestone creator to edit this milestone.")
        return redirect('team_roadmap', team_id=team.id)

    if request.method == 'POST':
        form = MilestoneForm(request.POST, instance=milestone)
        if form.is_valid():
            form.save()
            messages.success(request, "Milestone updated successfully.")
            return redirect('team_roadmap', team_id=team.id)
    else:
        form = MilestoneForm(instance=milestone)
    
    return render(request, 'roadmap/edit_milestone.html', {
        'form': form,
        'team': team,
        'milestone': milestone,
    })

@login_required
def delete_team_milestone(request, team_id, milestone_id):
    """Delete a team milestone."""
    team = get_object_or_404(Team, id=team_id)
    milestone = get_object_or_404(Milestone, id=milestone_id, team=team)
    user = request.user

    # Check if the user is a PMA Admin or the team owner/milestone creator
    user_profile = request.user.profile
    is_pma_admin = user_profile.role == 'admin'
    is_authorized = is_pma_admin or team.created_by == user or milestone.user == user

    # PMA Admins cannot delite milestones
    if is_pma_admin:
        messages.error(request, "PMA Administrators cannot delete milestones.")
        return redirect('team_roadmap', team_id=team.id)

    if not is_authorized:
        messages.error(request, "You must be the team owner or milestone creator to delete this milestone.")
        return redirect('team_roadmap', team_id=team.id)

    if request.method == 'POST':
        milestone.delete()
        messages.success(request, "Milestone deleted successfully.")
        return redirect('team_roadmap', team_id=team.id)
    
    return render(request, 'roadmap/delete_milestone.html', {
        'team': team,
        'milestone': milestone
    })

@login_required
def mark_milestone_complete(request, team_id, milestone_id):
    """Mark a milestone as complete."""
    team = get_object_or_404(Team, id=team_id)
    milestone = get_object_or_404(Milestone, id=milestone_id, team=team)
    user = request.user

    is_authorized = team.created_by == user or milestone.user == user
    if not is_authorized:
        messages.error(request, "You must be the team owner or milestone creator to mark this milestone as complete.")
        return redirect('team_roadmap', team_id=team.id)

    milestone.mark_complete()
    messages.success(request, "Milestone marked as complete.")
    return redirect('team_roadmap', team_id=team.id)