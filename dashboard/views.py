from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from users.authentication import authenticate
from users.models import User
from exams.models import TestAttempt
from enrollments.models import Enrollment
from bson import ObjectId
from mongoengine.errors import DoesNotExist

# ✅ DASHBOARD STATS
@csrf_exempt
@authenticate
@api_view(['POST'])
def user_dashboard(request, user_id):
    try:
        if not ObjectId.is_valid(user_id):
            return JsonResponse({"success": False, "message": "Invalid user ID"}, status=400)

        user = User.objects.get(id=ObjectId(user_id))

        # Test attempts data
        test_attempts = TestAttempt.objects(user=user)
        total_tests = test_attempts.count()
        best_score = max((t.percentage for t in test_attempts), default=0)
        avg_score = (
            sum(t.percentage for t in test_attempts) / total_tests
            if total_tests > 0
            else 0
        )

        # Courses enrolled - use user ID (string) to match enrollment.user_name
        enrollments = Enrollment.objects(user_name=str(user.id))
        unlocked_courses = enrollments.count()

        dashboard_data = {
            "username": user.fullname or "User",
            "total_tests": total_tests,
            "best_score": round(best_score, 2),
            "average_score": round(avg_score, 2),
            "unlocked_courses": unlocked_courses,
        }

        return JsonResponse({"success": True, "dashboard": dashboard_data}, status=200)

    except User.DoesNotExist:
        return JsonResponse({"success": False, "message": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


# ✅ USER TEST LIST
@csrf_exempt
@authenticate
@api_view(['GET'])
def user_tests(request, user_id):
    try:
        if not ObjectId.is_valid(user_id):
            return JsonResponse({"success": False, "message": "Invalid user ID"}, status=400)

        user = User.objects.get(id=ObjectId(user_id))
        test_attempts = TestAttempt.objects(user=user)

        tests = []
        for attempt in test_attempts:
            exam_title = ""
            if attempt.exam:
                try:
                    exam_title = attempt.exam.title
                except Exception:
                    exam_title = "Untitled Exam"

            status = (
                "Completed"
                if attempt.is_completed
                else "Pending"
                if attempt.percentage == 0
                else "In Progress"
            )

            tests.append({
                "id": str(attempt.id),
                "title": exam_title or "Practice Test",
                "date": attempt.created_at.strftime("%Y-%m-%d"),
                "total_questions": len(attempt.questions) if attempt.questions else 0,
                "answered": len(attempt.user_answers) if attempt.user_answers else 0,
                "status": status,
            })

        return JsonResponse({"success": True, "tests": tests}, status=200)

    except User.DoesNotExist:
        return JsonResponse({"success": False, "message": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
