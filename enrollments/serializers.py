from rest_framework import serializers
from .models import Enrollment

class EnrollmentSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user_name = serializers.CharField(max_length=100)
    course_name = serializers.CharField(max_length=200)
    duration_months = serializers.IntegerField()
    enrolled_date = serializers.DateField()
    expiry_date = serializers.DateField()

    def create(self, validated_data):
        enrollment = Enrollment(**validated_data)
        enrollment.save()
        return enrollment
