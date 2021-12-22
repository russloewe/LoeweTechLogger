import datetime
import pytz
from functools import reduce
from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User, UserManager
from django.contrib.auth import login, logout, authenticate
from ..models import Log, Patient


class LogTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(
            username="test user", email="test@test.com",
            password="test")
        Patient.objects.create(
            dob='2001-01-01', name="test patient"
        )
        Log.objects.create(
            patient=Patient.objects.get(name="test patient"),
            user=User.objects.get(name="test user"),
            carbs=3
            )

    def test_get_logs(self):
        logs = Log.objects.get(patient=Patient.objects.get(name="test patient"))
        self.assertEqual(len(logs),2)