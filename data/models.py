from urllib.request import urlopen
from io import BytesIO

from PIL import Image as PIL_Image

import mongoengine

mongoengine.connect('cars_db', 'default')


class Image(mongoengine.Document):
    url = mongoengine.URLField(primary_key=True)
    is_car = mongoengine.BooleanField()
    test_set = mongoengine.BooleanField()
    brand = mongoengine.StringField(max_length=256, null=True)
    vector = mongoengine.ListField(mongoengine.FloatField())

    def get(self):
        file = BytesIO(urlopen(self.url).read())
        image = PIL_Image.open(file)

        image = image.resize((64, 64))

        return image

    def update_vector(self):
        image = self.get()
        vector = []

        for pixel in image.getdata():
            vector.append(pixel[0] / 255)

        self.vector = vector

        return self.vector

    def save(self, force_insert=False, validate=True, clean=True,
             write_concern=None, cascade=None, cascade_kwargs=None,
             _refs=None, save_condition=None, signal_kwargs=None, **kwargs):

        self.update_vector()

        return super(Image, self).save(force_insert, validate, clean,
             write_concern, cascade, cascade_kwargs,
             _refs, save_condition, signal_kwargs, **kwargs)
