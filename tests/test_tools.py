import pytest
from django.contrib.auth.models import Group

from conjunto.tools import create_groups_permissions

groups_permissions = {
    "Person Admin": {
        "test_app.Person": ["view", "add", "change", "delete"],
    },
}


@pytest.mark.django_db
def test_correct_permissions():
    create_groups_permissions(
        {"group1": {"test_app.Person": ["view", "add", "change", "delete"]}}
    )


@pytest.mark.django_db
def test_add_permissions_to_existing_group():
    create_groups_permissions(
        {"group2": {"test_app.Person": ["view", "add", "change"]}}
    )
    permissions = Group.objects.get(name="group2").permissions
    assert len(permissions.filter(codename="delete_person")) == 0

    create_groups_permissions({"group2": {"test_app.Person": ["delete"]}})
    assert len(permissions.filter(codename="view_person")) == 1
    assert len(permissions.filter(codename="add_person")) == 1
    assert len(permissions.filter(codename="change_person")) == 1
    assert len(permissions.filter(codename="delete_person")) == 1

    assert len(permissions.filter(codename="foo")) == 0


@pytest.mark.django_db
def test_add_permissions_to_nonexisting_model():
    with pytest.raises(LookupError):
        create_groups_permissions(
            {"group3": {"common.XYZ_does_not_exist": ["view", "add", "change"]}}
        )
