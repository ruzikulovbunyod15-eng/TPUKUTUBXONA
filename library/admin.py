from django.contrib import admin, messages
from django.utils.html import format_html
import random
import string

from .models import (
    AdminProfile,
    Student,
    Teacher,
    Book,
    Category,
    FavoriteBook,
    StudentFavoriteBook,
)
from .forms import (
    AdminProfileAdminForm,
    StudentPanelForm,
    TeacherPanelForm,
    BookPanelForm,
)


def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


admin.site.site_header = "Tpulib Super Admin"
admin.site.site_title = "Tpulib"
admin.site.index_title = "Super admin boshqaruvi"


# ======================
# ADMIN
# ======================

@admin.action(description="Tanlangan oddiy adminlar uchun yangi parol generatsiya qilish")
def regenerate_admin_password(modeladmin, request, queryset):
    for profile in queryset:
        if profile.user:
            new_password = generate_password()
            profile.user.set_password(new_password)
            profile.user.save()
            profile.generated_login = profile.user.username
            profile.generated_password = new_password
            profile.save()
    messages.success(request, "Tanlangan oddiy adminlar uchun yangi parol yaratildi.")


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    form = AdminProfileAdminForm
    actions = [regenerate_admin_password]

    list_display = (
        'id',
        'full_name',
        'role',
        'generated_login',
        'generated_password',
        'phone',
        'created_at',
    )

    search_fields = (
        'first_name',
        'last_name',
        'middle_name',
        'generated_login',
        'role',
        'phone',
    )

    list_filter = (
        'role',
        'gender',
        'created_at',
    )

    readonly_fields = (
        'generated_login',
        'generated_password',
        'created_at',
        'updated_at',
    )

    list_per_page = 25
    ordering = ('-created_at',)

    fieldsets = (
        ("Oddiy admin ma'lumotlari", {
            'fields': (
                'first_name',
                'last_name',
                'middle_name',
                'gender',
                'role',
                'phone',
                'photo',
            )
        }),
        ("Tizim bergan kirish ma'lumotlari", {
            'fields': (
                'generated_login',
                'generated_password',
            )
        }),
        ("Vaqt ma'lumotlari", {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )

    def full_name(self, obj):
        return f"{obj.last_name} {obj.first_name} {obj.middle_name}".strip()
    full_name.short_description = "F.I.Sh"


# ======================
# CATEGORY
# ======================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'book_count', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ('name',)

    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = "Kitoblar soni"


# ======================
# STUDENT
# ======================

@admin.action(description="Tanlangan talabalar parolini 12345678 ga tiklash")
def reset_student_password(modeladmin, request, queryset):
    for student in queryset:
        if student.user:
            student.user.set_password("12345678")
            student.user.save()
            student.generated_password = "12345678"
            student.save()
    messages.success(request, "Tanlangan talabalar paroli 12345678 ga tiklandi.")


@admin.action(description="Tanlangan talabalarni bloklash")
def block_students(modeladmin, request, queryset):
    for student in queryset:
        student.is_blocked = True
        student.save()
        if student.user:
            student.user.is_active = False
            student.user.save()
    messages.success(request, "Tanlangan talabalar bloklandi.")


@admin.action(description="Tanlangan talabalarni aktivlashtirish")
def unblock_students(modeladmin, request, queryset):
    for student in queryset:
        student.is_blocked = False
        student.save()
        if student.user:
            student.user.is_active = True
            student.user.save()
    messages.success(request, "Tanlangan talabalar aktivlashtirildi.")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentPanelForm
    actions = [reset_student_password, block_students, unblock_students]

    list_display = (
        'id',
        'full_name',
        'gender',
        'group',
        'course',
        'generated_login',
        'generated_password',
        'phone',
        'status_badge',
        'created_at',
    )

    search_fields = (
        'first_name',
        'last_name',
        'middle_name',
        'group',
        'generated_login',
        'phone',
    )

    list_filter = (
        'gender',
        'course',
        'group',
        'is_blocked',
        'created_at',
    )

    readonly_fields = (
        'generated_login',
        'generated_password',
        'created_at',
        'updated_at',
    )

    list_per_page = 25
    ordering = ('-created_at',)

    fieldsets = (
        ("Talaba ma'lumotlari", {
            'fields': (
                'first_name',
                'last_name',
                'middle_name',
                'gender',
                'group',
                'course',
                'phone',
                'is_blocked',
            )
        }),
        ("Tizim bergan kirish ma'lumotlari", {
            'fields': (
                'generated_login',
                'generated_password',
            )
        }),
        ("Vaqt ma'lumotlari", {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )

    def full_name(self, obj):
        return f"{obj.last_name} {obj.first_name} {obj.middle_name}".strip()
    full_name.short_description = "F.I.Sh"

    def status_badge(self, obj):
        if obj.is_blocked:
            return format_html(
                '<span style="padding:6px 10px;border-radius:999px;background:{};color:{};font-weight:700;">{}</span>',
                '#fee2e2',
                '#991b1b',
                'Bloklangan'
            )
        return format_html(
            '<span style="padding:6px 10px;border-radius:999px;background:{};color:{};font-weight:700;">{}</span>',
            '#dcfce7',
            '#166534',
            'Aktiv'
        )
    status_badge.short_description = "Holati"


# ======================
# TEACHER
# ======================

@admin.action(description="Tanlangan o‘qituvchilar parolini 12345678 ga tiklash")
def reset_teacher_password(modeladmin, request, queryset):
    for teacher in queryset:
        if teacher.user:
            teacher.user.set_password("12345678")
            teacher.user.save()
            teacher.generated_password = "12345678"
            teacher.save()
    messages.success(request, "Tanlangan o‘qituvchilar paroli 12345678 ga tiklandi.")


@admin.action(description="Tanlangan o‘qituvchilarni bloklash")
def block_teachers(modeladmin, request, queryset):
    for teacher in queryset:
        teacher.is_blocked = True
        teacher.save()
        if teacher.user:
            teacher.user.is_active = False
            teacher.user.save()
    messages.success(request, "Tanlangan o‘qituvchilar bloklandi.")


@admin.action(description="Tanlangan o‘qituvchilarni aktivlashtirish")
def unblock_teachers(modeladmin, request, queryset):
    for teacher in queryset:
        teacher.is_blocked = False
        teacher.save()
        if teacher.user:
            teacher.user.is_active = True
            teacher.user.save()
    messages.success(request, "Tanlangan o‘qituvchilar aktivlashtirildi.")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    form = TeacherPanelForm
    actions = [reset_teacher_password, block_teachers, unblock_teachers]

    list_display = (
        'id',
        'full_name',
        'gender',
        'department',
        'generated_login',
        'generated_password',
        'phone',
        'status_badge',
        'created_at',
    )

    search_fields = (
        'first_name',
        'last_name',
        'middle_name',
        'department',
        'generated_login',
        'phone',
    )

    list_filter = (
        'gender',
        'department',
        'is_blocked',
        'created_at',
    )

    readonly_fields = (
        'generated_login',
        'generated_password',
        'created_at',
        'updated_at',
    )

    list_per_page = 25
    ordering = ('-created_at',)

    fieldsets = (
        ("O‘qituvchi ma'lumotlari", {
            'fields': (
                'first_name',
                'last_name',
                'middle_name',
                'gender',
                'department',
                'phone',
                'is_blocked',
            )
        }),
        ("Tizim bergan kirish ma'lumotlari", {
            'fields': (
                'generated_login',
                'generated_password',
            )
        }),
        ("Vaqt ma'lumotlari", {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )

    def full_name(self, obj):
        return f"{obj.last_name} {obj.first_name} {obj.middle_name}".strip()
    full_name.short_description = "F.I.Sh"

    def status_badge(self, obj):
        if obj.is_blocked:
            return format_html(
                '<span style="padding:6px 10px;border-radius:999px;background:{};color:{};font-weight:700;">{}</span>',
                '#fee2e2',
                '#991b1b',
                'Bloklangan'
            )
        return format_html(
            '<span style="padding:6px 10px;border-radius:999px;background:{};color:{};font-weight:700;">{}</span>',
            '#dcfce7',
            '#166534',
            'Aktiv'
        )
    status_badge.short_description = "Holati"


# ======================
# BOOK
# ======================

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    form = BookPanelForm

    list_display = (
        'id',
        'title',
        'author',
        'category',
        'uploaded_by',
        'cover_preview',
        'pdf_preview',
        'created_at',
    )

    search_fields = (
        'title',
        'author',
        'keywords',
        'description',
        'category__name',
        'uploaded_by__username',
    )

    list_filter = (
        'category',
        'created_at',
    )

    readonly_fields = (
        'uploaded_by',
        'cover_preview_large',
        'created_at',
        'updated_at',
    )

    list_per_page = 25
    ordering = ('-created_at',)

    fieldsets = (
        ("Kitob ma'lumotlari", {
            'fields': (
                'title',
                'author',
                'category',
                'keywords',
                'description',
            )
        }),
        ("Fayllar", {
            'fields': (
                'pdf_file',
                'cover',
                'cover_preview_large',
            )
        }),
        ("Qo‘shimcha ma'lumotlar", {
            'fields': (
                'uploaded_by',
                'created_at',
                'updated_at',
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

    def pdf_preview(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" style="font-weight:700;">Ko‘rish</a>',
                obj.pdf_file.url
            )
        return "-"
    pdf_preview.short_description = "PDF"

    def cover_preview(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" width="45" height="65" style="object-fit:cover;border-radius:8px;border:1px solid #ddd;" />',
                obj.cover.url
            )
        return "-"
    cover_preview.short_description = "Muqova"

    def cover_preview_large(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" width="120" style="object-fit:cover;border-radius:10px;border:1px solid #ddd;" />',
                obj.cover.url
            )
        return "Muqova mavjud emas"
    cover_preview_large.short_description = "Muqova preview"


# ======================
# TEACHER FAVORITES
# ======================

@admin.register(FavoriteBook)
class FavoriteBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher', 'book', 'created_at')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'book__title')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ('-created_at',)


# ======================
# STUDENT FAVORITES
# ======================

@admin.register(StudentFavoriteBook)
class StudentFavoriteBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'book', 'created_at')
    search_fields = ('student__first_name', 'student__last_name', 'book__title')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ('-created_at',)