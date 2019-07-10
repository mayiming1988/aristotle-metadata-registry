from django.test import TestCase

from django.core.management import call_command


class TestFixtures(TestCase):
    def test_fixtures(self):
        call_command('loaddata', 'iso_metadata.json')
        call_command('loaddata', 'test_metadata.json')
