import json
import io
import csv
import re
import random
from datetime import datetime, timedelta
from bson import ObjectId

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from common.middleware import authenticate, restrict
from exams.models import Question
from exams.models import Exam
# from exams.models import TestAttempt
from categories.models import TestCategory 
from users.models import User
from practice_tests.models import PracticeTest
from exams.models import Question, Exam, TestAttempt, QuestionBank
from practice_tests.models import PracticeTest


# -------------------------------
# CREATE QUESTION
# -------------------------------
@csrf_exempt
@authenticate
@restrict(['admin'])
def create_question(request):
    """
    ✅ Create a new question linked to a PracticeTest.
    Required fields:
        category_id, question_text, question_type, options, correct_answers
    """
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))

        # ✅ Required fields check
        required_fields = ["category_id", "question_text", "question_type", "options", "correct_answers"]
        for field in required_fields:
            if field not in data:
                return JsonResponse({"success": False, "message": f"{field} is required"}, status=400)

        # ✅ Parse options and correct_answers if they are JSON strings
        if isinstance(data['options'], str):
            data['options'] = json.loads(data['options'])
        if isinstance(data['correct_answers'], str):
            data['correct_answers'] = json.loads(data['correct_answers'])

        # ✅ Validate category_id
        category_id = data['category_id']
        if not ObjectId.is_valid(category_id):
            return JsonResponse({"success": False, "message": "Invalid category ID"}, status=400)

        try:
            category = PracticeTest.objects.get(id=ObjectId(category_id))
        except PracticeTest.DoesNotExist:
            return JsonResponse({"success": False, "message": "PracticeTest not found"}, status=404)

        # ✅ Validate options
        options = data['options']
        if not isinstance(options, list) or len(options) < 2:
            return JsonResponse({"success": False, "message": "At least 2 options are required"}, status=400)

        # ✅ Validate correct answers (must be strings that exist in options)
        correct_answers = data['correct_answers']
        if not isinstance(correct_answers, list) or len(correct_answers) == 0:
            return JsonResponse({"success": False, "message": "At least one correct answer is required"}, status=400)

        for ans in correct_answers:
            if ans not in options:
                return JsonResponse({"success": False, "message": f"Invalid correct answer: {ans}"}, status=400)

        # ✅ Create and save Question
        question = Question(
            category=category,
            question_text=data['question_text'],
            question_type=data['question_type'],
            options=options,
            correct_answers=correct_answers,  # string answers
            marks=data.get('marks', 1),
            explanation=data.get('explanation', ''),
            tags=data.get('tags', []),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        question.save()

        return JsonResponse({
            "success": True,
            "message": "Question created successfully",
            "question_id": str(question.id)
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON body"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=400)


# -------------------------------
# UPDATE QUESTION
# -------------------------------
@csrf_exempt
@authenticate
@restrict(['admin'])
def update_question(request, question_id):
    if request.method != 'PUT':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        if not ObjectId.is_valid(question_id):
            return JsonResponse({"success": False, "message": "Invalid question ID"}, status=400)

        question = Question.objects.get(id=ObjectId(question_id))
        data = json.loads(request.body.decode('utf-8'))

        for field in ['question_text', 'question_type', 'options', 'correct_answers', 'marks', 'explanation', 'tags']:
            if field in data:
                # ✅ Validate options
                if field == 'options' and (not isinstance(data['options'], list) or len(data['options']) < 2):
                    return JsonResponse({"success": False, "message": "At least 2 options are required"}, status=400)

                # ✅ Validate correct_answers
                if field == 'correct_answers':
                    correct_answers = data['correct_answers']
                    options = data.get('options', question.options)
                    for ans in correct_answers:
                        if ans not in options:
                            return JsonResponse({"success": False, "message": f"Invalid correct answer: {ans}"}, status=400)

                setattr(question, field, data[field])

        question.updated_at = datetime.utcnow()
        question.save()
        return JsonResponse({'success': True, 'message': 'Question updated successfully'})

    except Question.DoesNotExist:
        return JsonResponse({"success": False, "message": "Question not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON body"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


# -------------------------------
# DELETE QUESTION
# -------------------------------
from django.http import JsonResponse
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt
from users.authentication import authenticate, restrict  # adjust import as per your project
from .models import Question


@csrf_exempt
@authenticate
@restrict(['admin'])
def delete_question(request, question_id):
    """
    Delete a question by its ObjectId.
    Accessible only by admin users.
    """
    if request.method != 'DELETE':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        # ✅ Validate ObjectId
        if not ObjectId.is_valid(question_id):
            return JsonResponse({"success": False, "message": "Invalid question ID"}, status=400)

        # ✅ Use _id instead of id
        question = Question.objects(_id=ObjectId(question_id)).first()
        if not question:
            return JsonResponse({"success": False, "message": "Question not found"}, status=404)

        # ✅ Delete question
        question.delete()

        return JsonResponse({"success": True, "message": "Question deleted successfully"}, status=200)

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)



# -------------------------------
# BULK DELETE QUESTIONS
# -------------------------------

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from bson import ObjectId
from .models import Question
from common.middleware import authenticate, restrict  # adjust your actual import paths

from bson import ObjectId
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Question
from common.middleware import authenticate, restrict  # adjust import to your project

@csrf_exempt
@authenticate
@restrict(['admin'])
def bulk_delete_questions(request):
    if request.method != 'DELETE':
        return JsonResponse(
            {"success": False, "message": "Method not allowed"},
            status=405
        )

    try:
        data = json.loads(request.body.decode('utf-8'))
        question_ids = data.get('question_ids', [])

        if not question_ids:
            return JsonResponse(
                {"success": False, "message": "No question IDs provided"},
                status=400
            )

        # ✅ Validate ObjectIds
        valid_ids = []
        for qid in question_ids:
            try:
                valid_ids.append(ObjectId(qid))
            except Exception:
                return JsonResponse(
                    {"success": False, "message": f"Invalid question ID: {qid}"},
                    status=400
                )

        # ✅ Use `pk__in` or `id__in` is wrong for MongoEngine
        # Use filter with id=ObjectId instead
        deleted_result = Question.objects(_id__in=valid_ids).delete()  # ✅ FIXED

        # `.delete()` returns an int in MongoEngine (count of deleted)
        deleted_count = deleted_result if isinstance(deleted_result, int) else deleted_result[0]

        return JsonResponse(
            {"success": True, "message": f"{deleted_count} question(s) deleted successfully"},
            status=200
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON body"}, status=400)

    except Exception as e:
        print("❌ Bulk delete error:", str(e))
        return JsonResponse({"success": False, "message": str(e)}, status=500)


# -------------------------------
# GET QUESTION BY ID
# -------------------------------
@csrf_exempt
@authenticate
@restrict(['admin'])
def get_question_by_id(request, question_id):
    if request.method != 'GET':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        if not ObjectId.is_valid(question_id):
            return JsonResponse({"success": False, "message": "Invalid question ID"}, status=400)

        question = Question.objects.get(id=ObjectId(question_id))
        question_data = {
            'id': str(question.id),
            'category_id': str(question.category.id),
            'category_name': getattr(question.category, 'name', ''),
            'question_text': question.question_text,
            'question_type': question.question_type,
            'options': question.options,
            'correct_answers': question.correct_answers,
            'marks': question.marks,
            'explanation': question.explanation,
            'tags': question.tags,
            'created_at': question.created_at.isoformat() if question.created_at else None,
            'updated_at': question.updated_at.isoformat() if question.updated_at else None
        }
        return JsonResponse({"success": True, "question": question_data}, status=200)

    except Question.DoesNotExist:
        return JsonResponse({"success": False, "message": "Question not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


# -------------------------------
# GET QUESTIONS (BY CATEGORY)
# -------------------------------
@csrf_exempt
# @authenticate
# @restrict(['admin'])
def get_questions(request):
    """Fetch all questions for a category (Admin only)."""
    if request.method != 'GET':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        category_id = request.GET.get('category_id')
        if not category_id:
            return JsonResponse({"success": False, "message": "category_id is required"}, status=400)

        if not ObjectId.is_valid(category_id):
            return JsonResponse({"success": False, "message": "Invalid category_id"}, status=400)

        questions = Question.objects.filter(category=ObjectId(category_id))

        question_list = [{
            'id': str(q.id),
            'question_text': q.question_text,
            'question_type': q.question_type,
            'options': q.options,
            'correct_answers': q.correct_answers,
            'marks': getattr(q, 'marks', 1),
            'category_id': str(q.category.id) if getattr(q, 'category', None) else None,
            'category_name': getattr(q.category, 'name', ''),
            'explanation': getattr(q, 'explanation', ''),
            'tags': getattr(q, 'tags', []),
            'created_at': q.created_at.isoformat() if getattr(q, 'created_at', None) else ''
        } for q in questions]

        return JsonResponse({"success": True, "questions": question_list}, status=200)

    except Exception as e:
        print("❌ ERROR in get_questions:", e)
        return JsonResponse({"success": False, "message": str(e)}, status=400)


# -------------------------------
# UPLOAD QUESTIONS CSV
# -------------------------------

# @csrf_exempt
# @authenticate
# # @restrict(['admin'])
# def upload_questions_csv(request):
#     print(request.method)
#     """
#     Upload questions in bulk via CSV (Admin only).
#     """
#     if request.method != 'POST':
#         return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

#     try:
#         csv_file = request.FILES.get('csv_file')
#         category_id = request.POST.get('category_id')

#         if not csv_file or not category_id:
#             return JsonResponse(
#                 {"success": False, "message": "CSV file and category_id are required"},
#                 status=400
#             )

#         if not ObjectId.is_valid(category_id):
#             return JsonResponse({"success": False, "message": "Invalid category ID"}, status=400)

#         try:
#             category = PracticeTest.objects.get(id=ObjectId(category_id))
#         except PracticeTest.DoesNotExist:
#             return JsonResponse({"success": False, "message": "PracticeTest not found"}, status=404)

#         csv_data = csv_file.read().decode('utf-8')
#         csv_reader = csv.DictReader(io.StringIO(csv_data))

#         questions_created = 0
#         errors = []

#         for row_num, row in enumerate(csv_reader, 1):
#             try:
#                 row = {k.strip(): v.strip() for k, v in row.items() if k and v}
#                 options = [opt.strip() for opt in row['options'].split('|') if opt.strip()]
#                 correct_answers = [
#                     x.strip() for x in re.split(r'[|,]', row['correct_answers']) if x.strip()
#                 ]

#                 Question.objects.create(
#                     category=category,
#                     question_text=row['question_text'],
#                     question_type=row['question_type'],
#                     options=options,
#                     correct_answers=correct_answers,
#                     marks=int(row.get('marks', 1)),
#                     explanation=row.get('explanation', ''),
#                 )
#                 questions_created += 1

#             except Exception as e:
#                 errors.append(f"Row {row_num} Error: {str(e)}")
#                 continue

#         return JsonResponse({
#             'success': True if questions_created > 0 else False,
#             'message': f'{questions_created} question(s) created, {len(errors)} error(s)',
#             'errors': errors
#         })

#     except Exception as e:
#         return JsonResponse({'success': False, 'message': str(e)}, status=400)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.utils import timezone
from django.conf import settings
from bson import ObjectId
import os, csv, io, re

from users.authentication import authenticate
from categories.models import TestCategory
from exams.models import Question, CSVFile


# Directory where CSV files are stored
UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "csv_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ✅ UPLOAD CSV (Admin Only)
@csrf_exempt
# @authenticate
@api_view(["POST"])
def upload_questions_csv(request):
    """
    Upload a CSV file, save it on disk, create a CSVFile record,
    and insert questions into the database.
    """
    try:
        csv_file = request.FILES.get("file") or request.FILES.get("csv_file")
        category_id = request.POST.get("category_id")
        user = getattr(request, "user", None)

        if not csv_file or not category_id:
            return JsonResponse({
                "success": False,
                "message": "CSV file and category_id are required"
            }, status=400)

        if not ObjectId.is_valid(category_id):
            return JsonResponse({
                "success": False,
                "message": "Invalid category ID"
            }, status=400)

        # Fetch category
        category = TestCategory.objects.get(id=ObjectId(category_id))

        # Save file to disk
        filename = f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{csv_file.name}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            for chunk in csv_file.chunks():
                f.write(chunk)

        # Store CSVFile document (store path as string)
        csv_doc = CSVFile(
            category=category,
            file_path=file_path,  # store as string
            uploaded_by=user,
            uploaded_at=timezone.now()
        )
        csv_doc.save()

        # Parse CSV content
        csv_data = csv_file.read().decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(csv_data))

        questions_created = 0
        errors = []

        for row_num, row in enumerate(csv_reader, start=1):
            try:
                row = {k.strip(): v.strip() for k, v in row.items() if k and v}

                # Expected columns: question_text, question_type, options, correct_answers
                question_text = row.get("question_text", "")
                question_type = row.get("question_type", "single")
                options = [opt.strip() for opt in row.get("options", "").split("|") if opt.strip()]
                correct_answers = [
                    x.strip() for x in re.split(r"[|,]", row.get("correct_answers", "")) if x.strip()
                ]
                marks = int(row.get("marks", 1))
                explanation = row.get("explanation", "")

                if not question_text or not options:
                    raise ValueError("Missing question_text or options")

                Question.objects.create(
                    category=category,
                    question_text=question_text,
                    question_type=question_type,
                    options=options,
                    correct_answers=correct_answers,
                    marks=marks,
                    explanation=explanation,
                )
                questions_created += 1
            except Exception as e:
                errors.append(f"Row {row_num} Error: {str(e)}")

        return JsonResponse({
            "success": True,
            "message": f"{questions_created} question(s) created, {len(errors)} error(s)",
            "errors": errors,
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=400)


# ✅ GET CSV FILES BY CATEGORY
@csrf_exempt
#@authenticate
@api_view(["GET"])
def get_csv_files(request):
    """
    Fetch all uploaded CSV files for a given category.
    """
    try:
        category_id = request.GET.get("category_id")
        if not category_id:
            return JsonResponse({
                "success": False,
                "message": "category_id is required"
            }, status=400)

        if not ObjectId.is_valid(category_id):
            return JsonResponse({
                "success": False,
                "message": "Invalid category ID"
            }, status=400)

        csv_files = CSVFile.objects(category=ObjectId(category_id))
        data = []

        for f in csv_files:
            data.append({
                "id": str(f.id),
                "filename": os.path.basename(f.file_path),
                "uploaded_at": f.uploaded_at.isoformat() if f.uploaded_at else None,
                "uploaded_by": str(f.uploaded_by.id) if getattr(f, "uploaded_by", None) else None,
            })

        return JsonResponse({
            "success": True,
            "files": data
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=400)


# ✅ DELETE CSV FILE (and related questions)
@csrf_exempt
#@authenticate
@api_view(["DELETE"])
def delete_csv_file(request, csv_id):
    """
    Delete a CSV file and all questions in that file's category.
    """
    try:
        if not ObjectId.is_valid(csv_id):
            return JsonResponse({
                "success": False,
                "message": "Invalid CSV ID"
            }, status=400)

        csv_doc = CSVFile.objects.get(id=ObjectId(csv_id))
        file_path = csv_doc.file_path

        # Delete file from disk
        if os.path.exists(file_path):
            os.remove(file_path)

        # Optionally delete related questions in that category
        Question.objects(category=csv_doc.category).delete()

        # Delete CSV record
        csv_doc.delete()

        return JsonResponse({
            "success": True,
            "message": "CSV file and related questions deleted successfully"
        })

    except CSVFile.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "CSV file not found"
        }, status=404)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=400)




# ----------------------------
# EXAM & TEST ATTEMPTS
# ----------------------------
@csrf_exempt
# @authenticate   
@restrict(['admin'])
def create_exam(request):
    """✅ Create a new exam linked to a TestCategory."""
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))

        # ✅ Required fields validation
        required_fields = ['category_id', 'title', 'duration', 'questions_per_test']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({"success": False, "message": f"{field} is required"}, status=400)

        # ✅ Validate category_id
        category_id = data['category_id']
        if not ObjectId.is_valid(category_id):
            return JsonResponse({"success": False, "message": "Invalid category ID"}, status=400)

        try:
            category = TestCategory.objects.get(id=ObjectId(category_id))
        except TestCategory.DoesNotExist:
            return JsonResponse({"success": False, "message": "Category not found"}, status=404)

        # ✅ Create Exam object
        exam = Exam(
            category=category,
            title=data['title'],
            description=data.get('description', ''),
            duration=int(data['duration']),
            questions_per_test=int(data['questions_per_test']),
            passing_score=float(data.get('passing_score', 60.0)),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        exam.save()

        return JsonResponse({
            "success": True,
            "message": "Exam created successfully",
            "exam_id": str(exam.id)
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON body"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=400)


from datetime import datetime
import random
from bson import ObjectId

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from users.models import User
from exams.models import Question, Exam, TestAttempt, QuestionBank
from practice_tests.models import PracticeTest


@csrf_exempt
@authenticate  # only check if the user is authenticated
def start_test(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        user = request.user
        exam_id = data.get("exam_id")
        category_id = data.get("category_id")

        if not category_id:
            return JsonResponse({"success": False, "message": "category_id is required"}, status=400)

        # ✅ Fetch category and exam (if given)
        category = PracticeTest.objects.get(id=ObjectId(category_id))
        exam = Exam.objects.get(id=ObjectId(exam_id)) if exam_id else None

        # ✅ Get ALL questions linked to this category
        all_questions = list(Question.objects(category=category))
        if not all_questions:
            return JsonResponse({"success": False, "message": "No questions found in this category"}, status=404)

        # ✅ Show ALL questions (not limited)
        selected_questions = all_questions

        # ✅ (Optional) Shuffle question order
        import random
        random.shuffle(selected_questions)

        formatted_questions = [
            {
                "id": str(q.id),
                "question_text": q.question_text,
                "question_type": q.question_type,
                "options": json.loads(q.options) if isinstance(q.options, str) else (q.options or []),
                "correct_answers": json.loads(q.correct_answers) if isinstance(q.correct_answers, str) else (q.correct_answers or []),
                "marks": q.marks,
                "explanation": q.explanation or "",
            } for q in selected_questions
        ]

        # ✅ Create test attempt
        attempt = TestAttempt.objects.create(
            user=user,
            exam=exam,
            category=category,
            questions=formatted_questions,
            total_marks=sum(q.marks for q in selected_questions),
            time_limit=getattr(exam, 'duration', 30) if exam else getattr(category, 'duration', 30),
            start_time=datetime.utcnow(),
            is_completed=False
        )

        # ✅ Include category/test info
        category_name = getattr(category.category, 'name', '') if hasattr(category, 'category') else getattr(category, 'title', 'Practice Test')
        test_name = getattr(exam, 'title', category.title if hasattr(category, 'title') else 'Practice Test') if exam else getattr(category, 'title', 'Practice Test')
        description = getattr(category, 'description', '') if hasattr(category, 'description') else (getattr(exam, 'description', '') if exam else '')

        # ✅ Return navigable structure
        return JsonResponse({
            "success": True,
            "message": "Test started successfully",
            "attempt_id": str(attempt.id),
            "questions": formatted_questions,
            "total_questions": len(formatted_questions),
            "current_question_index": 0,  # frontend starts here
            "time_limit": attempt.time_limit,
            "category_name": category_name,
            "test_name": test_name,
            "description": description
        }, status=201)

    except PracticeTest.DoesNotExist:
        return JsonResponse({"success": False, "message": "Category not found"}, status=404)
    except Exam.DoesNotExist:
        return JsonResponse({"success": False, "message": "Exam not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)



# -----------------------------
# SUBMIT TEST
# -----------------------------
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json
from bson import ObjectId

@csrf_exempt
# @authenticate
def submit_test(request, attempt_id):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        # Parse JSON body
        data = json.loads(request.body)
        user_answers = data.get("user_answers", [])

        # Get the TestAttempt using id field (your model uses id as primary key)
        attempt = TestAttempt.objects.get(_id=ObjectId(attempt_id))


        total_score = 0

        # Loop through user answers
        for ans in user_answers:
            question_id = ans.get("question_id")
            selected = ans.get("selected_answers", [])

            # Query Question using id field
            question = Question.objects.get(_id=ObjectId(question_id))
            if not question:
                return JsonResponse({"success": False, "message": "Question not found"}, status=404)

            # Compare answers
            if sorted(selected) == sorted(question.correct_answers):
                total_score += question.marks

        # Calculate percentage
        percentage = (total_score / attempt.total_marks) * 100 if attempt.total_marks else 0
        passing_score = getattr(attempt, "exam", None).passing_score if getattr(attempt, "exam", None) else 60.0
        passed = percentage >= passing_score

        # Update attempt
        attempt.update(
            set__user_answers=user_answers,
            set__score=total_score,
            set__percentage=percentage,
            set__passed=passed,
            set__is_completed=True,
            set__end_time=datetime.utcnow()
        )

        return JsonResponse({
            "success": True,
            "message": "Test submitted successfully",
            "score": total_score,
            "percentage": round(percentage, 2),
            "passed": passed
        }, status=200)

    except TestAttempt.DoesNotExist:
        return JsonResponse({"success": False, "message": "Attempt not found"}, status=404)
    except Exception as e:
        print(e)
        return JsonResponse({"success": False, "message": str(e)}, status=400)



# -----------------------------
# GET TEST RESULT
# -----------------------------
# -----------------------------
# GET TEST RESULT
# -----------------------------
@csrf_exempt
# @authenticate
def get_test_result(request, attempt_id):
    if request.method != 'GET':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        attempt = TestAttempt.objects.no_dereference().get(_id=ObjectId(attempt_id))
        raw_data = attempt.to_mongo().to_dict()

        user_id = None
        category_id = None

        if "user" in raw_data and isinstance(raw_data["user"], dict):
            user_id = str(raw_data["user"].get("$id")) if "$id" in raw_data["user"] else str(raw_data["user"])
        elif isinstance(raw_data.get("user"), ObjectId):
            user_id = str(raw_data["user"])

        if "category" in raw_data and isinstance(raw_data["category"], dict):
            category_id = str(raw_data["category"].get("$id")) if "$id" in raw_data["category"] else str(raw_data["category"])
        elif isinstance(raw_data.get("category"), ObjectId):
            category_id = str(raw_data["category"])

        result = {
            "user": user_id,
            "category": category_id,
            "score": raw_data.get("score", 0),
            "total_marks": raw_data.get("total_marks", 0),
            "percentage": raw_data.get("percentage", 0),
            "passed": raw_data.get("passed", False),
            "start_time": str(raw_data.get("start_time")),
            "end_time": str(raw_data.get("end_time")),
        }

        return JsonResponse({"success": True, "result": result}, status=200)

    except TestAttempt.DoesNotExist:
        return JsonResponse({"success": False, "message": "Attempt not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mongoengine.errors import DoesNotExist, ValidationError
from bson import ObjectId
from .models import TestAttempt


@csrf_exempt
def get_attempt_questions(request, attempt_id):
    """
    ✅ Fetch all questions for a given TestAttempt document.
    Includes user-selected answers, correct answers, and explanation.
    """
    try:
        # ✅ Ensure attempt_id is valid ObjectId
        if not ObjectId.is_valid(attempt_id):
            return JsonResponse({
                "success": False,
                "message": "Invalid attempt ID format"
            }, status=400)

        # ✅ Fetch using pk/ObjectId (correct for MongoEngine)
        attempt = TestAttempt.objects.get(pk=ObjectId(attempt_id))

        # ✅ Ensure questions exist
        if not hasattr(attempt, "questions") or not isinstance(attempt.questions, list):
            return JsonResponse({
                "success": False,
                "message": "No questions found for this attempt."
            }, status=404)

        questions_data = []

        for q in attempt.questions:
            question_id = str(q.get("question_id", ""))
            question_text = q.get("question_text", "")
            options = q.get("options", [])
            correct_answers = q.get("correct_answers", [])
            user_selected_answers = q.get("user_selected_answers", [])
            marks = q.get("marks", 1)
            explanation = q.get("explanation", "")

            # ✅ Determine correctness
            is_correct = set(correct_answers) == set(user_selected_answers)
            marks_awarded = marks if is_correct else 0

            questions_data.append({
                "question_id": question_id,
                "question_text": question_text,
                "options": options,
                "correct_answers": correct_answers,
                "user_selected_answers": user_selected_answers,
                "is_correct": is_correct,
                "marks": marks,
                "marks_awarded": marks_awarded,
                "explanation": explanation,
            })

        return JsonResponse({
            "success": True,
            "questions": questions_data
        }, status=200)

    except TestAttempt.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Attempt not found."
        }, status=404)

    except ValidationError:
        return JsonResponse({
            "success": False,
            "message": "Invalid ObjectId."
        }, status=400)

    except Exception as e:
        print("❌ Error in get_attempt_questions:", e)
        return JsonResponse({
            "success": False,
            "message": f"Internal server error: {str(e)}"
        }, status=500)




from django.http import JsonResponse
# from .models import Attempt, QuestionAttempt

def get_result_summary(request, attempt_id):
    try:
        attempt = Attempt.objects.get(id=attempt_id)
        result_data = {
            "result": {
                "score": attempt.score,
                "total_marks": attempt.total_marks,
                "percentage": attempt.percentage,
                "passed": attempt.passed,
            }
        }
        return JsonResponse(result_data, status=200)
    except Attempt.DoesNotExist:
        return JsonResponse({"error": "Attempt not found"}, status=404)





# -----------------------------
# CREATE QUESTION BANK
# -----------------------------
@csrf_exempt
#@authenticate
def create_question_bank(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        category_id = data.get("category")
        if not category_id:
            return JsonResponse({"success": False, "message": "category is required"}, status=400)

        category = PracticeTest.objects.get(id=ObjectId(category_id))
        question_ids = data.get("question_ids", [])
        questions = [Question.objects.get(id=ObjectId(qid)) for qid in question_ids]

        qb = QuestionBank.objects.create(
            category=category,
            name=data.get("name"),
            description=data.get("description", ""),
            questions=questions,
            total_questions=len(questions)
        )
        return JsonResponse({"success": True, "message": "Question bank created", "id": str(qb.id)}, status=201)

    except PracticeTest.DoesNotExist:
        return JsonResponse({"success": False, "message": "Category not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)



