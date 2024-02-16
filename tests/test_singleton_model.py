import pytest
from django.core.exceptions import ValidationError
from conjunto.models import SingletonModel

# FIXME: these tests are completely untested, done by ChatGPT. Make them useful.


class TestSingletonModel(SingletonModel):
    pass


@pytest.fixture
def instance():
    m = TestSingletonModel()
    m.save()
    return m


@pytest.mark.django_db
def test_save_single_instance():
    instance = TestSingletonModel()
    instance.save()
    assert TestSingletonModel.objects.count() == 1


@pytest.mark.django_db
def test_save_2_single_instances():
    instance = TestSingletonModel()
    instance.save()
    instance = TestSingletonModel()
    instance.save()
    assert TestSingletonModel.objects.count() == 1


@pytest.mark.django_db
def test_save_multiple_instances():
    with pytest.raises(ValidationError):
        instance1 = TestSingletonModel()
        instance1.save()
        instance2 = TestSingletonModel()
        instance2.save()


@pytest.mark.django_db
def test_load_existing_instance():
    instance = TestSingletonModel()
    instance.save()
    loaded_instance = TestSingletonModel.load()
    assert instance == loaded_instance


@pytest.mark.django_db
def test_load_no_instance(instance):
    loaded_instance = TestSingletonModel.load()
    assert isinstance(loaded_instance, TestSingletonModel)
