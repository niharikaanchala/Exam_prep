# blog/models.py
from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

class Blog(Document):
    title = StringField(required=True, max_length=255)
    excerpt = StringField()
    category = StringField(max_length=100)
    author = StringField(max_length=100)
    date = DateTimeField(default=datetime.utcnow)
    read_time = StringField()
    image_url = StringField()

    meta = {"collection": "blogs"}

    def to_json(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "excerpt": self.excerpt,
            "category": self.category,
            "author": self.author,
            "date": self.date.strftime("%Y-%m-%d"),
            "readTime": self.read_time,
            "image_url": self.image_url,
        }
