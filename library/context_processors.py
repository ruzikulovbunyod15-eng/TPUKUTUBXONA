from django.contrib.auth.models import User
from django.db.models import Count
from .models import AdminProfile, Student, Teacher, Book, Category


def admin_dashboard_stats(request):
    # faqat admin panel uchun ishlaydi
    if request.path.startswith('/admin/'):

        # bo‘limlar bo‘yicha statistika (MUHIM: books!)
        category_stats = Category.objects.annotate(
            total_books=Count('books')
        ).order_by('name')

        return {
            # umumiy statistika
            'total_students': Student.objects.count(),
            'total_teachers': Teacher.objects.count(),
            'total_books': Book.objects.count(),
            'total_categories': Category.objects.count(),
            'total_admins': AdminProfile.objects.count(),
            'total_users': User.objects.count(),

            # oxirgi qo‘shilganlar
            'latest_students': Student.objects.order_by('-created_at')[:5],
            'latest_teachers': Teacher.objects.order_by('-created_at')[:5],
            'latest_books': Book.objects.select_related('category', 'uploaded_by').order_by('-created_at')[:5],
            'latest_admins': AdminProfile.objects.order_by('-created_at')[:5],

            # chart uchun
            'category_stats': category_stats,
            'chart_labels': [c.name for c in category_stats],
            'chart_data': [c.total_books for c in category_stats],
        }

    return {}