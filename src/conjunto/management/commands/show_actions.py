from django.core.management.base import BaseCommand
from django.utils.termcolors import colorize
from conjunto.audit_log.registry import log_action_registry

WIDTH = 100


class Command(BaseCommand):
    """
    Management command to list all registered log actions in the LogActionRegistry.
    """

    help = "Lists all registered log actions with their labels and messages."

    def add_arguments(self, parser):
        parser.add_argument(
            "--filter",
            help="Filter actions by name (case-insensitive substring match)",
            default="",
        )

    def handle(self, *args, **options):
        # Ensure all actions are loaded
        log_action_registry.scan_for_actions()

        filter_text = options["filter"].lower()

        # Get all formatters
        formatters = log_action_registry.formatters

        if not formatters:
            self.stdout.write(self.style.WARNING("No log actions registered."))
            return

        self.stdout.write(self.style.MIGRATE_HEADING("Registered Log Actions:"))
        # Print header
        self.stdout.write("=" * WIDTH)
        self.stdout.write(f"{'Action':<{WIDTH // 2}} {'Label':<{WIDTH // 4}} Message")
        self.stdout.write("-" * WIDTH)

        # Sort actions alphabetically
        actions = sorted(formatters.keys())

        # Filter actions if filter parameter is provided
        if filter_text:
            actions = [action for action in actions if filter_text in action.lower()]

        if not actions:
            self.stdout.write(
                self.style.WARNING(f"No actions found matching filter: '{filter_text}'")
            )
            return

        # Print each action with its label and message
        for action in actions:
            formatter = formatters[action]
            self.stdout.write(
                f"{colorize(action, fg='green'):<{WIDTH // 2+9}} "  # colorize= +9 chars
                f"{formatter.label:<{WIDTH // 4}} "
                f"{formatter.message}"
            )

        # Print summary
        self.stdout.write("-" * WIDTH)
        self.stdout.write(self.style.SUCCESS(f"Total: {len(actions)} action(s)"))

        # Print registered models
        self.stdout.write("\n")
        self.stdout.write(self.style.MIGRATE_HEADING("Registered Log Models:"))
        self.stdout.write("=" * WIDTH)

        log_models = log_action_registry.get_log_entry_models()
        if not log_models:
            self.stdout.write(self.style.WARNING("No log models registered."))
            return

        for model in log_models:
            self.stdout.write(f"{model.__module__}.{model.__name__}")

        self.stdout.write("-" * WIDTH)
        self.stdout.write(self.style.SUCCESS(f"Total: {len(log_models)} model(s)"))
