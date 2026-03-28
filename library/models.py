import os
import uuid
import fitz

from io import BytesIO

from django.db import models
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from PIL import Image


def validate_pdf_size(value):
    limit = 10 * 1024 * 1024  # 10 MB
    if value.size > limit:
        raise ValidationError("PDF fayl 10 MB dan oshmasligi kerak.")


def validate_image_size(value):
    limit = 5 * 1024 * 1024  # 5 MB
    if value.size > limit:
        raise ValidationError("Muqova rasmi 5 MB dan oshmasligi kerak.")


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")

    class Meta:
        abstract = True


# ======================
# ADMIN
# ======================

class AdminProfile(TimeStampedModel):
    GENDER_CHOICES = (
        ('erkak', 'Erkak'),
        ('ayol', 'Ayol'),
    )

    ROLE_CHOICES = (
        ('kutubxonachi', 'Kutubxonachi'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin_profile',
        verbose_name="Foydalanuvchi",
    )
    first_name = models.CharField("Ismi", max_length=100)
    last_name = models.CharField("Familyasi", max_length=100)
    middle_name = models.CharField("Sharifi", max_length=100, blank=True)
    gender = models.CharField("Jinsi", max_length=10, choices=GENDER_CHOICES)
    role = models.CharField("Roli", max_length=20, choices=ROLE_CHOICES, default='kutubxonachi')
    phone = models.CharField("Telefon", max_length=30, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    generated_login = models.CharField("Berilgan login", max_length=150, blank=True)
    generated_password = models.CharField("Berilgan parol", max_length=150, blank=True)

    class Meta:
        verbose_name = "Oddiy admin"
        verbose_name_plural = "Oddiy adminlar"
        ordering = ['-created_at']

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}".strip()
        return full_name if full_name else self.user.username

    def save(self, *args, **kwargs):
        if self.user and not self.user.is_staff:
            self.user.is_staff = True
            self.user.save(update_fields=['is_staff'])
        super().save(*args, **kwargs)


# ======================
# CATEGORY
# ======================

class Category(TimeStampedModel):
    name = models.CharField("Bo‘lim nomi", max_length=150, unique=True)

    class Meta:
        verbose_name = "Bo‘lim"
        verbose_name_plural = "Bo‘limlar"
        ordering = ['name']

    def __str__(self):
        return self.name


# ======================
# STUDENT
# ======================

class Student(TimeStampedModel):
    GENDER_CHOICES = (
        ('erkak', 'Erkak'),
        ('ayol', 'Ayol'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name="Foydalanuvchi",
    )
    first_name = models.CharField("Ismi", max_length=100)
    last_name = models.CharField("Familyasi", max_length=100)
    middle_name = models.CharField("Sharifi", max_length=100, blank=True)
    gender = models.CharField("Jinsi", max_length=10, choices=GENDER_CHOICES)
    group = models.CharField("Guruhi", max_length=50)
    course = models.PositiveSmallIntegerField("Kursi")
    phone = models.CharField("Telefon", max_length=30, blank=True)

    generated_login = models.CharField("Berilgan login", max_length=150, blank=True)
    generated_password = models.CharField("Berilgan parol", max_length=150, blank=True)

    is_blocked = models.BooleanField("Bloklangan", default=False)

    class Meta:
        verbose_name = "Talaba"
        verbose_name_plural = "Talabalar"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}".strip()
        return full_name if full_name else self.user.username

    def clean(self):
        if self.course and self.course < 1:
            raise ValidationError({"course": "Kurs 1 dan kichik bo‘lmasligi kerak."})


# ======================
# TEACHER
# ======================

class Teacher(TimeStampedModel):
    GENDER_CHOICES = (
        ('erkak', 'Erkak'),
        ('ayol', 'Ayol'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        verbose_name="Foydalanuvchi",
    )
    first_name = models.CharField("Ismi", max_length=100)
    last_name = models.CharField("Familyasi", max_length=100)
    middle_name = models.CharField("Sharifi", max_length=100, blank=True)
    gender = models.CharField("Jinsi", max_length=10, choices=GENDER_CHOICES)
    department = models.CharField("Kafedra", max_length=150)
    phone = models.CharField("Telefon", max_length=30, blank=True)

    generated_login = models.CharField("Berilgan login", max_length=150, blank=True)
    generated_password = models.CharField("Berilgan parol", max_length=150, blank=True)

    is_blocked = models.BooleanField("Bloklangan", default=False)

    class Meta:
        verbose_name = "O‘qituvchi"
        verbose_name_plural = "O‘qituvchilar"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}".strip()
        return full_name if full_name else self.user.username

    def clean(self):
        if not self.department:
            raise ValidationError({"department": "Kafedra kiritilishi kerak."})


# ======================
# BOOK
# ======================

class Book(TimeStampedModel):
    title = models.CharField("Kitob nomi", max_length=255)
    author = models.CharField("Muallif", max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Bo‘lim",
        related_name='books',
    )
    keywords = models.CharField("Kalit so‘zlar", max_length=255, blank=True)
    description = models.TextField("Tavsif", blank=True)

    pdf_file = models.FileField(
        "PDF fayl",
        upload_to='books/pdfs/',
        validators=[validate_pdf_size],
    )

    cover = models.ImageField(
        "Muqova rasmi",
        upload_to='books/covers/',
        blank=True,
        null=True,
        validators=[validate_image_size],
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Yuklagan foydalanuvchi",
        related_name='uploaded_books',
    )

    class Meta:
        verbose_name = "Kitob"
        verbose_name_plural = "Kitoblar"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def generate_cover_from_pdf(self):
        if not self.pdf_file:
            return

        try:
            self.pdf_file.seek(0)
            pdf_bytes = self.pdf_file.read()

            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            if doc.page_count == 0:
                doc.close()
                return

            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("png")
            doc.close()

            image = Image.open(BytesIO(img_data)).convert("RGB")

            output = BytesIO()
            image.save(output, format="JPEG", quality=90)
            output.seek(0)

            pdf_name = os.path.splitext(os.path.basename(self.pdf_file.name))[0]
            filename = f"{pdf_name}_{uuid.uuid4().hex[:8]}.jpg"

            self.cover.save(
                filename,
                ContentFile(output.read()),
                save=False
            )

        except Exception:
            pass

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        old_pdf_name = None
        if not is_new:
            try:
                old_obj = Book.objects.get(pk=self.pk)
                old_pdf_name = old_obj.pdf_file.name if old_obj.pdf_file else None
            except Book.DoesNotExist:
                old_pdf_name = None

        super().save(*args, **kwargs)

        pdf_changed = False
        if self.pdf_file:
            if is_new:
                pdf_changed = True
            elif old_pdf_name != self.pdf_file.name:
                pdf_changed = True

        if self.pdf_file and (not self.cover or pdf_changed):
            self.generate_cover_from_pdf()
            super().save(update_fields=['cover', 'updated_at'])


# ======================
# TEACHER FAVORITES
# ======================

class FavoriteBook(TimeStampedModel):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='favorite_books',
        verbose_name="Ustoz"
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='favorited_by_teachers',
        verbose_name="Kitob"
    )

    class Meta:
        verbose_name = "Sevimli kitob"
        verbose_name_plural = "Sevimli kitoblar"
        unique_together = ('teacher', 'book')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.teacher} - {self.book}"


# ======================
# STUDENT FAVORITES
# ======================

class StudentFavoriteBook(TimeStampedModel):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='favorite_books',
        verbose_name="Talaba"
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='favorited_by_students',
        verbose_name="Kitob"
    )

    class Meta:
        verbose_name = "Talaba sevimli kitobi"
        verbose_name_plural = "Talaba sevimli kitoblari"
        unique_together = ('student', 'book')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.book}"