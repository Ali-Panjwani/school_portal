from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Marksheet, Student, Teacher
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from django.views.generic import UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist

import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

def home(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    elif request.user.profile.status == 'S':
        return redirect('core:student-portal')
    elif request.user.profile.status == 'T':
        return redirect('core:teacher-portal')
    elif request.user.profile.status == 'A':
        return redirect('core:admin-portal')

@login_required
def student_portal(request):
    student = Student.objects.get(profile=request.user.profile)
    class_joined = student.class_joined
    current_class = student.current_class
    context = {
        'class_list': range(class_joined, current_class+1)
    }
    return render(request, 'student-portal.html', context)


def calc_overall(marksheets):
    mid_term_marks = 0
    final_term_marks = 0
    for marksheet in marksheets:
        mid_term_marks += marksheet.mid_term_marks
        final_term_marks += marksheet.final_term_marks
    mid_term_marks = mid_term_marks / len(marksheets)
    final_term_marks = final_term_marks / len(marksheets)
    percentage = (mid_term_marks + final_term_marks) / 2
    if percentage > 90:
        final_grade = 'A'
    elif percentage > 80:
        final_grade = 'B'
    elif percentage > 80:
        final_grade = 'C'
    elif percentage > 80:
        final_grade = 'D'
    elif percentage > 80:
        final_grade = 'E'
    else:
        final_grade = 'F'
    return mid_term_marks, final_term_marks, percentage, final_grade

@login_required
def student_marksheet(request, username, grade):
    std_user = User.objects.get(username=username)
    std = Student.objects.get(profile=std_user.profile)
    marksheets = Marksheet.objects.filter(pupil=std, student_grade=grade)
    if marksheets:
        mid_term_marks, final_term_marks, percentage, final_grade = calc_overall(marksheets)
        context = {
            'marksheets': marksheets,
            'class': grade,
            'mid_term_marks': mid_term_marks, 
            'final_term_marks': final_term_marks,
            'percentage': percentage,
            'final_grade': final_grade,
            'student': std
        }
        return render(request, 'marksheets.html', context)
    else:
        messages.warning(request, 'There Was No Marksheet Found For This Class')
        if request.user.profile.status == 'S':
            return redirect('core:student-portal')
        else:
            return redirect('core:student-detail-admin', username=username)

@login_required
def marksheet_pdf(request, username, grade):
    std_user = User.objects.get(username=username)
    std = Student.objects.get(profile=std_user.profile)
    marksheets = Marksheet.objects.filter(pupil=std, student_grade=grade)
    mid_term_marks, final_term_marks, percentage, final_grade = calc_overall(marksheets)

    buffer = io.BytesIO()

    from reportlab.lib.pagesizes import A4
    w, h = A4
    center = int(w / 2)

    p = canvas.Canvas(buffer)

    y = 700

    p.drawString(center-45, 770, 'Al-Hadi Academy')
    p.drawString(70, 740, f'Name: {request.user.profile.first_name} {request.user.profile.last_name}')
    p.drawString(180, 740, f'Grade: {grade}')

    p.drawString(50, y, 'Subject')
    p.drawString(110, y, 'Marked By')
    p.drawString(180, y, 'Mid-Term Percentage')
    p.drawString(310, y, 'Final-Term Percentage')
    p.drawString(460, y, 'Final Grade')

    for marksheet in marksheets:
        y -= 30
        p.drawString(50, y, marksheet.get_subject_display())
        teacher_name = marksheet.teacher.profile.first_name + ' ' + marksheet.teacher.profile.last_name
        if len(teacher_name) > 7:
            teacher_name = teacher_name[:7] + '...'
        p.drawString(110, y, f"{teacher_name}")
        p.drawString(180, y, f"{marksheet.mid_term_marks}")
        p.drawString(310, y, f"{marksheet.final_term_marks}")
        p.drawString(460, y, marksheet.final_grade)

    y -= 30
    p.drawString(50, y, 'Overall')
    p.drawString(180, y, f"{mid_term_marks}")
    p.drawString(310, y, f"{final_term_marks}")
    p.drawString(460, y, f"{final_grade} ({percentage}%)")

    p.showPage()
    p.save()

    buffer.seek(0)

    return FileResponse(buffer, filename='hello.pdf')


@login_required
def teacher_portal(request):
    teacher = Teacher.objects.get(profile=request.user.profile)
    students = teacher.student_set.all()
    context = {
        'students': students
    }
    return render(request, 'teacher-portal.html', context)


@login_required
def profile(request):
    if request.user.profile.status == 'S':
        std = Student.objects.get(profile=request.user.profile)
        return render(request, 'profile.html', {'std': std})
    elif request.user.profile.status == 'T':
        teacher = Teacher.objects.get(profile=request.user.profile)
        return render(request, 'profile.html', {'teacher': teacher})
    elif request.user.profile.status == 'A':
        return render(request, 'profile.html')
    


@login_required
def student_info(request, username):
    if request.user.profile.status == 'T':
        std_user = User.objects.get(username=username)
        std = Student.objects.get(profile=std_user.profile)
        teacher = Teacher.objects.get(profile=request.user.profile)
        marksheets = Marksheet.objects.filter(pupil=std, teacher=teacher)
        context = {
            'student': std,
            'marksheets': marksheets
        }
        return render(request, 'student_info.html', context)

class MarksheetUpdateView(UpdateView):
    model = Marksheet
    fields = ['mid_term_marks', 'final_term_marks', 'final_grade']
    template_name = 'update_marksheet.html'

def admin_portal(request):
    return render(request, 'admin-portal.html')

def students_admin(request):
    if request.user.profile.status == 'A':
        students = Student.objects.all().order_by('current_class')
        context = {
            'students': students
        }
        return render(request, 'students-admin.html', context)
    else:
        raise PermissionDenied

def student_detail_admin(request, username):
    if request.user.profile.status == 'A':
        std_user = User.objects.get(username=username)
        std = Student.objects.get(profile=std_user.profile)
        current_class = std.current_class
        class_joined = std.class_joined
        teachers = std.current_teachers.all()
        context = {
            'student': std,
            'class_list': range(class_joined, current_class+1),
            'teachers': teachers
        }
        return render(request, 'student-detail-admin.html', context)


class TeachersAdminView(ListView):
    context_object_name = 'teachers'
    model = Teacher
    template_name = 'teachers-admin.html'

class TeacherDetailAdminView(DetailView):
    model = Teacher
    template_name = 'teacher-detail-admin.html'
    context_object_name = 'teacher'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = Teacher.objects.get(pk=self.kwargs['pk'])
        context['students'] = teacher.student_set.all()
        return context