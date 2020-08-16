from django.urls import path
from .views import (
    home,
    student_portal, 
    teacher_portal,
    student_marksheet,
    marksheet_pdf, 
    profile, 
    student_info,
    MarksheetUpdateView,
    admin_portal,
    students_admin,
    TeachersAdminView,
    student_detail_admin,
    TeacherDetailAdminView
)

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
    path('accounts/profile/', profile, name='profile'),
    path('student-portal/', student_portal, name='student-portal'),
    path('marksheet/<str:username>/<int:grade>/', student_marksheet, name='student-marksheet'),
    path('marksheet/<str:username>/<int:grade>/pdf/', marksheet_pdf, name='marksheet-pdf'),
    path('teacher-portal/', teacher_portal, name='teacher-portal'),
    path('student/<str:username>/', student_info, name='student-info'),
    path('teacher-portal/marksheet/<int:pk>/update/', MarksheetUpdateView.as_view(), name='update-marksheet'),
    path('admin-portal/', admin_portal, name='admin-portal'),
    path('admin-portal/students/', students_admin, name='students-admin'),
    path('admin-portal/student/<str:username>/', student_detail_admin, name='student-detail-admin'),
    path('admin-portal/teachers/', TeachersAdminView.as_view(), name='teachers-admin'),
    path('admin-portal/teacher/<int:pk>/', TeacherDetailAdminView.as_view(), name='teacher-detail-admin')
]
