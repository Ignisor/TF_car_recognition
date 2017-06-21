import time
import random
import pickle

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


class CifarImageSet(object):
    @staticmethod
    def unpickle(file):
        with open(file, 'rb') as fo:
            dict = pickle.load(fo, encoding='bytes')
        return dict

    @staticmethod
    def get_batch(amount=None, test=False):
        if test:
            path = 'data/cifar-10_dataset/test_batch'
        else:
            path = f'data/cifar-10_dataset/data_batch_{random.randrange(1,6)}'

        batch = CifarImageSet.unpickle(path)

        if amount:
            data = batch[b'data']
            data_labels = batch[b'labels']
            left = random.randrange(0, len(data) - amount)
            right = left + amount

            data = data[left:right]
            data_labels = data_labels[left:right]
        else:
            data = batch[b'data']
            data_labels = batch[b'labels']

        images = []
        labels = []
        for image, label in zip(data, data_labels):
            img_vector = []
            for i in range(1024):
                # make image bigger
                pix = (image[i], image[1024 + i], image[2048 + i])
                for _ in range(4):
                    img_vector.append(pix)

            images.append(img_vector)
            labels.append([int(label != 1), int(label == 1)])

        return images, labels
