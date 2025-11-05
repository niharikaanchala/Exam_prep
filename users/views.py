
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import User, Admin
from .serializers import UserSerializer, AdminSerializer
from django.contrib.auth.hashers import check_password 
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime, timedelta
from django.conf import settings

import jwt
from bson import ObjectId
from django.conf import settings
from users.authentication import authenticate  # custom decorator


# ================= JWT HELPER =================
SECRET_KEY = settings.SECRET_KEY

def generate_jwt(payload):
    """Generate a JWT token with a 7-day expiry."""
    payload["exp"] = datetime.utcnow() + timedelta(days=7)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# ================= REGISTER =================
@api_view(["POST"])
def register_user(request):
    try:
        data = request.data
        email = data.get("email")
        fullname = data.get("fullname", "").strip()
        password = data.get("password")
        phone_number = data.get("phone_number", "").strip()

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects(email=email).first():
            return Response(
                {"error": "Email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Create user
        user = User(
            fullname=fullname if fullname else "Unknown User",
            email=email,
            phone_number=phone_number if phone_number else "N/A",
        )
        user.set_password(password)
        user.save()

        # ✅ Generate JWT token (use consistent key "id")
        token = generate_jwt({"id": str(user.id), "email": user.email, "role": user.role})

        return Response(
            {
                "success": True,
                "message": "User registered successfully.",
                "token": token,
                "user": {
                    "id": str(user.id),
                    "fullname": user.fullname,
                    "email": user.email,
                    "role": user.role,
                    "phone_number": user.phone_number,
                    "location": getattr(user, "location", ""),
                },
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================= LOGIN =================
@api_view(["POST"])
def login_user(request):
    data = request.data
    email = data.get("email")
    password = data.get("password")

    user = User.objects(email=email).first()
    if not user:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if not user.check_password(password):
        return Response(
            {"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED
        )

    # ✅ Generate consistent token
    token = generate_jwt({"id": str(user.id), "role": user.role})

    return Response(
        {
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "id": str(user.id),
                "fullname": user.fullname,
                "email": user.email,
                "role": user.role,
                "phone_number": user.phone_number,
                "location": user.location,
            },
        },
        status=status.HTTP_200_OK,
    )


# ================= CURRENT USER =================
@api_view(["GET"])
@authenticate  # uses token
def current_user(request):
    """Get user info from decoded JWT"""
    try:
        user_id = request.user.get("id")
        user = User.objects.get(id=ObjectId(user_id))

        return Response(
            {
                "id": str(user.id),
                "fullname": user.fullname,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role,
                "location": getattr(user, "location", ""),
            },
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================= USER PROFILE =================
# @api_view(["GET"])
# @authenticate
# def user_profile(request):
#     """Get currently logged-in user's profile."""
#     try:
#         user_id = request.user.get("id")
#         if not user_id:
#             return Response(
#                 {"error": "User ID not found in token"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         user = User.objects.get(id=ObjectId(user_id))

#         return Response(
#             {
#                 "id": str(user.id),
#                 "fullname": user.fullname,
#                 "email": user.email,
#                 "phone_number": user.phone_number,
#                 "role": user.role,
#                 "location": user.location,
#             },
#             status=status.HTTP_200_OK,
#         )

#     except User.DoesNotExist:
#         return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#     except jwt.ExpiredSignatureError:
#         return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
#     except jwt.InvalidTokenError:
#         return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
import jwt
from .models import User, Admin


@api_view(["GET"])
@authenticate
def user_profile(request):
    """Return profile info for logged-in student or admin based on token role."""
    try:
        payload = request.user  # contains {'id': ..., 'role': ..., 'exp': ...}
        print("payload : ",payload)
        user_id = payload.get("id")
        role = payload.get("role")

        if not user_id or not role:
            return Response(
                {"error": "Invalid token payload: missing user ID or role"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ============================
        # 🧩 STUDENT USER
        # ============================
        if role == "student":
            user = User.objects.get(id=ObjectId(user_id))
            user_data = user.to_mongo().to_dict()

            user_data["id"] = str(user_data.pop("_id"))
            user_data["role"] = "student"

            if "enrolled_courses" in user_data:
                user_data["enrolled_courses"] = [
                    str(course.id) for course in user.enrolled_courses
                ]

            user_data.pop("password", None)

            return Response(
                {"success": True, "role": "student", "profile": user_data},
                status=status.HTTP_200_OK,
            )

        # ============================
        # 🧩 ADMIN USER
        # ============================
        elif role == "admin":
            admin = Admin.objects.get(_id=ObjectId(user_id))
            admin_data = admin.to_mongo().to_dict()

            admin_data["id"] = str(admin_data.pop("_id"))
            admin_data["role"] = "admin"
            admin_data.pop("password", None)

            return Response(
                {"success": True, "role": "admin", "profile": admin_data},
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {"error": f"Unknown role '{role}' in token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except User.DoesNotExist:
        return Response({"error": "Student user not found"}, status=status.HTTP_404_NOT_FOUND)
    except Admin.DoesNotExist:
        return Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)
    except jwt.ExpiredSignatureError:
        return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print("error : ",e)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from bson import ObjectId
from datetime import datetime, timedelta
import jwt
from users.authentication import authenticate  # your custom decorator
from .models import Admin

SECRET_KEY = settings.SECRET_KEY


# ------------------ JWT Helper ------------------
def generate_jwt(payload):
    """Generate JWT with 7 days expiry."""
    payload["exp"] = datetime.utcnow() + timedelta(days=7)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# ------------------ Admin Register ------------------
@api_view(["POST"])
def register_admin(request):
    name = request.data.get("name")
    email = request.data.get("email")
    password = request.data.get("password")
    confirm_password = request.data.get("confirm_password")

    # Validation
    if not all([name, email, password, confirm_password]):
        return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

    if password != confirm_password:
        return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

    if Admin.objects(email=email).first():
        return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

    # Create admin
    admin = Admin(name=name, email=email)
    admin.set_password(password)
    admin.save()

    return Response({"message": "Admin registered successfully"}, status=status.HTTP_201_CREATED)


# ------------------ Admin Login ------------------
@api_view(["POST"])
def login_admin(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    admin = Admin.objects(email=email).first()
    if not admin:
        return Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)

    if not admin.check_password(password):
        return Response({"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)

    # Generate JWT
    token = generate_jwt({"id": str(admin.id), "role": "admin"})

    return Response({
        "message": "Admin login successful",
        "token": token,
        "admin": {
            "id": str(admin.id),
            "name": admin.name,
            "email": admin.email,
            "role": admin.role
        }
    }, status=status.HTTP_200_OK)


# ------------------ Admin Profile ------------------
@api_view(["GET"])
@authenticate
def admin_profile(request):
    """Fetch logged-in admin profile from JWT"""
    user_id = request.user.get("id")

    try:
        admin = Admin.objects(_id=ObjectId(user_id)).first()
    except Exception:
        return Response({"error": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST)

    if not admin:
        return Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "id": str(admin.id),
        "name": admin.name,
        "email": admin.email,
        "role": admin.role,
        "is_active": admin.is_active,
        "created_at": admin.created_at
    }, status=status.HTTP_200_OK)
