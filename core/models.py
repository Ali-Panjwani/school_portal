from django.db import models
from django.conf import settings
from django.urls import reverse

import datetime

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    birthdate = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)
    STATUS_CHOICES = [
        ('S', 'Student'),
        ('T', 'Teacher'),
        ('A', 'Admin')
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        unique_together = ['first_name', 'last_name']
    

CLASS_CHOICES = (
    (1, 'Class 1'),
    (2, 'Class 2'),
    (3, 'Class 3'),
    (4, 'Class 4'),
    (5, 'Class 5'),
    (6, 'Class 6'),
    (7, 'Class 7'),
    (8, 'Class 8'),
    (9, 'Class 9'),
    (10, 'Class 10'),
)

class Student(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    class_joined = models.IntegerField(blank=True, null=True, choices=CLASS_CHOICES)
    current_class = models.IntegerField(blank=True, null=True, choices=CLASS_CHOICES)
    current_teachers = models.ManyToManyField(to='Teacher')
    school_finished = models.BooleanField(default=False)
    final_result_calculated = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.profile.first_name} {self.profile.last_name}'
    
class Teacher(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    TEACHER_SUBJECTS = [
        ('M', 'Maths'),
        ('S', 'Science'),
        ('E', 'English')
    ]
    subject = models.CharField(max_length=1, choices=TEACHER_SUBJECTS)
    classes = models.ManyToManyField(to='Class')

    def __str__(self):
        return f'{self.profile.first_name} {self.profile.last_name}'


GRADE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F')
    ]

class Marksheet(models.Model):
    pupil = models.ForeignKey(Student, on_delete=models.CASCADE)
    student_grade = models.IntegerField()
    teacher = models.ForeignKey(Teacher, blank=True, null=True, on_delete=models.SET_NULL)
    MARKSHEET_SUBJECTS = [
        ('M', 'Maths'),
        ('S', 'Science'),
        ('E', 'English'),
        ('O', 'Overall')
    ]
    subject = models.CharField(max_length=1, choices=MARKSHEET_SUBJECTS)
    mid_term_marks = models.IntegerField(blank=True, null=True)
    final_term_marks = models.IntegerField(blank=True, null=True)
    
    final_grade = models.CharField(max_length=1, choices=GRADE_CHOICES, blank=True, null=True)
    current = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pupil.profile.first_name} {self.pupil.profile.last_name}'s Marksheet"
    
    def get_absolute_url(self):
        return reverse('core:teacher-portal')

    
class Class(models.Model):
    grade = models.IntegerField(choices=CLASS_CHOICES)

    def __str__(self):
        return f"Grade {self.grade}"

    class Meta:
        verbose_name_plural = 'classes'

class FinalGrades(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    grade = models.CharField(max_length=1, choices=CLASS_CHOICES)
    mid_term_marks = models.IntegerField()
    final_term_marks = models.IntegerField()
    percentage = models.IntegerField()
    final_grade = models.CharField(max_length=1, choices=GRADE_CHOICES)

    def __str__(self):
        return f"{self.student.profile.first_name} {self.student.profile.last_name}'s Final Grades For Class {self.grade}"

    class Meta:
        verbose_name_plural = 'Final Grades'