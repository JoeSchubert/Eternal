from PIL import Image
import os

path = "profile_images"


async def resize_image(f, user, filename):
    if not os.path.exists(path):
        os.mkdir(path)
    if not os.path.exists(path + "/" + user):
        os.mkdir(path + "/" + user)
    img = Image.open(f)
    max_size = (800, 800)
    img.thumbnail(max_size)
    img.save(path + "/" + user + "/" + filename)


def get_profile_image(user):
    if os.path.isdir(path + "/" + user):
        files = next(os.walk(path + "/" + user))[2]
        if len(files) > 0:
            return os.listdir(path + "/" + user)
        else:
            return False
    else:
        return False
