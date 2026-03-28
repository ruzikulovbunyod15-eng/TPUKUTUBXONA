import random
import string

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import AdminProfile, Student, Teacher, Book


# ======================
# GENERATORLAR
# ======================

def generate_admin_login():
    return f"admin_{random.randint(1000, 9999)}"


def generate_user_login(prefix):
    return f"{prefix}_{random.randint(10000, 99999)}"


def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


# ======================
# ADMIN (ODDIY ADMIN)
# ======================

class AdminProfileAdminForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = [
            'first_name',
            'last_name',
            'middle_name',
            'gender',
            'role',
            'phone',
            'photo',
        ]

    def save(self, commit=True):
        admin_profile = super().save(commit=False)

        if not admin_profile.pk:
            login = generate_admin_login()
            while User.objects.filter(username=login).exists():
                login = generate_admin_login()

            password = generate_password()

            user = User.objects.create_user(
                username=login,
                password=password,
                is_active=True,
                is_staff=True,
                is_superuser=False,
            )

            user.first_name = admin_profile.first_name
            user.last_name = admin_profile.last_name
            user.save()

            admin_profile.user = user
            admin_profile.generated_login = login
            admin_profile.generated_password = password
        else:
            if admin_profile.user:
                admin_profile.user.first_name = admin_profile.first_name
                admin_profile.user.last_name = admin_profile.last_name
                admin_profile.user.save()
                admin_profile.generated_login = admin_profile.user.username

        if commit:
            admin_profile.save()

        return admin_profile


# ======================
# TALABA
# ======================

class StudentPanelForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'first_name',
            'last_name',
            'middle_name',
            'gender',
            'group',
            'course',
            'phone',
        ]

    def save(self, commit=True):
        student = super().save(commit=False)

        if not student.pk:
            username = generate_user_login("student")
            while User.objects.filter(username=username).exists():
                username = generate_user_login("student")

            password = generate_password()

            user = User.objects.create_user(
                username=username,
                password=password
            )

            user.first_name = student.first_name
            user.last_name = student.last_name
            user.save()

            student.user = user
            student.generated_login = username
            student.generated_password = password
        else:
            if student.user:
                student.user.first_name = student.first_name
                student.user.last_name = student.last_name
                student.user.save()

        if commit:
            student.save()

        return student


# ======================
# O‘QITUVCHI
# ======================

class TeacherPanelForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'first_name',
            'last_name',
            'middle_name',
            'gender',
            'department',
            'phone',
        ]

    def save(self, commit=True):
        teacher = super().save(commit=False)

        if not teacher.pk:
            username = generate_user_login("teacher")
            while User.objects.filter(username=username).exists():
                username = generate_user_login("teacher")

            password = generate_password()

            user = User.objects.create_user(
                username=username,
                password=password
            )

            user.first_name = teacher.first_name
            user.last_name = teacher.last_name
            user.save()

            teacher.user = user
            teacher.generated_login = username
            teacher.generated_password = password
        else:
            if teacher.user:
                teacher.user.first_name = teacher.first_name
                teacher.user.last_name = teacher.last_name
                teacher.user.save()

        if commit:
            teacher.save()

        return teacher


# ======================
# KITOB
# ======================

class BookPanelForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'author',
            'category',
            'keywords',
            'description',
            'pdf_file',
            'cover',  # 🔥 ENG MUHIM QO‘SHILDI
        ]

    def clean_pdf_file(self):
        file = self.cleaned_data.get('pdf_file')

        if file:
            if not file.name.lower().endswith('.pdf'):
                raise ValidationError("Faqat PDF fayl yuklash mumkin.")

            if file.size > 10 * 1024 * 1024:
                raise ValidationError("PDF hajmi 10MB dan oshmasin.")

        return file

    def clean_cover(self):
        image = self.cleaned_data.get('cover')

        if image:
            if not image.content_type.startswith('image/'):
                raise ValidationError("Faqat rasm fayl yuklash mumkin.")

            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Muqova rasmi 5MB dan oshmasin.")

        return image


# ======================
# ADMIN PROFILE UPDATE
# ======================

class AdminProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(label="Login", max_length=150)

    class Meta:
        model = AdminProfile
        fields = [
            'first_name',
            'last_name',
            'middle_name',
            'gender',
            'role',
            'phone',
            'photo',
        ]

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username)

        if self.instance and self.instance.user_id:
            qs = qs.exclude(pk=self.instance.user_id)

        if qs.exists():
            raise ValidationError("Bu login allaqachon mavjud.")

        return username

    def save(self, commit=True):
        profile = super().save(commit=False)
        username = self.cleaned_data['username']

        if profile.user:
            profile.user.username = username
            profile.user.first_name = profile.first_name
            profile.user.last_name = profile.last_name
            profile.user.save()
            profile.generated_login = username

        if commit:
            profile.save()

        return profile


# ======================
# ADMIN PASSWORD CHANGE
# ======================

class AdminPasswordChangeForm(forms.Form):
    new_password = forms.CharField(
        label="Yangi parol",
        widget=forms.PasswordInput
    )
    confirm_password = forms.CharField(
        label="Parolni tasdiqlang",
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("Parollar bir xil emas.")

        return cleaned_data