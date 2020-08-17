from django.db import models
from django.conf import settings
from django.urls import reverse

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    birthdate = models.DateField(blank=True, null=True)
    date_joined = models.DateField(blank=True, null=True)
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
    
class Student(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    class_joined = models.IntegerField(blank=True, null=True)
    current_class = models.IntegerField(blank=True, null=True)
    class_passed = models.BooleanField(default=False)
    current_teachers = models.ManyToManyField(to='Teacher')

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

    def __str__(self):
        return f'{self.profile.first_name} {self.profile.last_name}'


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
    mid_term_marks = models.IntegerField()
    final_term_marks = models.IntegerField()
    GRADE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F')
    ]
    final_grade = models.CharField(max_length=1, choices=GRADE_CHOICES)

    def __str__(self):
        return f"{self.pupil.profile.first_name} {self.pupil.profile.last_name}'s Marksheet"
    
    def get_absolute_url(self):
        return reverse('core:teacher-portal')