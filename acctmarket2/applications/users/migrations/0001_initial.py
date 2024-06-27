# Generated by Django 4.2.13 on 2024-06-27 15:18

import acctmarket2.applications.users.managers
import auto_prefetch
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Name of User"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="email address"
                    ),
                ),
                (
                    "phone_no",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=20,
                        verbose_name="Phone number",
                    ),
                ),
                (
                    "country",
                    django_countries.fields.CountryField(
                        blank=True, max_length=2, verbose_name="Country"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
                "base_manager_name": "prefetch_manager",
            },
            managers=[
                ("objects", acctmarket2.applications.users.managers.UserManager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="Account",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "owner",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owned_accounts",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Account Owner",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Accounts",
                "ordering": ["-created_at"],
                "abstract": False,
                "base_manager_name": "prefetch_manager",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="MarketingAndSales",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "marketing_strategy",
                    models.TextField(verbose_name="Marketing Strategy"),
                ),
                (
                    "account",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to="users.account",
                        verbose_name="Account",
                    ),
                ),
                (
                    "user",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Marketing and Sales",
                "ordering": ["-created_at"],
                "abstract": False,
                "base_manager_name": "prefetch_manager",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="LiveChatSupport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "languages_spoken",
                    models.CharField(max_length=100, verbose_name="Languages Spoken"),
                ),
                (
                    "account",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to="users.account",
                        verbose_name="Account",
                    ),
                ),
                (
                    "user",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Live Chat Supports",
                "ordering": ["-created_at"],
                "abstract": False,
                "base_manager_name": "prefetch_manager",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="HelpDeskTechnicalSupport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("technical_skills", models.TextField(verbose_name="Technical Skills")),
                (
                    "account",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to="users.account",
                        verbose_name="Account",
                    ),
                ),
                (
                    "user",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Help Desk Technical Supports",
                "ordering": ["-created_at"],
                "abstract": False,
                "base_manager_name": "prefetch_manager",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="DigitalGoodsDistribution",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "delivery_method",
                    models.CharField(max_length=50, verbose_name="Delivery Method"),
                ),
                (
                    "account",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to="users.account",
                        verbose_name="Account",
                    ),
                ),
                (
                    "user",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Digital Goods Distributions",
                "ordering": ["-created_at"],
                "abstract": False,
                "base_manager_name": "prefetch_manager",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="CustomerSupportRepresentative",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "department",
                    models.CharField(max_length=100, verbose_name="Department"),
                ),
                (
                    "account",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to="users.account",
                        verbose_name="Account",
                    ),
                ),
                (
                    "user",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Customer Support Representatives",
                "ordering": ["-created_at"],
                "abstract": False,
                "base_manager_name": "prefetch_manager",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "account",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to="users.account",
                        verbose_name="Account",
                    ),
                ),
                (
                    "user",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
                "base_manager_name": "prefetch_manager",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="ContentManager",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "expertise_area",
                    models.CharField(max_length=255, verbose_name="Expertise Area"),
                ),
                (
                    "account",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to="users.account",
                        verbose_name="Account",
                    ),
                ),
                (
                    "user",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Content Managers",
                "ordering": ["-created_at"],
                "abstract": False,
                "base_manager_name": "prefetch_manager",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="AffiliatePartner",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "affiliate_code",
                    models.CharField(max_length=20, verbose_name="Affiliate Code"),
                ),
                (
                    "account",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to="users.account",
                        verbose_name="Account",
                    ),
                ),
                (
                    "user",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Affiliate Partners",
                "ordering": ["-created_at"],
                "abstract": False,
                "base_manager_name": "prefetch_manager",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="Administrator",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "department",
                    models.CharField(max_length=100, verbose_name="Department"),
                ),
                (
                    "account",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to="users.account",
                        verbose_name="Account",
                    ),
                ),
                (
                    "user",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Administrators",
                "ordering": ["-created_at"],
                "abstract": False,
                "base_manager_name": "prefetch_manager",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="Accountant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("visible", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "financial_software_used",
                    models.CharField(
                        max_length=100, verbose_name="Financial Software Used"
                    ),
                ),
                (
                    "account",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to="users.account",
                        verbose_name="Account",
                    ),
                ),
                (
                    "user",
                    auto_prefetch.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_profiles",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Accountants",
                "ordering": ["-created_at"],
                "abstract": False,
                "base_manager_name": "prefetch_manager",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
    ]
