import time
import random

from pymongo import MongoClient

import numpy
class ImageSet(object):
    @staticmethod
    def get_set(amount=None, test=False):
        client = MongoClient('mongodb://localhost:27017')
        db = client.get_database('cars_db')
        collection = db.get_collection('image')

        ids = collection.distinct('_id', {'test_set': True})
        random.shuffle(ids)

        if amount:
            ids = ids[:amount]

        set = collection.find({'_id': {'$in': ids}})

        return set

    @staticmethod
    def get_batch(amount=None, test=False):
        """Returns 'amount' random images as vectors with answers"""
        set = ImageSet.get_set(amount, test)

        imgs = []
        labels = []

        for img in set:
            img_vector = []

            for pix in zip(img.get('R_vector'), img.get('G_vector'), img.get('B_vector')):
                img_vector.append(pix)

            imgs.append(img_vector)
            labels.append([int(not img['is_car']), int(img['is_car'])])

        return imgs, labels
