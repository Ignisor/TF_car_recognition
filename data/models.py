import mongoengine

mongoengine.connect('cars_db', 'default')


class Image(mongoengine.Document):
    url = mongoengine.URLField(primary_key=True)
    is_car = mongoengine.BooleanField()
    test_set = mongoengine.BooleanField()
    brand = mongoengine.StringField(max_length=256)