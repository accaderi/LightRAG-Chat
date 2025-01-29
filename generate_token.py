# generate_token.py
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Replace 'admin' with your superuser username
user = User.objects.get(username='a')
token = Token.objects.create(user=user)
print(f"Your authentication token is: {token.key}")