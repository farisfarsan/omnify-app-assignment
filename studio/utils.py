# studio/utils.py
from rest_framework.response import Response
from rest_framework import status

def token_email_match(request):
 
    email = request.query_params.get('email') or request.data.get('email')
    if not email:
        return False, Response({'error': 'Email parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

    if request.user.email.strip().lower() != email.strip().lower():
        return False, Response({'error': 'Email does not match token.'}, status=status.HTTP_403_FORBIDDEN)

    return True, None
