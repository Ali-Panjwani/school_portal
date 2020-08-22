from django.contrib import admin
from .models import Profile, Student, Teacher, Marksheet, Class, FinalGrades

admin.site.register(Profile)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Marksheet)
admin.site.register(Class)
admin.site.register(FinalGrades)
