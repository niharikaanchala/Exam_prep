# # import json
# # from rest_framework.response import Response
# # from rest_framework import status
# # from .serializers import EnrollmentSerializer
# # from django.http import JsonResponse
# # from bson import ObjectId
# # from bson.errors import InvalidId
# # from common.middleware import authenticate
# # from django.views.decorators.csrf import csrf_exempt
# # from .models import Enrollment  
# # from users.models import User

# # @csrf_exempt
# # @authenticate
# # def create_enrollment(request):
# #     """Create a new enrollment."""
# #     if request.method != "POST":
# #         return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

# #     try:
# #         data = json.loads(request.body)
# #         userId = request.user['id']  # from authenticate decorator
# #         user = User.Objects.get(id=userId)
# #         user_name = user.get("fullname")

# #         # Inject user_name into data for serializer
# #         data["user_name"] = user_name

# #         serializer = EnrollmentSerializer(data=data)
# #         if serializer.is_valid():
# #             enrollment = serializer.save()
# #             return JsonResponse({
# #                 "success": True,
# #                 "message": "Enrollment created successfully.",
# #                 "data": {
# #                     "id": str(enrollment.id),
# #                     "user_name": enrollment.user_name,
# #                     "course_name": enrollment.course_name,
# #                     "duration_months": enrollment.duration_months,
# #                     "enrolled_date": str(enrollment.enrolled_date),
# #                     "expiry_date": str(enrollment.expiry_date),
# #                 }
# #             }, status=201)

# #         return JsonResponse({
# #             "success": False,
# #             "message": "Invalid data",
# #             "errors": serializer.errors
# #         }, status=400)

# #     except Exception as e:
# #         print(e)
# #         return JsonResponse({
# #             "success": False,
# #             "message": "An error occurred while creating enrollment",
# #             "error": str(e)
# #         }, status=500)

# import json
# from rest_framework.response import Response
# from rest_framework import status
# from django.http import JsonResponse
# from bson import ObjectId
# from bson.errors import InvalidId
# from common.middleware import authenticate
# from django.views.decorators.csrf import csrf_exempt
# from .serializers import EnrollmentSerializer
# from .models import Enrollment  
# import datetime
# from users.models import User
# from practice_tests.models import PracticeTest




# @csrf_exempt
# @authenticate
# def create_enrollment(request):
#     """Create a new enrollment (only if not already enrolled)."""
#     if request.method != "POST":
#         return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

#     try:
#         user_id = request.user.get("id")
#         data = json.loads(request.body)
#         category_id = data.get("category_id")   # ✅ category id from frontend
#         print(category_id)
#         duration_months = data.get("duration_months")
#         print(duration_months)
#         if not category_id or not duration_months:
#             return JsonResponse({"success": False, "message": "Missing fields"}, status=400)

#         # ✅ Find the category
#         from categories.models import TestCategory
#         category = TestCategory.objects(id=ObjectId(category_id)).first()
#         if not category:
#             return JsonResponse({"success": False, "message": "Category not found"}, status=404)

#         # ✅ Check if already enrolled
#         existing = Enrollment.objects(user_name=user_id, category=category).first()
#         if existing:
#             return JsonResponse({
#                 "success": False,
#                 "message": "You are already enrolled in this course!"
#             }, status=400)

#         # ✅ Create new enrollment
#         enrolled_date = datetime.date.today()
#         expiry_date = enrolled_date + datetime.timedelta(days=30 * int(duration_months))

#         enrollment = Enrollment(
#             user_name=user_id,
#             category=category,
#             duration_months=duration_months,
#             enrolled_date=enrolled_date,
#             expiry_date=expiry_date
#         )
#         enrollment.save()

#         # ✅ Optionally link course to user (if you maintain that)
#         user = User.objects(id=ObjectId(user_id)).first()
#         if user:
#             user.enrolled_courses.append(category)  # now category instead of course_name
#             user.save()

#         return JsonResponse({
#             "success": True,
#             "message": "Enrollment successful",
#             "data": {
#                 "id": str(enrollment.id),
#                 "user_name": user.fullname if user else user_id,
#                 "category": {
#                     "id": str(category.id),
#                     "name": category.name
#                 },
#                 "duration_months": enrollment.duration_months,
#                 "enrolled_date": str(enrollment.enrolled_date),
#                 "expiry_date": str(enrollment.expiry_date)
#             }
#         })

#     except Exception as e:
#         print("❌ Enrollment error:", e)
#         return JsonResponse({"success": False, "message": str(e)}, status=500)




# @csrf_exempt
# @authenticate
# def check_enrollment(request, category_id):
#     """
#     Check if the logged-in user is already enrolled in the given TestCategory.
#     Uses the 'enrolled_courses' list in the User model.
#     """
#     if request.method != "GET":
#         return JsonResponse(
#             {"success": False, "message": "Method not allowed"},
#             status=405
#         )

#     try:
#         # ✅ Always treat category_id as a string
#         course_id = str(category_id)

#         # ✅ Get authenticated user info
#         user_data = request.user
#         userId = request.user['id']
#         print(userId)
#         user = User.objects.get(id=userId)
#         if not user:
#             return JsonResponse(
#                 {"already_enrolled": False, "error": "User not found"},
#                 status=404
#             )

#         # ✅ Check if the category ID exists in enrolled_courses
#         enrolled = any(str(course.id) == course_id for course in user.enrolled_courses)

#         return JsonResponse({"already_enrolled": enrolled}, status=200)

#     except Exception as e:
#         # ✅ Handle all errors safely
#         return JsonResponse(
#             {"already_enrolled": False, "error": str(e)},
#             status=200
#         )


# @csrf_exempt
# @authenticate
# def check_enrollment(request, category_id):
#     """
#     ✅ Check if user is enrolled in a course by checking user.enrolled_courses references.
#     """
#     if request.method != "GET":
#         return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

#     try:
#         user_data = request.user or {}
#         user_id = user_data.get("id")

#         if not user_name:
#             return JsonResponse({"already_enrolled": False, "error": "Invalid user"}, status=401)

#         # ✅ Fetch user object
#         user = User.objects.get(id=user_id)
#         if not user:
#             return JsonResponse({"already_enrolled": False, "error": "User not found"}, status=404)

#         # ✅ Check if category_id exists in enrolled_courses
#         enrolled = any(str(course.id) == str(category_id) for course in user.enrolled_courses)

#         return JsonResponse({"already_enrolled": enrolled}, status=200)

#     except Exception as e:
#         return JsonResponse({"already_enrolled": False, "error": str(e)}, status=200)



# @csrf_exempt
# @authenticate
# def check_practice_enrollment(request, practice_id):
#     """
#     ✅ Check if the logged-in user is enrolled in the category
#     linked to a given PracticeTest.
#     """
#     if request.method != "GET":
#         return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

#     try:
#         user_data = request.user or {}
#         user_id = user_data.get("id")

#         if not user_id:
#             return JsonResponse({"already_enrolled": False, "error": "Invalid user"}, status=401)

#         # ✅ Get User object
#         user = User.objects.get(id=user_id)
#         if not user:
#             return JsonResponse({"already_enrolled": False, "error": "User not found"}, status=404)

#         # ✅ Get Practice Test
#         practice = PracticeTest.objects.get(id=practice_id)
#         if not practice:
#             return JsonResponse({"already_enrolled": False, "error": "Practice test not found"}, status=404)

#         # ✅ Get linked Category
#         category = practice.category
#         if not category:
#             return JsonResponse({"already_enrolled": False, "error": "Category not linked"}, status=404)

#         # ✅ Check if enrolled in that category
#         enrolled = any(str(course.id) == str(category.id) for course in user.enrolled_courses)

#         return JsonResponse({"already_enrolled": enrolled}, status=200)

#     except PracticeTest.DoesNotExist:
#         return JsonResponse({"already_enrolled": False, "error": "Practice test not found"}, status=404)
#     except User.DoesNotExist:
#         return JsonResponse({"already_enrolled": False, "error": "User not found"}, status=404)
#     except Exception as e:
#         return JsonResponse({"already_enrolled": False, "error": str(e)}, status=500)





# import json
# import traceback
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Enrollment
# from .serializers import EnrollmentSerializer
# from common.middleware import authenticate, restrict  # assuming you have a custom one

# @csrf_exempt
# @authenticate  # custom decorator that sets request.user
# @restrict(['admin'])
# def get_enrollments(request):
#     """
#     Admin-only: Fetch all enrollments
#     """
#     if request.method != "GET":
#         return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

#     try:
#         user = getattr(request, "user", None)

#         # ✅ Handle missing or invalid user
#         if not user:
#             return JsonResponse({
#                 "success": False,
#                 "message": "Authentication required."
#             }, status=401)

#         # ✅ Only admins allowed
#         if not getattr(user, "is_admin", False):
#             return JsonResponse({
#                 "success": False,
#                 "message": "Unauthorized access. Admins only."
#             }, status=403)

#         # ✅ Fetch and serialize enrollments
#         enrollments = Enrollment.objects.all()
#         serializer = EnrollmentSerializer(enrollments, many=True)

#         return JsonResponse({
#             "success": True,
#             "count": len(serializer.data),
#             "data": serializer.data
#         }, status=200)

#     except Exception as e:
#         print(traceback.format_exc())  # for debugging
#         return JsonResponse({
#             "success": False,
#             "message": "An error occurred while fetching enrollments",
#             "error": str(e)
#         }, status=500)



# @csrf_exempt
# @authenticate
# def get_enrollment_detail(request, enrollment_id):
#     """Fetch a single enrollment by ID."""
#     if request.method != "GET":
#         return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

#     try:
#         enrollment = Enrollment.objects.get(id=enrollment_id)
#         serializer = EnrollmentSerializer(enrollment)
#         return JsonResponse({
#             "success": True,
#             "data": serializer.data
#         }, status=200)

#     except Enrollment.DoesNotExist:
#         return JsonResponse({
#             "success": False,
#             "message": "Enrollment not found"
#         }, status=404)
#     except Exception as e:
#         return JsonResponse({
#             "success": False,
#             "message": "An error occurred while retrieving enrollment",
#             "error": str(e)
#         }, status=500)



# @csrf_exempt
# @authenticate
# def delete_enrollment(request, enrollment_id):
#     """Delete an enrollment (admin use only)."""
#     if request.method != "DELETE":
#         return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

#     try:
#         enrollment = Enrollment.objects.get(id=enrollment_id)
#         enrollment.delete()
#         return JsonResponse({
#             "success": True,
#             "message": "Enrollment deleted successfully"
#         }, status=200)

#     except Enrollment.DoesNotExist:
#         return JsonResponse({
#             "success": False,
#             "message": "Enrollment not found"
#         }, status=404)
#     except Exception as e:
#         return JsonResponse({
#             "success": False,
#             "message": "An error occurred while deleting enrollment",
#             "error": str(e)
#         }, status=500)


# @csrf_exempt
# @authenticate
# def update_enrollment(request, enrollment_id):
#     """Update enrollment details."""
#     if request.method != "PUT":
#         return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

#     from bson import ObjectId
#     import json

#     try:
#         data = json.loads(request.body)
#         enrollment = Enrollment.objects.get(id=ObjectId(enrollment_id))

#         enrollment.user_name = data.get("user_name", enrollment.user_name)
#         enrollment.course_name = data.get("course_name", enrollment.course_name)
#         enrollment.duration_months = data.get("duration_months", enrollment.duration_months)
#         enrollment.enrolled_date = data.get("enrolled_date", enrollment.enrolled_date)
#         enrollment.expiry_date = data.get("expiry_date", enrollment.expiry_date)

#         enrollment.save()

#         return JsonResponse({
#             "success": True,
#             "message": "Enrollment updated successfully",
#             "data": {
#                 "id": str(enrollment.id),
#                 "user_name": enrollment.user_name,
#                 "course_name": enrollment.course_name,
#                 "duration_months": enrollment.duration_months,
#                 "enrolled_date": str(enrollment.enrolled_date),
#                 "expiry_date": str(enrollment.expiry_date)
#             }
#         }, status=200)

#     except Enrollment.DoesNotExist:
#         return JsonResponse({"success": False, "message": "Enrollment not found"}, status=404)
#     except Exception as e:
#         return JsonResponse({"success": False, "message": "An error occurred while updating enrollment", "error": str(e)}, status=500)




     



     # import json
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import EnrollmentSerializer
# from django.http import JsonResponse
# from bson import ObjectId
# from bson.errors import InvalidId
# from common.middleware import authenticate
# from django.views.decorators.csrf import csrf_exempt
# from .models import Enrollment  
# from users.models import User

# @csrf_exempt
# @authenticate
# def create_enrollment(request):
#     """Create a new enrollment."""
#     if request.method != "POST":
#         return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

#     try:
#         data = json.loads(request.body)
#         userId = request.user['id']  # from authenticate decorator
#         user = User.Objects.get(id=userId)
#         user_name = user.get("fullname")

#         # Inject user_name into data for serializer
#         data["user_name"] = user_name

#         serializer = EnrollmentSerializer(data=data)
#         if serializer.is_valid():
#             enrollment = serializer.save()
#             return JsonResponse({
#                 "success": True,
#                 "message": "Enrollment created successfully.",
#                 "data": {
#                     "id": str(enrollment.id),
#                     "user_name": enrollment.user_name,
#                     "course_name": enrollment.course_name,
#                     "duration_months": enrollment.duration_months,
#                     "enrolled_date": str(enrollment.enrolled_date),
#                     "expiry_date": str(enrollment.expiry_date),
#                 }
#             }, status=201)

#         return JsonResponse({
#             "success": False,
#             "message": "Invalid data",
#             "errors": serializer.errors
#         }, status=400)

#     except Exception as e:
#         print(e)
#         return JsonResponse({
#             "success": False,
#             "message": "An error occurred while creating enrollment",
#             "error": str(e)
#         }, status=500)

import json
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from bson import ObjectId
from bson.errors import InvalidId
from common.middleware import authenticate
from django.views.decorators.csrf import csrf_exempt
from .serializers import EnrollmentSerializer
from .models import Enrollment  
import datetime
from users.models import User
from practice_tests.models import PracticeTest




@csrf_exempt
@authenticate
def create_enrollment(request):
    """Create a new enrollment (only if not already enrolled)."""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        user_id = request.user.get("id")
        data = json.loads(request.body)
        print("RAW BODY:", request.body)
        category_id = data.get("category_id")   # ✅ category id from frontend
        print(category_id)
        duration_months = data.get("duration_months")
        print(duration_months)
        if not category_id or not duration_months:
            return JsonResponse({"success": False, "message": "Missing fields"}, status=400)

        # ✅ Find the category
        from categories.models import TestCategory
        category = TestCategory.objects(id=ObjectId(category_id)).first()
        if not category:
            return JsonResponse({"success": False, "message": "Category not found"}, status=404)

        # ✅ Check if already enrolled
        existing = Enrollment.objects(user_name=user_id, category=category).first()
        if existing:
            return JsonResponse({
                "success": False,
                "message": "You are already enrolled in this course!"
            }, status=400)

        # ✅ Create new enrollment
        enrolled_date = datetime.date.today()
        expiry_date = enrolled_date + datetime.timedelta(days=30 * int(duration_months))

        enrollment = Enrollment(
            user_name=user_id,
            category=category,
            duration_months=duration_months,
            enrolled_date=enrolled_date,
            expiry_date=expiry_date
        )
        enrollment.save()

        # ✅ Optionally link course to user (if you maintain that)
        user = User.objects(id=ObjectId(user_id)).first()
        if user:
            user.enrolled_courses.append(category)  # now category instead of course_name
            user.save()

        return JsonResponse({
            "success": True,
            "message": "Enrollment successful",
            "data": {
                "id": str(enrollment.id),
                "user_name": user.fullname if user else user_id,
                "category": {
                    "id": str(category.id),
                    "name": category.name
                },
                "duration_months": enrollment.duration_months,
                "enrolled_date": str(enrollment.enrolled_date),
                "expiry_date": str(enrollment.expiry_date)
            }
        })

    except Exception as e:
        print("❌ Enrollment error:", e)
        return JsonResponse({"success": False, "message": str(e)}, status=500)



@csrf_exempt
@authenticate
def check_enrollment(request, category_id):
    """
    Check if the logged-in user is already enrolled in the given TestCategory.
    Uses the 'enrolled_courses' list in the User model.
    """
    if request.method != "GET":
        return JsonResponse(
            {"success": False, "message": "Method not allowed"},
            status=405
        )

    try:
        # ✅ Always treat category_id as a string
        course_id = str(category_id)

        # ✅ Get authenticated user info
        user_data = request.user
        userId = request.user['id']
        print(userId)
        user = User.objects.get(id=userId)
        if not user:
            return JsonResponse(
                {"already_enrolled": False, "error": "User not found"},
                status=404
            )

        # ✅ Check if the category ID exists in enrolled_courses
        enrolled = any(str(course.id) == course_id for course in user.enrolled_courses)

        return JsonResponse({"already_enrolled": enrolled}, status=200)

    except Exception as e:
        # ✅ Handle all errors safely
        return JsonResponse(
            {"already_enrolled": False, "error": str(e)},
            status=200
        )





@csrf_exempt
@authenticate
def check_practice_enrollment(request, practice_id):
    """
    ✅ Check if the logged-in user is enrolled in the category
    linked to a given PracticeTest.
    """
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        user_data = request.user or {}
        user_id = user_data.get("id")

        if not user_id:
            return JsonResponse({"already_enrolled": False, "error": "Invalid user"}, status=401)

        # ✅ Get User object
        user = User.objects.get(id=user_id)
        if not user:
            return JsonResponse({"already_enrolled": False, "error": "User not found"}, status=404)

        # ✅ Get Practice Test
        practice = PracticeTest.objects.get(id=practice_id)
        if not practice:
            return JsonResponse({"already_enrolled": False, "error": "Practice test not found"}, status=404)

        # ✅ Get linked Category
        category = practice.category
        if not category:
            return JsonResponse({"already_enrolled": False, "error": "Category not linked"}, status=404)

        # ✅ Check if enrolled in that category
        enrolled = any(str(course.id) == str(category.id) for course in user.enrolled_courses)

        return JsonResponse({"already_enrolled": enrolled}, status=200)

    except PracticeTest.DoesNotExist:
        return JsonResponse({"already_enrolled": False, "error": "Practice test not found"}, status=404)
    except User.DoesNotExist:
        return JsonResponse({"already_enrolled": False, "error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"already_enrolled": False, "error": str(e)}, status=500)





import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Enrollment
from .serializers import EnrollmentSerializer
from common.middleware import authenticate, restrict  # assuming you have a custom one

@csrf_exempt
@authenticate
@restrict("admin")
def get_enrollments(request):
    """Admin-only: Fetch all enrollments"""
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        user = getattr(request, "user", None)

        # ✅ Check authentication
        if not user:
            return JsonResponse({
                "success": False,
                "message": "Authentication required."
            }, status=401)

        # ✅ Handle both dict and object cases
        
        # ✅ Fetch all enrollments
        enrollments = Enrollment.objects.all()
        serializer = EnrollmentSerializer(enrollments, many=True)
        print("serializer : ",serializer.data)

        return JsonResponse({
            "success": True,
            "count": len(serializer.data),
            "data": serializer.data
        }, status=200)

    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({
            "success": False,
            "message": "An error occurred while fetching enrollments",
            "error": str(e)
        }, status=500)




@csrf_exempt
@authenticate
def get_enrollment_detail(request, enrollment_id):
    """Fetch a single enrollment by ID."""
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        serializer = EnrollmentSerializer(enrollment)
        return JsonResponse({
            "success": True,
            "data": serializer.data
        }, status=200)

    except Enrollment.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Enrollment not found"
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": "An error occurred while retrieving enrollment",
            "error": str(e)
        }, status=500)



@csrf_exempt
@authenticate
def delete_enrollment(request, enrollment_id):
    """Delete an enrollment (admin use only)."""
    if request.method != "DELETE":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        enrollment.delete()
        return JsonResponse({
            "success": True,
            "message": "Enrollment deleted successfully"
        }, status=200)

    except Enrollment.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Enrollment not found"
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": "An error occurred while deleting enrollment",
            "error": str(e)
        }, status=500)


@csrf_exempt
@authenticate
def update_enrollment(request, enrollment_id):
    """Update enrollment details."""
    if request.method != "PUT":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    from bson import ObjectId
    import json

    try:
        data = json.loads(request.body)
        enrollment = Enrollment.objects.get(id=ObjectId(enrollment_id))

        enrollment.user_name = data.get("user_name", enrollment.user_name)
        enrollment.course_name = data.get("course_name", enrollment.course_name)
        enrollment.duration_months = data.get("duration_months", enrollment.duration_months)
        enrollment.enrolled_date = data.get("enrolled_date", enrollment.enrolled_date)
        enrollment.expiry_date = data.get("expiry_date", enrollment.expiry_date)

        enrollment.save()

        return JsonResponse({
            "success": True,
            "message": "Enrollment updated successfully",
            "data": {
                "id": str(enrollment.id),
                "user_name": enrollment.user_name,
                "course_name": enrollment.course_name,
                "duration_months": enrollment.duration_months,
                "enrolled_date": str(enrollment.enrolled_date),
                "expiry_date": str(enrollment.expiry_date)
            }
        }, status=200)

    except Enrollment.DoesNotExist:
        return JsonResponse({"success": False, "message": "Enrollment not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": "An error occurred while updating enrollment", "error": str(e)}, status=500)


@csrf_exempt
@authenticate
def get_user_enrollments(request):
    """Get all enrollments for the logged-in user with payment info."""
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        user_id = request.user.get('id')
        if not user_id:
            return JsonResponse({
                "success": False,
                "message": "Authentication required."
            }, status=401)

        # Convert userId to ObjectId if needed
        if ObjectId.is_valid(user_id):
            user_obj = User.objects.get(id=ObjectId(user_id))
        else:
            user_obj = User.objects.get(id=user_id)

        # Fetch enrollments for this user
        user_id_str = str(user_obj.id)
        enrollments = Enrollment.objects(user_name=user_id_str)
        
        enrollments_data = []
        for enrollment in enrollments:
            enrollment_dict = {
                "id": str(enrollment.id),
                "category": {
                    "id": str(enrollment.category.id),
                    "name": enrollment.category.name
                } if enrollment.category else None,
                "duration_months": enrollment.duration_months,
                "enrolled_date": str(enrollment.enrolled_date),
                "expiry_date": str(enrollment.expiry_date),
                "payment": None
            }
            # Add payment info if exists
            if enrollment.payment:
                payment = enrollment.payment
                enrollment_dict["payment"] = {
                    "id": str(payment.id),
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "status": payment.status,
                    "paid_at": str(payment.paid_at) if payment.paid_at else None
                }
            enrollments_data.append(enrollment_dict)

        return JsonResponse({
            "success": True,
            "count": len(enrollments_data),
            "data": enrollments_data
        }, status=200)

    except User.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "User not found"
        }, status=404)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({
            "success": False,
            "message": "An error occurred while fetching enrollments",
            "error": str(e)
        }, status=500)


# ==================== RAZORPAY PAYMENT VIEWS ====================

import razorpay
import hashlib
import hmac
from django.conf import settings
from .payment_models import Payment
from datetime import datetime, date, timedelta

@csrf_exempt
@authenticate
def create_razorpay_order(request):
    """Create Razorpay order for enrollment payment"""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        user_id = request.user.get("id")
        category_id = data.get("category_id")
        duration_months = data.get("duration_months")
        amount = data.get("amount")  # Amount in rupees

        if not category_id or not duration_months or not amount:
            return JsonResponse({"success": False, "message": "Missing required fields"}, status=400)

        # Initialize Razorpay client
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Create order
        amount_in_paise = int(float(amount) * 100)  # Convert to paise
        # Generate short receipt (max 40 chars for Razorpay)
        timestamp_str = str(int(datetime.now().timestamp()))
        receipt = f"ENR{user_id[:8]}{category_id[:8]}{timestamp_str[-8:]}"
        receipt = receipt[:40]  # Ensure max 40 chars
        
        order_data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": receipt,
            "notes": {
                "user_id": user_id,
                "category_id": category_id,
                "duration_months": duration_months
            }
        }

        razorpay_order = razorpay_client.order.create(data=order_data)

        # Create payment record
        payment = Payment(
            user_id=user_id,
            razorpay_order_id=razorpay_order['id'],
            amount=float(amount),
            currency="INR",
            status="pending"
        )
        payment.save()

        return JsonResponse({
            "success": True,
            "order_id": razorpay_order['id'],
            "amount": razorpay_order['amount'],
            "currency": razorpay_order['currency'],
            "key_id": settings.RAZORPAY_KEY_ID,
            "payment_id": str(payment.id)
        }, status=200)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@csrf_exempt
@authenticate
def verify_razorpay_payment(request):
    """Verify Razorpay payment and create enrollment"""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        user_id = request.user.get("id")
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")
        payment_id = data.get("payment_id")
        category_id = data.get("category_id")
        duration_months = data.get("duration_months")

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature, payment_id, category_id, duration_months]):
            return JsonResponse({"success": False, "message": "Missing required fields"}, status=400)

        # Get payment record
        payment = Payment.objects.get(id=ObjectId(payment_id))
        if payment.user_id != user_id:
            return JsonResponse({"success": False, "message": "Unauthorized"}, status=403)

        # Verify signature
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != razorpay_signature:
            payment.status = "failed"
            payment.save()
            return JsonResponse({"success": False, "message": "Invalid payment signature"}, status=400)

        # Get category
        from categories.models import TestCategory
        category = TestCategory.objects(id=ObjectId(category_id)).first()
        if not category:
            return JsonResponse({"success": False, "message": "Category not found"}, status=404)

        # Check if already enrolled
        existing = Enrollment.objects(user_name=payment.user_id, category=category).first()
        if existing:
            payment.status = "completed"
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.paid_at = datetime.utcnow()
            payment.save()
            return JsonResponse({
                "success": False,
                "message": "You are already enrolled in this course!"
            }, status=400)

        # Create enrollment
        enrolled_date = date.today()
        expiry_date = enrolled_date + timedelta(days=30 * int(duration_months))

        enrollment = Enrollment(
            user_name=payment.user_id,
            category=category,
            duration_months=duration_months,
            enrolled_date=enrolled_date,
            expiry_date=expiry_date,
            payment=payment
        )
        enrollment.save()

        # Update payment
        payment.enrollment_id = enrollment
        payment.status = "completed"
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.paid_at = datetime.utcnow()
        payment.updated_at = datetime.utcnow()
        payment.save()

        # Update user enrolled courses - handle ObjectId conversion
        if ObjectId.is_valid(payment.user_id):
            user = User.objects(id=ObjectId(payment.user_id)).first()
        else:
            user = User.objects(id=payment.user_id).first()
        if user:
            # Check if category is already in enrolled_courses
            category_ids = [str(c.id) for c in user.enrolled_courses]
            if str(category.id) not in category_ids:
                user.enrolled_courses.append(category)
                user.save()

        return JsonResponse({
            "success": True,
            "message": "Payment verified and enrollment created successfully",
            "enrollment_id": str(enrollment.id)
        }, status=200)

    except Payment.DoesNotExist:
        return JsonResponse({"success": False, "message": "Payment not found"}, status=404)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({"success": False, "message": str(e)}, status=500)


     