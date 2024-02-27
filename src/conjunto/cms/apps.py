from django.apps import AppConfig


class CmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "conjunto.cms"

    groups_permissions = {
        "Content editor": {
            "cms.StaticPage": ["view", "add", "change", "delete"],
            "cms.TermsConditionsPage": ["view", "add", "change", "delete"],
            "cms.PrivacyPage": ["view", "add", "change", "delete"],
        },
    }
