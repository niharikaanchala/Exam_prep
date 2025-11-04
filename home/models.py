from mongoengine import (
    Document,
    StringField,
    BooleanField,
    FileField,
    IntField,
    FloatField,
    DynamicField
)

class HeroSection(Document):
    title = StringField(required=True, max_length=255)
    subtitle = StringField()
    search_placeholder = StringField(default="Search courses...")
    # background_image = FileField()  # you can store file metadata (GridFS)
    background_image_url = StringField() 
    is_active = BooleanField(default=True)

    meta = {
        "collection": "hero_section"
    }

    def __str__(self):
        return self.title


class AnalyticsStat(Document):
    title = StringField(required=True)  # e.g. "Students found the real exam almost same"
    value = DynamicField(required=True)  # e.g. "94%" or "1056"
    icon = StringField(required=True)   # e.g. "FileCheck", "Users", "TrendingUp"
    gradient = StringField(default="from-blue-500 to-cyan-600")
    is_active = BooleanField(default=True)

    meta = {'collection': 'analytics_stats'}


class Feature(Document):
    title = StringField(required=True)
    description = StringField(required=True)
    icon = StringField(required=True)  # e.g. "BarChart3", "BookOpen"
    gradient = StringField(required=True)  # e.g. "from-blue-500 via-cyan-500 to-teal-600"
    is_active = BooleanField(default=True)

    meta = {"collection": "features"}

    def __str__(self):
        return self.title



class Testimonial(Document):
    name = StringField(required=True)
    role = StringField(required=True)  # e.g., "UPSC CSE 2024"
    text = StringField(required=True)
    image = FileField()  # Admin can upload image/
    image_url = StringField()  # store Cloudinary image URL
    rating = IntField(default=5)
    is_active = BooleanField(default=True)

    meta = {"collection": "testimonials"}

    def __str__(self):
        return self.name



from mongoengine import Document, StringField, DateTimeField
import datetime

class FAQ(Document):
    question = StringField(required=True)
    answer = StringField(required=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {'collection': 'faqs'}


from mongoengine import Document, StringField, BooleanField, FileField, DateTimeField
import datetime

class CTASection(Document):
    heading = StringField(required=True, max_length=255)
    subheading = StringField()  # optional
    button_text_primary = StringField()  # optional
    button_link_primary = StringField()  # optional
    button_text_secondary = StringField()  # optional
    button_link_secondary = StringField()  # optional
    footer_note = StringField()  # optional
    background_image = FileField()  # optional
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        "collection": "cta_section"
    }

    def __str__(self):
        return self.heading


