from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import PracticeTest

class PracticeTestSerializer(DocumentSerializer):
    class Meta:
        model = PracticeTest
        fields = "__all__"
