from django.test import TestCase
from .models import Project
from django.contrib.auth.models import User

# Create your tests here.
class ProjectTestCase(TestCase):
    def setUp(self):
        User.objects.create_user('test','test@test.com','test1234')
    
    def test_project_exists(self):
        exists = Project.objects.filter(id=1).exists()