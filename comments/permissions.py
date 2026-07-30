from rest_framework import permissions

class IsAdminOrOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # مشاهده برای همه آزاد
        if request.method in permissions.SAFE_METHODS:
            return True

        # ساختن/ویرایش/حذف نیاز به لاگین دارد
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # مشاهده جزئیات برای همه آزاد
        if request.method in permissions.SAFE_METHODS:
            return True

        # ادمین دسترسی کامل
        if request.user and request.user.is_staff:
            return True

        # کاربر فقط روی پست خودش
        return getattr(obj, "user_id", None) == request.user.id
