import boto3, os, json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from botocore.exceptions import ClientError
from urllib.parse import quote
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser

from .forms import TeamCreationForm, TeamFileUploadForm, Team
from .models import Team, TeamMembership, TeamFile, TeamChatMessage

'''
*  REFERENCES
*  Title: ChatGPT
*  Author: OpenAI
*  Date: 11/16/2024
*  Code version: GPT-4
*  URL: https://openai.com
*
*  Use: ChatGPT-generated comments and explanations for Django views and models. Wrote boilerplate for many of the methods
*       helped with serving file, upload, and deleting from bucket and site

*  Title: Medium
*  Author: Taylor Hughes
*  Date: 11/16/2024
*  URL: https://medium.com/@taylorhughes/simple-secure-direct-to-s3-uploads-from-modern-browsers-f42695e596ba
*  Use: Used to help implement direct upload to S3 bucket - was having issues with getting it to work through Django default upload feature
'''

# Public view for Anonymous Users
class PublicTeamListView(ListView):
    model = Team
    template_name = 'public_team_list.html'  # Create a separate template
    context_object_name = 'teams'

    def get_queryset(self):
        # Return all teams; limit the information exposed in the template
        return Team.objects.all().select_related('created_by')
    

@login_required
def moderate_project(request, team_id):
    """
    Allow PMA Administrators to moderate a team (e.g., delete files or entire teams).
    """
    team = get_object_or_404(Team, id=team_id)
    user_profile = request.user.profile

    if user_profile.role != 'admin':
        messages.error(request, "You do not have permission to moderate this team.")
        return redirect('team_detail', team_id=team.id)

    # Implement moderation logic here, e.g., deleting a team file
    # Example: Deleting a file
    if request.method == "POST":
        file_id = request.POST.get('file_id')
        team_file = get_object_or_404(TeamFile, id=file_id, team=team)
        team_file.delete()
        messages.success(request, f"File '{team_file.title}' has been deleted by an administrator.")
        return redirect('team_detail', team_id=team.id)

    return render(request, 'moderate_team.html', {'team': team})
    
# View after clicking "Upload"
def upload_confirmation(request, file_name):
    """
    View to display confirmation of successful upload and a preview of the uploaded file.
    """
    # URL-encode the file name to ensure special characters are handled
    file_name_encoded = quote(file_name)
    # Generate the full URL for accessing the file in the S3 bucket
    file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name_encoded}"
    return render(request, 'upload_confirmation.html', {
        'file_url': file_url,  # Pass the file URL to the template
        'file_name': file_name,  # Pass the original file name to the template
    })


@login_required
def create_team(request):
    """
    Allow only Common Users to create a new team.
    PMA Administrators are restricted from creating teams.
    """
    user_profile = request.user.profile
    if user_profile.role != 'common':
        messages.error(request, "You do not have permission to create a team.")
        return redirect('team_list')  # Redirect to the team list page

    if request.method == "POST":
        form = TeamCreationForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.created_by = request.user
            team.save()
            # Add the creator as the team owner
            TeamMembership.objects.create(
                user=request.user,
                team=team,
                role="Owner",
                status='accepted',
            )
            messages.success(request, f"Team '{team.name}' created successfully!")
            return redirect('team_detail', team_id=team.id)
    else:
        form = TeamCreationForm()
    return render(request, "create_team.html", {"form": form})


@login_required
def team_list(request):
    """
    Display a list of all teams and annotate each team with the user's membership status.
    """
    teams = Team.objects.all()
    user_memberships = TeamMembership.objects.filter(user=request.user)
    # Create a mapping of team IDs to membership statuses
    memberships = {membership.team_id: membership.status for membership in user_memberships}
    # Annotate each team with the user's membership status and ownership
    for team in teams:
        team.membership_status = memberships.get(team.id)
        team.is_owner = team.created_by == request.user
    return render(request, 'team_list.html', {'teams': teams})


@login_required
def join_team(request, team_id):
    """
    Handle requests to join a team. Create a membership or check existing status.
    """
    team = get_object_or_404(Team, id=team_id)
    # Prevent the owner from rejoining their own team
    if team.created_by == request.user:
        messages.info(request, "You are the owner of this team.")
        return redirect('team_detail', team_id=team.id)

    # Get or create a membership for the user and team
    membership, created = TeamMembership.objects.get_or_create(user=request.user, team=team)
    if not created:
        # Notify user of their existing membership status
        if membership.status == 'accepted':
            messages.info(request, f"You are already a member of '{team.name}'.")
        elif membership.status == 'pending':
            messages.info(request, f"Your join request for '{team.name}' is already pending.")
        elif membership.status == 'rejected':
            messages.info(request, f"Your join request for '{team.name}' was rejected.")
    else:
        # Create a new membership with 'pending' status
        membership.status = 'pending'
        membership.save()
        messages.success(request, f"You have requested to join the team '{team.name}'.")

    return redirect('team_detail', team_id=team.id)


@login_required
def team_detail(request, team_id):
    """
    Display detailed information about a team, including files and members if the user is a member, owner, or PMA Administrator.
    """
    team = get_object_or_404(Team, id=team_id)
    user = request.user
    is_owner = team.created_by == user

    # Check if the user is a PMA Administrator
    user_profile = request.user.profile
    is_pma_admin = user_profile.role == 'admin'

    # Check if the user has an existing membership
    membership = TeamMembership.objects.filter(user=user, team=team).first()
    is_member = (membership.status == 'accepted' if membership else False) or is_owner or is_pma_admin  # Include PMA Admins

    # Handle file filtering based on the search query
    files = team.files.all()
    query = request.GET.get('q', '').strip()
    if query:
        files = files.filter(keywords__icontains=query)  # Case-insensitive keyword search

    members = team.memberships.filter(status='accepted').select_related('user') if is_member else None
    pending_requests = team.memberships.filter(status='pending').select_related('user') if is_owner or is_pma_admin else None

    return render(request, 'team_detail.html', {
        'team': team,
        'is_member': is_member,
        'is_owner': is_owner,
        'is_pma_admin': is_pma_admin,
        'files': files,
        'members': members,
        'pending_requests': pending_requests,
        'membership': membership,
        'query': query,  # Pass the query back to the template
    })



@login_required
def upload_team_file(request, team_id):
    """
    Handle file uploads to a team by checking membership status and uploading to S3.
    """
    team = get_object_or_404(Team, id=team_id)
    is_owner = team.created_by == request.user
    is_member = TeamMembership.objects.filter(
        user=request.user, team=team, status='accepted'
    ).exists() or is_owner

    if not is_member:
        messages.error(request, "You are not an accepted member of this team.")
        return redirect('team_detail', team_id=team.id)
    if request.method == 'POST':
        form = TeamFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            team_file = TeamFile(
                title=form.cleaned_data['title'],
                file=form.cleaned_data['file'],
                description=form.cleaned_data['description'],
                keywords=form.cleaned_data['keywords'],
                uploaded_by=request.user,
                team=team
            )

            # Generate and encode file name
            file_name = os.path.basename(team_file.file.name)
            file_name_encoded = quote(file_name)

            # Create S3 client for file upload
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

            try:
                # Read file content and upload to S3
                file_content = team_file.file.open('rb').read()

                s3_client.put_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=file_name,
                    Body=file_content,
                    ContentType=request.FILES['file'].content_type,
                )

                # Save the file entry to the database after successful upload
                team_file.save()
                messages.success(request, "File uploaded successfully.")
                return redirect('team_detail', team_id=team.id)

            except Exception as e:
                # Handle any upload errors
                print(f"Error uploading {file_name} to S3: {e}")
                return render(request, 'upload_team_file.html', {'form': form, 'error': str(e), 'team': team})
    else:
        form = TeamFileUploadForm()  # Display an empty form for GET requests
    files = team.files.all()
    return render(request, 'upload_team_file.html', {'form': form, 'team': team, 'files': files})


@login_required
def view_team_files(request, team_id):
    """
    View to list all files associated with a specific team if the user is a member.
    """
    team = get_object_or_404(Team, id=team_id)
    user_profile = request.user.profile
    is_pma_admin = user_profile.role == 'admin'
    membership = TeamMembership.objects.filter(user=request.user, team=team).exists()

    if not is_pma_admin or not membership:
        messages.error(request, "You are not a member of this team.")
        return redirect('team_list')

    files = team.files.all()  # Get all files related to the team
    return render(request, 'view_team_files.html', {'team': team, 'files': files})


@login_required
def delete_team(request, team_id):
    """
    Allow Common Users to delete their own teams.
    Allow PMA Administrators to delete any team.
    """
    team = get_object_or_404(Team, id=team_id)
    user_profile = request.user.profile

    # Check if the user is the team owner or a PMA Administrator
    if team.created_by == request.user or user_profile.role == 'admin':
        team.delete()
        messages.success(request, f"Team '{team.name}' has been deleted.")
        return redirect('team_list')
    else:
        messages.error(request, "You do not have permission to delete this team.")
        return redirect('team_detail', team_id=team.id)

@login_required
def accept_membership_request(request, team_id, membership_id):
    """
    Allow team owners to accept a membership request.
    """
    team = get_object_or_404(Team, id=team_id)
    membership = get_object_or_404(TeamMembership, id=membership_id, team=team, status='pending')
    user_profile = request.user.profile

    if not (team.created_by == request.user):
        messages.error(request, "You do not have permission to accept membership requests.")
        return redirect('team_detail', team_id=team.id)

    membership.status = 'accepted'
    membership.save()
    messages.success(request, f"{membership.user.username} has been added to the team.")
    return redirect('team_detail', team_id=team.id)

@login_required
def reject_membership_request(request, team_id, membership_id):
    """
    Allow team owners to reject a membership request.
    """
    team = get_object_or_404(Team, id=team_id)
    membership = get_object_or_404(TeamMembership, id=membership_id, team=team, status='pending')
    user_profile = request.user.profile

    if not (team.created_by == request.user):
        messages.error(request, "You do not have permission to reject membership requests.")
        return redirect('team_detail', team_id=team.id)

    membership.status = 'rejected'
    membership.save()
    messages.success(request, f"{membership.user.username}'s request has been rejected.")
    return redirect('team_detail', team_id=team.id)


@login_required
def serve_file(request, file_id):
    """
    Serve a file stored in an S3 bucket for download or inline viewing.
    PMA Administrators can access any file.
    Common Users can access files within their teams.
    """
    team_file = get_object_or_404(TeamFile, id=file_id)
    user_profile = request.user.profile

    # PMA Administrators can access any file
    if user_profile.role != 'admin':
        # Check if the user is a member or the owner of the team
        is_member = TeamMembership.objects.filter(user=request.user, team=team_file.team, status='accepted').exists()
        is_owner = team_file.team.created_by == request.user
        if not (is_member or is_owner):
            messages.error(request, "You do not have permission to access this file.")
            return redirect('team_list')

    # Initialize an S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    try:
        # Retrieve the file from the S3 bucket
        file_obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=team_file.file.name)
        response = FileResponse(file_obj['Body'], content_type=file_obj['ContentType'])
        response['Content-Disposition'] = f'inline; filename="{quote(team_file.title)}"'
        return response
    except ClientError as e:
        print(f"Failed to retrieve file from S3: {e}")
        return HttpResponse("File not found.", status=404)


@login_required
def team_chat(request, team_id):
    """
    Display the chat page for a team with existing messages.
    """
    team = get_object_or_404(Team, id=team_id)  # Get the team or return a 404 if not found
    chat_messages = TeamChatMessage.objects.filter(team=team).order_by('created_at')  # Retrieve chat messages for the team
    return render(request, 'team_chat.html', {
        'team': team,  # Pass the team object to the template
        'chat_messages': chat_messages  # Pass chat messages to the template
    })


@login_required
def post_chat_message(request, team_id):
    """
    Handle AJAX POST request to save a new chat message.
    """
    if request.method == 'POST':
        team = get_object_or_404(Team, id=team_id)  # Get the team or return a 404 if not found
        user_profile = request.user.profile
        
        #pma admins should not be able to send message
        if user_profile.role == 'admin':
            return JsonResponse({'success': False, 'error': 'PMA Administrators are not allowed to post messages'}, status=403)
        
        data = json.loads(request.body)  # Parse the JSON body of the request
        message_content = data.get('message', '')  # Get the message content from the data

        if message_content.strip():
            # Create and save a new chat message
            new_message = TeamChatMessage.objects.create(
                team=team,
                user=request.user,
                message=message_content
            )
            # Return the new message data so it can be appended dynamically
            return JsonResponse({
                'success': True,
                'message': {
                    'id': new_message.id,
                    'user': new_message.user.username,
                    'content': new_message.message,
                    'created_at': new_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
            })

        return JsonResponse({'success': False, 'error': 'Message cannot be empty'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@login_required
def leave_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    membership = get_object_or_404(TeamMembership, user=request.user, team=team, status='accepted')

    if team.created_by == request.user:
        messages.error(request, "Team owners cannot leave their own team.")
        return redirect('team_detail', team_id=team.id)

    membership.delete()
    messages.success(request, f"You have left the team '{team.name}'.")
    return redirect('team_list')

def anonymous_login(request):
    """
    Allows anonymous users to view the public team list without signing in.
    """
    if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
        # Redirect to the public team list page
        return redirect('public_team_list')
    else:
        # If a logged-in user tries to access this view, redirect to their team list
        return redirect('team_list')

def is_admin(user):
    """Helper function to check if a user is an admin."""
    return user.profile.role == 'admin'

@login_required
def delete_file(request, file_id):
    """
    Handles file deletion. Only accessible to admins or the file uploader.
    """
    file = get_object_or_404(TeamFile, id=file_id)

    # Ensure the user has permission to delete the file
    if not (is_admin(request.user) or file.uploaded_by == request.user):
        return HttpResponseForbidden("You do not have permission to delete this file.")

    if request.method == 'POST':  # Ensure the method is POST for deletion
        file.delete()
        messages.success(request, f"File '{file.title}' has been deleted successfully.")
        return redirect('team_detail', team_id=file.team.id)

    return redirect('team_detail', team_id=file.team.id)