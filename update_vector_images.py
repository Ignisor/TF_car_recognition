import asyncio
import time
import threading

from data.models import Image


def update_image(img):
    print(f"started {img.url}")
    img.update_vector()
    img.save()
    print(f"updated {img.url}")


if __name__ == '__main__':
    threads = []

    for image in Image.objects.all():
        t = threading.Thread(target=update_image, args=(image, ))
        threads.append(t)

    for t in threads:
        while threading.active_count() > 10:
            # waiting for free slots
            pass

        t.start()

