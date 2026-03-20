import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rnd_platform.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
password = 'adminpassword'
email = 'admin@example.com'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser created: {username} / {password}")
else:
    u = User.objects.get(username=username)
    u.set_password(password)
    u.save()
    print(f"Superuser password reset: {username} / {password}")
