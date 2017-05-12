from urllib.request import urlopen
from io import BytesIO

from PIL import Image as PIL_Image

import mongoengine

mongoengine.connect('cars_db', 'default')


class Image(mongoengine.Document):
    url = mongoengine.URLField(primary_key=True)
    is_car = mongoengine.BooleanField()
    test_set = mongoengine.BooleanField()
    brand = mongoengine.StringField(max_length=256)
    vector = mongoengine.ListField(mongoengine.FloatField(), null=True)

    def get(self):
        file = BytesIO(urlopen(self.url).read())
        image = PIL_Image.open(file)

        image = image.resize((64, 64))

        return image

    def get_vector(self):
        print(bool(self.vector))
        if self.vector:
            return self.vector

        image = self.get()
        vector = []

        for pixel in image.getdata():
            vector.append(pixel[0] / 255)

        self.vector = vector
        self.save()

        return self.vector
