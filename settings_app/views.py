import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from common.middleware import authenticate, restrict
from .models import AdminSettings

@csrf_exempt
@authenticate
@restrict(['admin'])
def get_admin_settings(request):
    """Retrieve current admin settings."""
    try:
        settings_obj = AdminSettings.objects.first()
        if not settings_obj:
            settings_obj = AdminSettings().save()

        data = {
            "site_name": settings_obj.site_name,
            "admin_email": settings_obj.admin_email,
            "email_notifications": settings_obj.email_notifications,
            "maintenance_mode": settings_obj.maintenance_mode,
            "default_user_role": settings_obj.default_user_role,
            "session_timeout": settings_obj.session_timeout,
        }

        return JsonResponse({"success": True, "data": data}, status=200)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@authenticate
@restrict(['admin'])
def update_admin_settings(request):
    """Update admin settings via POST request."""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
        settings_obj = AdminSettings.objects.first()
        if not settings_obj:
            settings_obj = AdminSettings()

        # Update fields if provided
        settings_obj.site_name = body.get("site_name", settings_obj.site_name)
        settings_obj.admin_email = body.get("admin_email", settings_obj.admin_email)
        settings_obj.email_notifications = body.get("email_notifications", settings_obj.email_notifications)
        settings_obj.maintenance_mode = body.get("maintenance_mode", settings_obj.maintenance_mode)
        settings_obj.default_user_role = body.get("default_user_role", settings_obj.default_user_role)
        settings_obj.session_timeout = body.get("session_timeout", settings_obj.session_timeout)
        settings_obj.save()

        return JsonResponse({"success": True, "message": "Settings updated successfully"}, status=200)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
