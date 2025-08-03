import uuid

import pytest
from django.db import models
from django.utils.functional import LazyObject
from pytest_mock import mocker

from django.utils.translation import gettext as _

from conjunto.audit_log.formatter import LogFormatter
from gdaps import hooks

from conjunto.audit_log.registry import LogActionRegistry


# @hooks.implements("register_log_actions")
# def log_actions(actions: LogActionRegistry):
#     # define basic generic hooks for your app
#     actions.register_action("sale", _("Sell product"), _("Product sold"))
#     actions.register_action("return", _("Return product"), _("Product returned"))


def test_register_action():
    """Test if actions are registered correctly and can bei found in the registry."""
    registry = LogActionRegistry()
    registry.register_action("foo", _("Foo"), _("Foo"))
    registry.register_action("bar", _("Bar"), _("Bar"))

    assert "foo" in registry
    assert "bar" in registry
    assert "baz" not in registry
    assert "sale" not in registry


def test_register_action_missing_message():
    """Test if register_action raises ValueError when only label is provided."""
    registry = LogActionRegistry()
    with pytest.raises(ValueError, match="Both label and message must be provided"):
        registry.register_action("test_action", label="Test Label")


def test_register_action_missing_label():
    """Test if register_action raises ValueError when only message is provided."""
    registry = LogActionRegistry()
    with pytest.raises(ValueError, match="Both label and message must be provided"):
        registry.register_action("test_action", message="Test Message")


def test_register_action_as_decorator():
    """Test if register_action can be used as a decorator."""
    registry = LogActionRegistry()

    @registry.register_action("test_decorator_action")
    class CustomLogFormatter(LogFormatter):
        label = "Test Decorator Label"
        message = "Test Decorator Message"

    assert "test_decorator_action" in registry
    assert registry.formatters["test_decorator_action"].label == "Test Decorator Label"
    assert (
        registry.formatters["test_decorator_action"].message == "Test Decorator Message"
    )
    assert ("test_decorator_action", "Test Decorator Label") in registry.choices


def test_scan_for_actions_runs_once(mocker):
    """Test that scan_for_actions only runs hook functions once."""
    registry = LogActionRegistry()

    # Create a mock hook function
    mock_hook = mocker.Mock()

    # Patch the hooks.get_hooks to return our mock
    mocker.patch("gdaps.hooks.get_hooks", return_value=[mock_hook])

    # Call scan_for_actions twice
    registry.scan_for_actions()
    registry.scan_for_actions()

    # Verify the hook was only called once
    mock_hook.assert_called_once_with(registry)
    assert registry.has_scanned_for_actions is True


def test_register_model():
    """Test if models are registered correctly in the registry."""
    registry = LogActionRegistry()

    # Create mock models
    class MockModel:
        pass

    class MockLogEntryModel:
        pass

    # Register the model
    registry.register_model(MockModel, MockLogEntryModel)

    # Check if the model was registered correctly
    assert MockLogEntryModel in registry.log_entry_models
    assert registry.log_entry_models_by_type.get_by_type(MockModel) == MockLogEntryModel

    # Register another model
    class AnotherModel:
        pass

    registry.register_model(AnotherModel, MockLogEntryModel)

    # Check if both models point to the same log entry model
    assert len(registry.log_entry_models) == 1
    assert (
        registry.log_entry_models_by_type.get_by_type(AnotherModel) == MockLogEntryModel
    )


def test_get_log_entry_models():
    """Test if get_log_entry_models returns all registered log entry models."""
    registry = LogActionRegistry()

    # Create mock models
    class Model1:
        pass

    class Model2:
        pass

    class LogEntryModel1:
        pass

    class LogEntryModel2:
        pass

    # Register models with different log entry models
    registry.register_model(Model1, LogEntryModel1)
    registry.register_model(Model2, LogEntryModel2)

    # Get all registered log entry models
    log_entry_models = registry.get_log_entry_models()

    # Check if both log entry models are in the set
    assert len(log_entry_models) == 2
    assert LogEntryModel1 in log_entry_models
    assert LogEntryModel2 in log_entry_models

    # Register another model with an existing log entry model
    class Model3:
        pass

    registry.register_model(Model3, LogEntryModel1)

    # Check that we still have only two unique log entry models
    log_entry_models = registry.get_log_entry_models()
    assert len(log_entry_models) == 2


def test_get_formatter():
    """Test that get_formatter returns the correct formatter for a log entry."""
    registry = LogActionRegistry()

    # Register two actions with different formatters
    registry.register_action("action1", _("Action One"), _("Action One Message"))
    registry.register_action("action2", _("Action Two"), _("Action Two Message"))

    # Create mock log entries
    class MockLogEntry:
        def __init__(self, action):
            self.action = action

    log_entry1 = MockLogEntry("action1")
    log_entry2 = MockLogEntry("action2")
    log_entry3 = MockLogEntry("non_existent_action")

    # Test getting formatters
    formatter1 = registry.get_formatter(log_entry1)
    formatter2 = registry.get_formatter(log_entry2)
    formatter3 = registry.get_formatter(log_entry3)

    # Verify correct formatters are returned
    assert formatter1.label == "Action One"
    assert formatter1.message == "Action One Message"
    assert formatter2.label == "Action Two"
    assert formatter2.message == "Action Two Message"
    assert formatter3 is None  # Non-existent action should return None


def test_get_log_model_for_instance_handles_lazy_objects():
    """Test that get_log_model_for_instance unwraps LazyObject instances correctly."""
    # FIXME
    registry = LogActionRegistry()

    # Create a model class and its corresponding log entry model
    class TestModel(models.Model):
        class Meta:
            app_label = "test"

    class TestLogEntryModel:
        pass

    # Register the model with the registry
    registry.register_model(TestModel, TestLogEntryModel)

    # Create a LazyObject that wraps our TestModel instance
    test_instance = TestModel()

    class MockLazyObject(LazyObject):
        def __init__(self):
            super().__init__()
            self._wrapped = test_instance

    lazy_instance = MockLazyObject()

    # Test that the registry correctly unwraps the LazyObject
    log_model = registry.get_log_model_for_instance(lazy_instance)

    # Verify we got the correct log entry model
    assert log_model == TestLogEntryModel

    # Also verify direct model lookup works
    direct_log_model = registry.get_log_model_for_instance(test_instance)
    assert direct_log_model == TestLogEntryModel


def test_log_with_explicit_user_and_uuid(mocker):
    """Test that log method correctly uses provided user and UUID instead of active context."""
    registry = LogActionRegistry()

    # Create mock models and instances
    class TestModel(models.Model):
        class Meta:
            app_label = "test"

    class TestLogEntryModel:
        objects = mocker.Mock()

    test_instance = TestModel()
    test_user = mocker.Mock()
    test_uuid = uuid.uuid4()

    # Register the model with the registry
    registry.register_model(TestModel, TestLogEntryModel)

    # Register a test action
    registry.register_action("test_action", "Test Action", "Test Action Message")

    # Setup mock for active context (should not be used in this test)
    mock_context = mocker.Mock()
    mock_context.user = mocker.Mock(name="context_user")
    mock_context.uuid = uuid.uuid4()
    mocker.patch(
        "conjunto.audit_log.registry.get_active_log_context", return_value=mock_context
    )

    # Call log with explicit user and uuid
    registry.log(
        test_instance,
        "test_action",
        user=test_user,
        uuid=test_uuid,
        extra_param="value",
    )

    # Verify log_action was called with the explicit parameters, not from context
    TestLogEntryModel.objects.log_action.assert_called_once_with(
        test_instance,
        "test_action",
        user=test_user,
        uuid=test_uuid,
        extra_param="value",
    )

    # Verify the context values were not used
    assert (
        TestLogEntryModel.objects.log_action.call_args[1]["user"] != mock_context.user
    )
    assert (
        TestLogEntryModel.objects.log_action.call_args[1]["uuid"] != mock_context.uuid
    )


def test_get_logs_for_instance_with_unregistered_model(mocker):
    """Test that get_logs_for_instance returns an empty queryset for unregistered models."""
    registry = LogActionRegistry()

    # Create a model instance that is not registered
    class UnregisteredModel(models.Model):
        class Meta:
            app_label = "test"

    unregistered_instance = UnregisteredModel()

    # Mock the ModelLogEntry and its objects.none() method
    mock_none_queryset = mocker.Mock(name="empty_queryset")
    mock_model_log_entry = mocker.Mock()
    mock_model_log_entry.objects.none.return_value = mock_none_queryset

    # Patch the import of ModelLogEntry
    mocker.patch("conjunto.audit_log.models.ModelLogEntry", mock_model_log_entry)

    # Call get_logs_for_instance with the unregistered model instance
    result = registry.get_logs_for_instance(unregistered_instance)

    # Verify that ModelLogEntry.objects.none() was called and its result returned
    mock_model_log_entry.objects.none.assert_called_once()
    assert result == mock_none_queryset
