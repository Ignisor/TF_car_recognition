from urllib.request import urlopen
from io import BytesIO

import tensorflow as tf
from PIL import Image

from .models import Image as DataImage


class ImageSet(object):
    def get_train_batch(self, amount):
        """Returns 'amount' random images as vectors with answers"""
        training_set = DataImage.objects.filter(test_set=False).order_by('?')

        imgs = []
        labels = []

        for img in training_set:
            file = BytesIO(urlopen(img.url).read())
            image = Image.open(file)

            img_vector = []
            for pixel in image:
                img_vector.append(pixel[0]/255)

            imgs.append(img_vector)
            labels.append(int(img.is_car))

        imgs = tf.constant(imgs)
        labels = tf.constant(labels)

        return imgs, labels
