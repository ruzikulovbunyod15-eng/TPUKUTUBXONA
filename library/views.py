from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import (
    Student,
    Teacher,
    Book,
    Category,
    FavoriteBook,
    StudentFavoriteBook,
)
from .forms import (
    StudentPanelForm,
    TeacherPanelForm,
    BookPanelForm,
    AdminProfileUpdateForm,
    AdminPasswordChangeForm,
)


# ======================
# YORDAMCHI FUNKSIYALAR
# ======================

def is_library_admin(user):
    return user.is_authenticated and (
        user.is_superuser or
        user.is_staff or
        hasattr(user, 'admin_profile')
    )


def redirect_user_by_role(user):
    if user.is_superuser:
        return redirect('/admin/')

    if is_library_admin(user):
        return redirect('admin_panel')

    if hasattr(user, 'teacher_profile'):
        return redirect('teacher_panel')

    if hasattr(user, 'student_profile'):
        return redirect('student_panel')

    return redirect('home_page')


# ======================
# PUBLIC SAHIFALAR
# ======================

def home_page(request):
    latest_books = Book.objects.select_related('category').order_by('-created_at')[:8]

    context = {
        'latest_books': latest_books,
        'total_books': Book.objects.count(),
        'total_resources': Book.objects.count(),
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
    }
    return render(request, 'library/home_page.html', context)


def public_library(request):
    books = Book.objects.select_related('category').order_by('-created_at')
    categories = Category.objects.all().order_by('name')

    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()

    if q:
        books = books.filter(
            Q(title__icontains=q) |
            Q(author__icontains=q) |
            Q(keywords__icontains=q)
        )

    if category_id:
        books = books.filter(category_id=category_id)

    context = {
        'books': books,
        'categories': categories,
        'total_books': books.count(),
        'selected_category': category_id,
        'search_query': q,
    }
    return render(request, 'library/public_library.html', context)


# ======================
# AUTH
# ======================

def user_login(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect_user_by_role(request.user)

    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        next_url = request.POST.get('next') or request.GET.get('next')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if next_url:
                return redirect(next_url)

            return redirect_user_by_role(user)

        error = "Login yoki parol xato."

    return render(request, 'library/login.html', {
        'error': error,
        'next': request.GET.get('next', '')
    })


@login_required
def user_logout(request):
    logout(request)
    return redirect('home_page')


# ======================
# ADMIN PANEL
# ======================

@login_required
def admin_panel(request):
    if not is_library_admin(request.user):
        return redirect('home_page')

    profile = getattr(request.user, 'admin_profile', None)

    context = {
        'profile': profile,
        'students_count': Student.objects.count(),
        'teachers_count': Teacher.objects.count(),
        'books_count': Book.objects.count(),
        'latest_students': Student.objects.order_by('-created_at')[:5],
        'latest_books': Book.objects.select_related('category', 'uploaded_by').order_by('-created_at')[:5],
    }
    return render(request, 'library/admin_panel.html', context)


# ======================
# STUDENTS
# ======================

@login_required
def students_list(request):
    if not is_library_admin(request.user):
        return redirect('home_page')

    students = Student.objects.order_by('-created_at')

    q = request.GET.get('q', '').strip()
    group = request.GET.get('group', '').strip()
    course = request.GET.get('course', '').strip()
    gender = request.GET.get('gender', '').strip()

    if q:
        students = students.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(middle_name__icontains=q) |
            Q(group__icontains=q) |
            Q(generated_login__icontains=q)
        )

    if group:
        students = students.filter(group=group)

    if course:
        students = students.filter(course=course)

    if gender:
        students = students.filter(gender=gender)

    context = {
        'students': students,
        'groups': Student.objects.values_list('group', flat=True).distinct(),
        'courses': Student.objects.values_list('course', flat=True).distinct(),
        'selected_group': group,
        'selected_course': course,
        'selected_gender': gender,
        'search_query': q,
    }
    return render(request, 'library/students/list.html', context)


@login_required
def student_add(request):
    if not is_library_admin(request.user):
        return redirect('home_page')

    if request.method == 'POST':
        form = StudentPanelForm(request.POST)
        if form.is_valid():
            student = form.save()
            if student.user:
                student.user.first_name = student.first_name
                student.user.last_name = student.last_name
                student.user.save()
            return redirect('students_list')
    else:
        form = StudentPanelForm()

    return render(request, 'library/students/add.html', {'form': form})


@login_required
def student_edit(request, pk):
    if not is_library_admin(request.user):
        return redirect('home_page')

    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentPanelForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            if student.user:
                student.user.first_name = student.first_name
                student.user.last_name = student.last_name
                student.user.save()
            return redirect('students_list')
    else:
        form = StudentPanelForm(instance=student)

    return render(request, 'library/students/edit.html', {
        'form': form,
        'student': student,
    })


@login_required
def student_delete(request, pk):
    if not is_library_admin(request.user):
        return redirect('home_page')

    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        if student.user:
            student.user.delete()
        else:
            student.delete()
        return redirect('students_list')

    return render(request, 'library/students/delete.html', {'student': student})


# ======================
# TEACHERS
# ======================

@login_required
def teachers_list(request):
    if not is_library_admin(request.user):
        return redirect('home_page')

    teachers = Teacher.objects.order_by('-created_at')

    q = request.GET.get('q', '').strip()
    department = request.GET.get('department', '').strip()
    gender = request.GET.get('gender', '').strip()

    if q:
        teachers = teachers.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(middle_name__icontains=q) |
            Q(department__icontains=q) |
            Q(generated_login__icontains=q)
        )

    if department:
        teachers = teachers.filter(department=department)

    if gender:
        teachers = teachers.filter(gender=gender)

    context = {
        'teachers': teachers,
        'departments': Teacher.objects.values_list('department', flat=True).distinct(),
        'selected_department': department,
        'selected_gender': gender,
        'search_query': q,
    }
    return render(request, 'library/teachers/list.html', context)


@login_required
def teacher_add(request):
    if not is_library_admin(request.user):
        return redirect('home_page')

    if request.method == 'POST':
        form = TeacherPanelForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            if teacher.user:
                teacher.user.first_name = teacher.first_name
                teacher.user.last_name = teacher.last_name
                teacher.user.save()
            return redirect('teachers_list')
    else:
        form = TeacherPanelForm()

    return render(request, 'library/teachers/add.html', {'form': form})


@login_required
def teacher_edit(request, pk):
    if not is_library_admin(request.user):
        return redirect('home_page')

    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        form = TeacherPanelForm(request.POST, instance=teacher)
        if form.is_valid():
            teacher = form.save()
            if teacher.user:
                teacher.user.first_name = teacher.first_name
                teacher.user.last_name = teacher.last_name
                teacher.user.save()
            return redirect('teachers_list')
    else:
        form = TeacherPanelForm(instance=teacher)

    return render(request, 'library/teachers/edit.html', {
        'form': form,
        'teacher': teacher,
    })


@login_required
def teacher_delete(request, pk):
    if not is_library_admin(request.user):
        return redirect('home_page')

    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        if teacher.user:
            teacher.user.delete()
        else:
            teacher.delete()
        return redirect('teachers_list')

    return render(request, 'library/teachers/delete.html', {'teacher': teacher})


# ======================
# ADMIN PROFILE
# ======================

@login_required
def admin_profile(request):
    if not is_library_admin(request.user):
        return redirect('home_page')

    profile = getattr(request.user, 'admin_profile', None)
    return render(request, 'library/profile/detail.html', {'profile': profile})


@login_required
def admin_profile_edit(request):
    if not is_library_admin(request.user):
        return redirect('home_page')

    if not hasattr(request.user, 'admin_profile'):
        return redirect('admin_panel')

    profile = request.user.admin_profile

    if request.method == 'POST':
        form = AdminProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('admin_profile')
    else:
        form = AdminProfileUpdateForm(instance=profile)
        form.fields['username'].initial = profile.user.username

    return render(request, 'library/profile/edit.html', {'form': form})


@login_required
def admin_password_change(request):
    if not is_library_admin(request.user):
        return redirect('home_page')

    if not hasattr(request.user, 'admin_profile'):
        return redirect('admin_panel')

    profile = request.user.admin_profile

    if request.method == 'POST':
        form = AdminPasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            profile.user.set_password(new_password)
            profile.user.save()
            profile.generated_password = new_password
            profile.save()
            return redirect('login')
    else:
        form = AdminPasswordChangeForm()

    return render(request, 'library/profile/change_password.html', {'form': form})


# ======================
# TEACHER PANEL
# ======================

@login_required
def teacher_panel(request):
    if not hasattr(request.user, 'teacher_profile'):
        return redirect('login')

    profile = request.user.teacher_profile

    my_books = Book.objects.filter(uploaded_by=request.user)
    my_books_count = my_books.count()
    favorite_books_count = FavoriteBook.objects.filter(teacher=profile).count()
    total_books_count = Book.objects.count()

    latest_my_books = my_books.select_related('category').order_by('-created_at')[:5]
    latest_favorites = FavoriteBook.objects.filter(
        teacher=profile
    ).select_related('book', 'book__category').order_by('-created_at')[:5]

    context = {
        'profile': profile,
        'my_books_count': my_books_count,
        'favorite_books_count': favorite_books_count,
        'total_books_count': total_books_count,
        'latest_my_books': latest_my_books,
        'latest_favorites': latest_favorites,
        'chart_labels': ['Mening kitoblarim', 'Sevimli kitoblarim', 'Jami kitoblar'],
        'chart_data': [my_books_count, favorite_books_count, total_books_count],
    }
    return render(request, 'library/teacher_panel.html', context)


@login_required
def teacher_my_books(request):
    if not hasattr(request.user, 'teacher_profile'):
        return redirect('login')

    books = Book.objects.filter(uploaded_by=request.user).select_related('category').order_by('-created_at')

    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    if q:
        books = books.filter(
            Q(title__icontains=q) |
            Q(author__icontains=q) |
            Q(keywords__icontains=q)
        )

    if category:
        books = books.filter(category_id=category)

    context = {
        'books': books,
        'categories': Category.objects.all().order_by('name'),
        'selected_category': category,
        'search_query': q,
    }
    return render(request, 'library/teachers/my_books.html', context)


@login_required
def teacher_book_add(request):
    if not hasattr(request.user, 'teacher_profile'):
        return redirect('login')

    if request.method == 'POST':
        form = BookPanelForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.uploaded_by = request.user
            book.save()
            return redirect('teacher_my_books')
    else:
        form = BookPanelForm()

    return render(request, 'library/teachers/book_add.html', {'form': form})


@login_required
def teacher_book_edit(request, pk):
    if not hasattr(request.user, 'teacher_profile'):
        return redirect('login')

    book = get_object_or_404(Book, pk=pk, uploaded_by=request.user)

    if request.method == 'POST':
        form = BookPanelForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            edited_book = form.save(commit=False)
            edited_book.uploaded_by = request.user
            edited_book.save()
            return redirect('teacher_my_books')
    else:
        form = BookPanelForm(instance=book)

    return render(request, 'library/teachers/book_edit.html', {
        'form': form,
        'book': book,
    })


@login_required
def teacher_book_delete(request, pk):
    if not hasattr(request.user, 'teacher_profile'):
        return redirect('login')

    book = get_object_or_404(Book, pk=pk, uploaded_by=request.user)

    if request.method == 'POST':
        if book.pdf_file:
            book.pdf_file.delete(save=False)
        if book.cover:
            book.cover.delete(save=False)
        book.delete()
        return redirect('teacher_my_books')

    return render(request, 'library/teachers/book_delete.html', {'book': book})


# ======================
# STUDENT PANEL
# ======================

@login_required
def student_panel(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('login')

    profile = request.user.student_profile

    favorite_books_count = StudentFavoriteBook.objects.filter(student=profile).count()
    total_books_count = Book.objects.count()
    latest_books = Book.objects.select_related('category').order_by('-created_at')[:6]
    latest_favorites = StudentFavoriteBook.objects.filter(
        student=profile
    ).select_related('book', 'book__category').order_by('-created_at')[:5]

    context = {
        'profile': profile,
        'favorite_books_count': favorite_books_count,
        'total_books_count': total_books_count,
        'latest_books': latest_books,
        'latest_favorites': latest_favorites,
        'chart_labels': ['Sevimli kitoblarim', 'Jami kitoblar'],
        'chart_data': [favorite_books_count, total_books_count],
    }
    return render(request, 'library/student_panel.html', context)


@login_required
def student_books(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('login')

    books = Book.objects.select_related('category').order_by('-created_at')
    categories = Category.objects.all().order_by('name')

    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    if q:
        books = books.filter(
            Q(title__icontains=q) |
            Q(author__icontains=q) |
            Q(keywords__icontains=q)
        )

    if category:
        books = books.filter(category_id=category)

    favorite_ids = StudentFavoriteBook.objects.filter(
        student=request.user.student_profile
    ).values_list('book_id', flat=True)

    context = {
        'books': books,
        'categories': categories,
        'favorite_ids': list(favorite_ids),
        'selected_category': category,
        'search_query': q,
    }
    return render(request, 'library/students/books.html', context)


@login_required
def student_favorites(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('login')

    favorites = StudentFavoriteBook.objects.filter(
        student=request.user.student_profile
    ).select_related('book', 'book__category').order_by('-created_at')

    return render(request, 'library/students/favorites.html', {
        'favorites': favorites,
    })


@login_required
def toggle_student_favorite(request, book_id):
    if not hasattr(request.user, 'student_profile'):
        return redirect('login')

    student = request.user.student_profile
    book = get_object_or_404(Book, pk=book_id)

    favorite, created = StudentFavoriteBook.objects.get_or_create(
        student=student,
        book=book
    )

    if not created:
        favorite.delete()

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)

    return redirect('student_books')


# ======================
# BOOKS (ADMIN PANEL)
# ======================

@login_required
def books_list(request):
    if not is_library_admin(request.user):
        return redirect('home_page')

    books = Book.objects.select_related('category', 'uploaded_by').order_by('-created_at')

    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    if q:
        books = books.filter(
            Q(title__icontains=q) |
            Q(author__icontains=q) |
            Q(keywords__icontains=q) |
            Q(category__name__icontains=q)
        )

    if category:
        books = books.filter(category_id=category)

    context = {
        'books': books,
        'categories': Category.objects.all().order_by('name'),
        'selected_category': category,
        'search_query': q,
    }
    return render(request, 'library/books/list.html', context)


@login_required
def book_add(request):
    if not is_library_admin(request.user):
        return redirect('home_page')

    if request.method == 'POST':
        form = BookPanelForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.uploaded_by = request.user
            book.save()
            return redirect('books_list')
    else:
        form = BookPanelForm()

    return render(request, 'library/books/add.html', {'form': form})


@login_required
def book_edit(request, pk):
    if not is_library_admin(request.user):
        return redirect('home_page')

    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        form = BookPanelForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            edited_book = form.save(commit=False)
            if not edited_book.uploaded_by:
                edited_book.uploaded_by = request.user
            edited_book.save()
            return redirect('books_list')
    else:
        form = BookPanelForm(instance=book)

    return render(request, 'library/books/edit.html', {
        'form': form,
        'book': book,
    })


@login_required
def book_delete(request, pk):
    if not is_library_admin(request.user):
        return redirect('home_page')

    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        if book.pdf_file:
            book.pdf_file.delete(save=False)
        if book.cover:
            book.cover.delete(save=False)
        book.delete()
        return redirect('books_list')

    return render(request, 'library/books/delete.html', {'book': book})


# ======================
# BOOK READ
# ======================

@login_required
def book_read(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'library/books/read.html', {'book': book})