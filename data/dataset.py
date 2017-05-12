from .models import Image


class ImageSet(object):
    @staticmethod
    def get_batch(amount=None, test=False):
        """Returns 'amount' random images as vectors with answers"""
        training_set = Image.objects.filter(test_set=test).order_by('?')

        if amount:
            training_set = training_set[:amount]

        imgs = []
        labels = []

        i = 0
        for img in training_set:
            i += 1
            print('Processing image {}'.format(i))
            img_vector = img.get_vector()

            imgs.append(img_vector)
            labels.append([int(not img.is_car), int(img.is_car)])

        return imgs, labels
