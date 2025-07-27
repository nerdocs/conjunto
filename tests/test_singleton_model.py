import pytest
from django.core.exceptions import ValidationError
from tests.test_app.models import SingletonTestModel


# FIXME: these tests are completely untested, done by ChatGPT. Make them useful.


@pytest.fixture
def instance():
    m = SingletonTestModel()
    m.save()
    return m


@pytest.mark.django_db
def test_save_single_instance():
    instance = SingletonTestModel()
    instance.save()
    assert SingletonTestModel.objects.count() == 1


@pytest.mark.django_db
def test_save_2_single_instances():
    instance = SingletonTestModel()
    instance.save()
    instance = SingletonTestModel()
    instance.save()
    assert SingletonTestModel.objects.count() == 1


@pytest.mark.django_db
def test_load_existing_instance(instance):
    loaded_instance = SingletonTestModel.get_instance()
    assert instance == loaded_instance


@pytest.mark.django_db
def test_load_no_instance():
    loaded_instance = SingletonTestModel.get_instance()
    assert not loaded_instance.pk
    assert isinstance(loaded_instance, SingletonTestModel)
