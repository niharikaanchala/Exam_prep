from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import TestCategory
from .serializers import TestCategorySerializer

# ✅ List all categories
@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    categories = TestCategory.objects.all()
    serializer = TestCategorySerializer(categories, many=True)
    return Response(serializer.data)

# ✅ Create a new category
@api_view(['POST'])
@permission_classes([AllowAny])
def category_create(request):
    serializer = TestCategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Retrieve a single category by ID
@api_view(['GET'])
@permission_classes([AllowAny])
def category_detail(request, category_id):
    try:
        category = TestCategory.objects.get(id=category_id)
    except TestCategory.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = TestCategorySerializer(category)
    return Response(serializer.data)

# ✅ Update a category
@api_view(['PUT'])
@permission_classes([AllowAny])
def category_update(request, category_id):
    try:
        category = TestCategory.objects.get(id=category_id)
    except TestCategory.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = TestCategorySerializer(category, data=request.data, partial=True)  # partial=True allows partial updates
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Delete a category
@api_view(['DELETE'])
@permission_classes([AllowAny])
def category_delete(request, category_id):
    try:
        category = TestCategory.objects.get(id=category_id)
    except TestCategory.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    category.delete()
    return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_category_by_id(request, id):
    category = TestCategory.objects.filter(id=id).first()  # or .get(id=id) with try/except
    if not category:
        return Response({"error": "Category not found"}, status=404)
    serializer = TestCategorySerializer(category)
    return Response(serializer.data)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TestCategory
from common.middleware import authenticate, restrict



@csrf_exempt
@authenticate
@restrict(['admin'])
def analytics_overview(request):
    """
    Admin-only Analytics Dashboard
    Provides total/active courses, enrollment data, revenue, and top-performing courses.
    """

    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Method Not Allowed"}, status=405)

    try:
        # Convert user dict (from authenticate decorator) into object
        if isinstance(request.user, dict):
            class UserObj:
                def __init__(self, data):
                    self.__dict__.update(data)
            request.user = UserObj(request.user)

        # Fetch all categories
        categories = TestCategory.objects.all()

        total_courses = categories.count()
        active_courses = categories.filter(is_active=True).count()

        enrollment_per_course = []
        revenue_per_course = []

        # Build course-wise analytics
        for c in categories:
            enrollment_per_course.append({
                "course": c.name,
                "students": getattr(c, "enrollments", 0),
            })
            price = getattr(c, "price", 0)
            enrollments = getattr(c, "enrollments", 0)
            revenue_per_course.append({
                "course": c.name,
                "revenue": f"₹{round((price * enrollments) / 100000, 1)}L"
            })

        top_courses = sorted(enrollment_per_course, key=lambda x: x["students"], reverse=True)[:5]

        data = {
            "success": True,
            "totalCourses": total_courses,
            "activeCourses": active_courses,
            "enrollmentPerCourse": enrollment_per_course,
            "revenuePerCourse": revenue_per_course,
            "topCourses": top_courses,
        }

        return JsonResponse(data, status=200)

    except Exception as e:
        return JsonResponse(
            {"success": False, "error": str(e)},
            status=500,
        )
