from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.authentication import authenticate
from users.models import User
from exams.models import TestAttempt
from enrollments.models import Enrollment
from enrollments.payment_models import Payment
from bson import ObjectId
from mongoengine.errors import DoesNotExist
from practice_tests.models import PracticeTest

# ✅ DASHBOARD STATS
@csrf_exempt
@authenticate
def user_dashboard(request):
    """Get dashboard stats for the logged-in user."""
    if request.method != 'GET':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)
    
    try:
        # request.user is set by @authenticate decorator as a dict
        if not isinstance(request.user, dict):
            return JsonResponse({"success": False, "message": "Authentication required"}, status=401)
        
        user_id = request.user.get("id")
        if not user_id:
            return JsonResponse({"success": False, "message": "Authentication required"}, status=401)

        # Convert userId to ObjectId if needed
        user_obj_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
        
        # Get user object for fullname
        user = User.objects.get(id=user_obj_id)
        
        # Test attempts data - query by user ID directly (user field stores as reference with id)
        test_attempts = TestAttempt.objects(user=user_obj_id)
        total_tests = test_attempts.count()

        # Courses enrolled - use user ID (string) to match enrollment.user_name
        enrollments = Enrollment.objects(user_name=str(user_obj_id))
        unlocked_courses = enrollments.count()

        dashboard_data = {
            "username": user.fullname or "User",
            "total_attempts": total_tests,
            "enrolled_courses": unlocked_courses,
        }

        return JsonResponse({"success": True, "dashboard": dashboard_data}, status=200)

    except User.DoesNotExist:
        return JsonResponse({"success": False, "message": "User not found"}, status=404)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({"success": False, "message": str(e)}, status=500)


# ✅ USER TEST LIST
@csrf_exempt
@authenticate
def user_tests(request):
    """Get all test attempts for the logged-in user."""
    if request.method != 'GET':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)
    
    try:
        # request.user is set by @authenticate decorator as a dict
        if not isinstance(request.user, dict):
            return JsonResponse({"success": False, "message": "Authentication required"}, status=401)
        
        user_id = request.user.get('id')
        if not user_id:
            return JsonResponse({"success": False, "message": "Authentication required"}, status=401)

        # Convert userId to ObjectId if needed for querying
        user_obj_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id

        test_attempts = []

        # ✅ Access raw data using .to_mongo() to safely check user
        for attempt in TestAttempt.objects.all():
            raw_data = attempt.to_mongo().to_dict()
            user_data = raw_data.get("user")

            # Only include attempts where user.id matches
            if isinstance(user_data, dict) and user_data.get("id") == str(user_id):
                test_attempts.append(attempt)

        # ✅ Build response list
        tests = []
        for attempt in test_attempts:
            # --- Fetch PracticeTest title from the referenced category ---
            practice_title = "Untitled Practice Test"
            try:
                if attempt.category:
                    # Force reload from DB to ensure proper dereference
                    practice_test = PracticeTest.objects.get(id=attempt.category.id)
                    practice_title = practice_test.title
            except PracticeTest.DoesNotExist:
                practice_title = "Deleted Practice Test"
            except Exception as e:
                print("Category fetch error:", e)
                practice_title = "Unknown Test"

            # --- Compute status ---
            status = (
                "Completed"
                if getattr(attempt, "is_completed", False)
                else "Pending"
                if getattr(attempt, "percentage", 0) == 0
                else "In Progress"
            )

            # --- Add to response list ---
            tests.append({
                "id": str(attempt.id),
                "title": practice_title,
                "date": attempt.created_at.strftime("%Y-%m-%d"),
                "total_questions": len(getattr(attempt, "questions", [])),
                "answered": len(getattr(attempt, "user_answers", [])),
                "status": status,
            })

        return JsonResponse({"success": True, "tests": tests}, status=200)

    except Exception as e:
        print("error:", e)
        return JsonResponse({"success": False, "message": str(e)}, status=500)


