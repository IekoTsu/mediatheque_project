# create_superuser_and_group.py
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediatheque_project.settings')
django.setup()
from django.contrib.auth.models import User, Group


def create_superuser_and_group():
    # Create a group
    group_name = 'bibliothecaires'
    group, group_created = Group.objects.get_or_create(name=group_name)
    if group_created:
        print(f'Group "{group_name}" created.')
    else:
        print(f'Group "{group_name}" already exists.')

    # Create a user
    username = 'test'
    password = 'test123'
    email = 'test@example.com'
    user, user_created = User.objects.get_or_create(username=username, defaults={'email': email})
    if user_created:
        user.set_password(password)  # Hash the password
        user.save()
        print(f'User "{username}" created successfully.')
    else:
        print(f'User "{username}" already exists.')

    # Add the user to the group
    user.groups.add(group)
    print(f'User "{username}" added to group "{group_name}".')


if __name__ == "__main__":
    create_superuser_and_group()
