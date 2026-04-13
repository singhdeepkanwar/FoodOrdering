from django.db import migrations


def seed_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model("billing", "SubscriptionPlan")
    plans = [
        {
            "name": "Free",
            "price_monthly": 0,
            "max_tables": 2,
            "max_menu_items": 20,
            "has_analytics": False,
            "display_order": 0,
        },
        {
            "name": "Starter",
            "price_monthly": 499,
            "max_tables": 10,
            "max_menu_items": 100,
            "has_analytics": False,
            "display_order": 1,
        },
        {
            "name": "Pro",
            "price_monthly": 999,
            "max_tables": -1,
            "max_menu_items": -1,
            "has_analytics": True,
            "display_order": 2,
        },
    ]
    for plan in plans:
        SubscriptionPlan.objects.get_or_create(name=plan["name"], defaults=plan)


def reverse_seed(apps, schema_editor):
    SubscriptionPlan = apps.get_model("billing", "SubscriptionPlan")
    SubscriptionPlan.objects.filter(name__in=["Free", "Starter", "Pro"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_plans, reverse_seed),
    ]
