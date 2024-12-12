from .models import Profile
'''
*  REFERENCES
*  Title: ChatGPT
*  Author: OpenAI
*  Date: 11/16/2024
*
*  Used to ensure that a user is common user by default if they sign into the PMA
'''

class EnsureProfileMiddleware:
    """
    Middleware to ensure that every authenticated user has a Profile.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not hasattr(request.user, 'profile'):
            Profile.objects.get_or_create(user=request.user, defaults={'role': 'common'})

        response = self.get_response(request)
        return response
