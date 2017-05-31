from time import time
import random

from pymongo import MongoClient

from .models import Image


class ImageSet(object):
    @staticmethod
    def get_set(test=False):
        client = MongoClient('mongodb://localhost:27017')
        db = client.get_database('cars_db')
        collection = db.get_collection('image')

        set = collection.find({'test_set': test})

        return set

    @staticmethod
    def get_batch(amount=None, test=False):
        """Returns 'amount' random images as vectors with answers"""
        set = ImageSet.get_set(test)

        set = list(set)

        if not amount:
            amount = len(set)

        imgs = []
        labels = []

        for i in range(amount):
            img = random.choice(set)

            img_vector = img.get('vector')
            imgs.append(img_vector)
            labels.append([int(not img['is_car']), int(img['is_car'])])

            set.remove(img)

        return imgs, labels
