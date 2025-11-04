from mongoengine import Document, StringField, BooleanField, IntField

class AdminSettings(Document):
    site_name = StringField(default="PrepTara")
    admin_email = StringField(default="admin@preptara.com")
    email_notifications = BooleanField(default=True)
    maintenance_mode = BooleanField(default=False)
    default_user_role = StringField(default="user", choices=["user", "moderator", "admin"])
    session_timeout = IntField(default=30)

    meta = {'collection': 'admin_settings'}
