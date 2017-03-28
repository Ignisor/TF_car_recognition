import mongoengine

mongoengine.connect('cars_db', 'localhost')


class Image(mongoengine.Document):
    url = mongoengine.URLField(primary_key=True)
    is_car = mongoengine.BooleanField()
    test_set = mongoengine.BooleanField()