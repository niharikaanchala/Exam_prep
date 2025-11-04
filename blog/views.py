import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Blog


# ---------------------------
# CREATE BLOG
# ---------------------------
@csrf_exempt
def create_blog(request):
    """
    POST -> Create a new blog
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        blog = Blog(
            title=data.get("title"),
            excerpt=data.get("excerpt"),
            category=data.get("category"),
            author=data.get("author"),
            date=data.get("date"),
            read_time=data.get("readTime"),
            image=data.get("image"),
        )
        blog.save()
        return JsonResponse({"success": True, "message": "Blog created successfully"}, status=201)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


# ---------------------------
# READ ALL BLOGS
# ---------------------------
@csrf_exempt
def get_all_blogs(request):
    """
    GET -> Fetch all blogs
    """
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        blogs = [b.to_json() for b in Blog.objects()]
        return JsonResponse({"success": True, "blogs": blogs}, status=200)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


# ---------------------------
# READ SINGLE BLOG
# ---------------------------
@csrf_exempt
def get_blog(request, blog_id):
    """
    GET -> Fetch single blog by ID
    """
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        blog = Blog.objects.get(id=blog_id)
        return JsonResponse({"success": True, "blog": blog.to_json()}, status=200)
    except Blog.DoesNotExist:
        return JsonResponse({"success": False, "message": "Blog not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


# ---------------------------
# UPDATE BLOG
# ---------------------------
@csrf_exempt
def update_blog(request, blog_id):
    """
    PUT -> Update existing blog
    """
    if request.method != "PUT":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        blog = Blog.objects.get(id=blog_id)
        data = json.loads(request.body)

        for field in ["title", "excerpt", "category", "author", "date", "readTime", "image"]:
            if field in data:
                setattr(blog, field if field != "readTime" else "read_time", data[field])

        blog.save()
        return JsonResponse({"success": True, "message": "Blog updated successfully"}, status=200)
    except Blog.DoesNotExist:
        return JsonResponse({"success": False, "message": "Blog not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


# ---------------------------
# DELETE BLOG
# ---------------------------
@csrf_exempt
def delete_blog(request, blog_id):
    """
    DELETE -> Delete a blog by ID
    """
    if request.method != "DELETE":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        blog = Blog.objects.get(id=blog_id)
        blog.delete()
        return JsonResponse({"success": True, "message": "Blog deleted successfully"}, status=200)
    except Blog.DoesNotExist:
        return JsonResponse({"success": False, "message": "Blog not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
