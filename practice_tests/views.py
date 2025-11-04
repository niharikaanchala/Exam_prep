from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import PracticeTest
from categories.models import TestCategory
from .serializers import PracticeTestSerializer


# ✅ Get all tests
@api_view(["GET"])
@permission_classes([AllowAny])
def get_all_tests(request):
    """
    Fetch all practice tests. If any test has an invalid category reference,
    it will be skipped (to avoid 500 errors).
    """
    valid_tests = []
    for test in PracticeTest.objects:
        try:
            _ = test.category.id  # try to access to ensure category exists
            valid_tests.append(test)
        except Exception:
            # skip broken references
            continue

    serializer = PracticeTestSerializer(valid_tests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ✅ Get a single test by slug
@api_view(["GET"])
@permission_classes([AllowAny])
def get_test_by_slug(request, slug):
    """
    Fetch a specific practice test by its slug.
    """
    test = PracticeTest.objects(slug=slug).first()
    if not test:
        return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = PracticeTestSerializer(test)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ✅ Create a new test
@api_view(["POST"])
def create_test(request):
    """
    Create a new practice test. The request must include a valid `category_id`.
    Example:
    {
        "slug": "web-dev-basics",
        "title": "Web Development Basics",
        "category_id": "671ffb12abc12345def67890",
        "questions": 10,
        "duration": 30
    }
    """
    category_id = request.data.get("category_id")
    if not category_id:
        return Response({"error": "category_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        category = TestCategory.objects.get(id=category_id)
    except TestCategory.DoesNotExist:
        return Response({"error": "Invalid category_id"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data["category"] = str(category.id) 

    serializer = PracticeTestSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Update an existing test
@api_view(["PUT"])
def update_test(request, slug):
    """
    Update details of a specific practice test.
    You can also update its category by passing `category_id`.
    """
    test = PracticeTest.objects(slug=slug).first()
    if not test:
        return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()

    # Handle category update if provided
    category_id = data.get("category_id")
    if category_id:
        try:
            category = TestCategory.objects.get(id=category_id)
            data["category"] = category
        except TestCategory.DoesNotExist:
            return Response({"error": "Invalid category_id"}, status=status.HTTP_404_NOT_FOUND)

    serializer = PracticeTestSerializer(test, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Delete a test
@api_view(["DELETE"])
def delete_test(request, slug):
    """
    Delete a specific practice test.
    """
    test = PracticeTest.objects(slug=slug).first()
    if not test:
        return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)

    test.delete()
    return Response({"message": "Test deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# ✅ Get tests by category
@api_view(["GET"])
@permission_classes([AllowAny])
def tests_by_category(request, category_id):
    """
    Get all tests belonging to a specific category.
    """
    try:
        category = TestCategory.objects.get(id=category_id)
    except TestCategory.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    tests = PracticeTest.objects(category=category)
    serializer = PracticeTestSerializer(tests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
