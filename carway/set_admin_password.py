import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carway.settings')
django.setup()

from django.contrib.auth.models import User

# Get admin user
admin = User.objects.get(username='admin')

# Set new password
admin.set_password('admin123')
admin.save()

print("Admin password set to 'admin123'")