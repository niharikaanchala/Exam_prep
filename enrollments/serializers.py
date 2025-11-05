from rest_framework import serializers
from .models import Enrollment
from users.models import User
from categories.models import TestCategory
from bson import ObjectId

class EnrollmentSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user_name = serializers.CharField()  # stores user_id as string
    category = serializers.CharField()   # store as string to avoid ObjectId issues
    duration_months = serializers.IntegerField()
    enrolled_date = serializers.DateField()
    expiry_date = serializers.DateField()

    def to_representation(self, obj):
        """Customize API output to include user full name and category name."""
        data = super().to_representation(obj)

        # ✅ Convert ObjectId to string for the enrollment id
        data["id"] = str(obj.id)

        # ✅ Convert user_name (user_id string) → full name
        try:
            user_obj = User.objects(id=ObjectId(obj.user_name)).first()
            data["user_fullname"] = user_obj.fullname if user_obj else "Unknown User"
        except Exception:
            data["user_fullname"] = "Invalid User ID"

        # ✅ Convert category reference → category info
        try:
            if obj.category:
                data["category_id"] = str(obj.category.id)  # convert ObjectId to string
                data["category_name"] = obj.category.name
                data["category_description"] = obj.category.description
                data["category_price"] = obj.category.price
            else:
                data["category_name"] = "Unknown Category"
        except Exception:
            data["category_name"] = "Invalid Category"

        # Optional: remove raw fields
        # del data["user_name"]
        # del data["category"]

        return data



    def create(self, validated_data):
        enrollment = Enrollment(**validated_data)
        enrollment.save()
        return enrollment
