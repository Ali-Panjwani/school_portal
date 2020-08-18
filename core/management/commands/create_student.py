from django.core.management.base import BaseCommand
from core.models import Profile, Student, Teacher
from django.contrib.auth.models import User

from django.utils import timezone
import random
import datetime

def generate_birthdate():
    year = random.randint(2004, 2016)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime.date(year, month, day)

def get_teacher():
    t = Teacher.objects.get(pk=random.randint(5, 7))

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)
    
    def handle(self, *args, **kwargs):
        count = kwargs['count']
        for i in range(count):
            u = User(username=f'new_user00{i}', password='testing789')
            u.save()
            p = Profile.objects.get(user=u)
            p.user = u
            p.first_name='SchoolStudent'
            p.last_name=str(i)
            p.birthdate=generate_birthdate()
            p.date_joined=generate_birthdate()
            p.status='S'
            p.save()

            s = Student(
                profile=p,
                class_joined = random.randint(1, 5),
                current_class = random.randint(6, 10),
                class_passed = False,
            )
            s.save()
            s.current_teachers.add(get_teacher())
            s.save()

        self.stdout.write(self.style.SUCCESS('Students Created Successfully'))