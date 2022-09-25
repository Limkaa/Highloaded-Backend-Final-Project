import os

def avatarFilePath(instance, filename):
    return os.path.join('avatars', f'{str(instance.id)}-profile-photo.png')
