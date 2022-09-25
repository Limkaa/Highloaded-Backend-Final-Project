import os

def courseCoverFilePath(instance, filename):
    return os.path.join('covers', f'{str(instance.id)}-course-cover.png')
