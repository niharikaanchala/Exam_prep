from django.urls import path
from .views import (
    check_enrollment,
    create_enrollment,
    get_enrollments,
    get_enrollment_detail,
    delete_enrollment,
    update_enrollment,
    check_practice_enrollment,
    create_razorpay_order,
    verify_razorpay_payment,
)

urlpatterns = [
    # Check if user enrolled
    path("", get_enrollments, name="get_enrollments"),
    path("check/<str:category_id>/", check_enrollment, name="check_enrollment"),
    

    # Create enrollment
    path("create/", create_enrollment, name="create_enrollment"),

    path("check/<str:practice_id>/test/", check_practice_enrollment, name="check_practice_enrollment"),
    # Get all enrollments

    # Get single enrollment (use str id)
    path("<str:enrollment_id>/", get_enrollment_detail, name="get_enrollment_detail"),

    # Delete enrollment
    path("<str:enrollment_id>/delete/", delete_enrollment, name="delete_enrollment"),

    # Update enrollment
    path("<str:enrollment_id>/update/", update_enrollment, name="update_enrollment"),

    # Razorpay payment endpoints
    path("payment/create-order/", create_razorpay_order, name="create_razorpay_order"),
    path("payment/verify/", verify_razorpay_payment, name="verify_razorpay_payment"),
    
]
