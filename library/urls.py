from django.urls import path
from .views import (
    # PUBLIC
    home_page,
    public_library,
    book_read,

    # AUTH
    user_login,
    user_logout,

    # ADMIN PANEL
    admin_panel,

    students_list,
    student_add,
    student_edit,
    student_delete,

    teachers_list,
    teacher_add,
    teacher_edit,
    teacher_delete,

    books_list,
    book_add,
    book_edit,
    book_delete,

    admin_profile,
    admin_profile_edit,
    admin_password_change,

    # USER PANELS
    teacher_panel,
    student_panel,

    # TEACHER BOOK SYSTEM
    teacher_my_books,
    teacher_book_add,
    teacher_book_edit,
    teacher_book_delete,

    student_books,
    student_favorites,
    toggle_student_favorite,
)

urlpatterns = [

    # ======================
    # PUBLIC
    # ======================
    path('', home_page, name='home_page'),
    path('kutubxona/', public_library, name='public_library'),

    # 🔥 PUBLIC BOOK READ (ENG MUHIM)
    path('books/<int:pk>/read/', book_read, name='book_read'),

    # ======================
    # AUTH
    # ======================
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    # ======================
    # ADMIN PANEL
    # ======================
    path('panel/admin/', admin_panel, name='admin_panel'),

    # --- STUDENTS ---
    path('panel/admin/students/', students_list, name='students_list'),
    path('panel/admin/students/add/', student_add, name='student_add'),
    path('panel/admin/students/<int:pk>/edit/', student_edit, name='student_edit'),
    path('panel/admin/students/<int:pk>/delete/', student_delete, name='student_delete'),

    # --- TEACHERS ---
    path('panel/admin/teachers/', teachers_list, name='teachers_list'),
    path('panel/admin/teachers/add/', teacher_add, name='teacher_add'),
    path('panel/admin/teachers/<int:pk>/edit/', teacher_edit, name='teacher_edit'),
    path('panel/admin/teachers/<int:pk>/delete/', teacher_delete, name='teacher_delete'),

    # --- BOOKS ---
    path('panel/admin/books/', books_list, name='books_list'),
    path('panel/admin/books/add/', book_add, name='book_add'),
    path('panel/admin/books/<int:pk>/edit/', book_edit, name='book_edit'),
    path('panel/admin/books/<int:pk>/delete/', book_delete, name='book_delete'),

    # ❌ ESKISI (O‘CHIRILDI)
    # path('panel/admin/books/<int:pk>/read/', book_read, name='book_read'),

    # --- PROFILE ---
    path('panel/admin/profile/', admin_profile, name='admin_profile'),
    path('panel/admin/profile/edit/', admin_profile_edit, name='admin_profile_edit'),
    path('panel/admin/profile/password/', admin_password_change, name='admin_password_change'),

    # ======================
    # USER PANELS
    # ======================
    path('panel/teacher/', teacher_panel, name='teacher_panel'),
    path('panel/student/', student_panel, name='student_panel'),

    # ======================
    # TEACHER BOOK SYSTEM
    # ======================
    path('panel/teacher/my-books/', teacher_my_books, name='teacher_my_books'),
    path('panel/teacher/my-books/add/', teacher_book_add, name='teacher_book_add'),
    path('panel/teacher/my-books/<int:pk>/edit/', teacher_book_edit, name='teacher_book_edit'),
    path('panel/teacher/my-books/<int:pk>/delete/', teacher_book_delete, name='teacher_book_delete'),


    path('panel/student/books/', student_books, name='student_books'),
    path('panel/student/favorites/', student_favorites, name='student_favorites'),      
    path('panel/student/favorites/toggle/<int:book_id>/', toggle_student_favorite, name='toggle_student_favorite'),
]