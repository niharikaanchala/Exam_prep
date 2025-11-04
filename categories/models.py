from mongoengine import Document, StringField, IntField, FloatField, BooleanField

class TestCategory(Document):
    name = StringField(required=True, unique=True)
    description = StringField()
    price = FloatField(default=0.0)
    enrollments = IntField(default=0)
    is_active = BooleanField(default=True)

    meta = {"collection": "test_categories"}
