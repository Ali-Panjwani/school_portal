from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .models import Marksheet, Student, Teacher, Profile, Class
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from django.views.generic import UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from .forms import CreateUserForm, CreateProfileForm, CreateTeacherForm, CreateStudentForm, StatusForm
from django.db.models import Q

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
        if request.method == 'POST':
            search = request.POST.get('search', None)
            # print(search)
            if search != '' and search is not None:
                students = students.filter(Q(profile__first_name__icontains=search) | Q(profile__last_name__icontains=search)).order_by('current_class')
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

def create_user(request):
    if request.method == 'POST':
        u_form = CreateUserForm(request.POST)
        s_form = StatusForm(request.POST)
        if u_form.is_valid() and s_form.is_valid():
            u_form.save()
            profile = Profile.objects.get(user__username = u_form.cleaned_data['username'])
            if s_form.cleaned_data['status'] == 'S':
                profile.status = 'S'
                profile.save()
                s = Student(profile=profile)
                s.save()
            elif s_form.cleaned_data['status'] == 'T':
                profile.status = 'T'
                profile.save()
                t = Teacher(profile=profile)
                t.save()
            elif s_form.cleaned_data['status'] == 'A':
                profile.status = 'A'
                profile.save()

            return redirect('core:create-profile', username=u_form.cleaned_data['username'])
    elif request.method == 'GET':
        u_form = CreateUserForm()
        s_form = StatusForm()

    context = {
        'form': u_form,
        'form2': s_form,
        'title': 'Create New User'
    }
    return render(request, 'create_user.html', context)

def create_profile(request, username):
    user = User.objects.get(username=username)
    if request.method == 'POST':
        p_form = CreateProfileForm(request.POST, instance=user.profile)
        if p_form.is_valid():
            p_form.save()
            if user.profile.status == 'A':
                user.is_staff = True
                user.save()
                messages.success(request, 'User Created Successfully')
                return redirect('core:home', permanent=True)
            else:
                return redirect('core:create-student', username=username, permanent=True)
    elif request.method == 'GET':
        p_form = CreateProfileForm(instance=user.profile)

    context = {
        'form': p_form,
        'title': f"Create {user.username}'s profile"
    }
    return render(request, 'create_user.html', context)

def create_student(request, username):
    user = User.objects.get(username=username)
    if request.method == 'POST':
        if user.profile.status == 'S':
            form = CreateStudentForm(request.POST, instance=user.profile.student)
        elif user.profile.status == 'T':
            form = CreateTeacherForm(request.POST, instance=user.profile.teacher)
        else:
            raise Http404

        if form.is_valid():
            form.save()
            messages.success(request, 'User Created Successfully')
            return redirect('core:home', permanent=True)

    elif request.method == 'GET':
        if user.profile.status == 'S':
            form = CreateStudentForm(request.POST)
        elif user.profile.status == 'T':
            form = CreateTeacherForm(request.POST)
        else:
            raise Http404

    context = {
        'form': form,
        'title': f"Enter More Info About {user.profile.first_name} {user.profile.last_name}"
    }
    return render(request, 'create_user.html', context)

def classes_view(request):
    if request.user.profile.status == 'A':
        classes = Class.objects.all()
        context = {
            'classes': classes
        }
        return render(request, 'classes.html', context)
    else:
        raise PermissionDenied

def class_detail_view(request, grade):
    if request.user.profile.status == 'A':
        class_grade = Class.objects.get(grade=grade)
        teachers = class_grade.teacher_set.all()
        context = {
            'teachers': teachers,
            'grade': grade
        }
        return render(request, 'class-detail.html', context)
    else:
        raise PermissionDenied

def is_query_valid(query):
    return query != '' and query is not None


def edit_class_teachers(request, grade):
    if request.user.profile.status == 'A':
        class_grade = Class.objects.get(grade=grade)
        class_teachers = class_grade.teacher_set.all()
        teachers = Teacher.objects.all()
        if request.method == 'GET':
            first = request.GET.get('first')
            last = request.GET.get('last')
            subject = request.GET.get('subject')
            if is_query_valid(first) and is_query_valid(last):
                teachers = teachers.filter(profile__first_name__icontains=first, profile__last_name__icontains=last)
            elif is_query_valid(first):
                print(first)
                teachers = teachers.filter(profile__first_name__icontains=first)
            elif is_query_valid(last):
                print(last)
                teachers = teachers.filter(profile__last_name__icontains=last)

            if is_query_valid(subject):
                teachers = teachers.filter(subject__icontains=subject[0])
            context = {
                'class_teachers': class_teachers,
                'teachers': teachers,
                'grade': grade
            }
            return render(request, 'edit-class-teachers.html', context)
        else:
            for t in teachers:
                check = request.POST.get(str(t.pk))
                if check == 'on':
                    t.classes.add(class_grade)
                    t.save()
                else:
                    if t in class_teachers:
                        t.classes.remove(class_grade)
            messages.success(request, f'Teachers for class {grade} edited successfully')
            return redirect('core:class-detail', grade=grade)
    else:
        raise PermissionDenied