from mongoengine import Document, StringField, IntField, FloatField, DateTimeField, ReferenceField
import datetime
from categories.models import TestCategory  # adjust import path as needed


class PracticeTest(Document):
    slug = StringField(required=True, unique=True)
    title = StringField(required=True)
    category = ReferenceField(TestCategory)  # stores ObjectId reference
    questions = IntField(default=0)
    duration = IntField(default=0)
    avg_score = FloatField(default=0.0)
    attempts = IntField(default=0)
    enrolled_count = IntField(default=0)
    
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {"collection": "practice_tests"}
