from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Student, Teacher


STATUS_CHOICES = (
    ('S', 'Student'),
    ('A', 'Admin'),
    ('T', 'Teacher')
)

class CreateUserForm(UserCreationForm):
    # payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email']

class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'image', 'birthdate']

class CreateStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['class_joined']

class CreateTeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['subject']

class StatusForm(forms.Form):
    status = forms.ChoiceField(widget=forms.RadioSelect(), choices=STATUS_CHOICES)