# Generated by Django 4.2.13 on 2024-06-27 18:43

import auto_prefetch
import ckeditor_uploader.fields
import cloudinary.models
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        (
            "taggit",
            "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Announcement",
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
                ("title", models.CharField(blank=True, default="", max_length=50)),
                (
                    "content",
                    ckeditor_uploader.fields.RichTextUploadingField(
                        default="", null=True, verbose_name="Description"
                    ),
                ),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Announcement",
                "verbose_name_plural": "Announcements",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="Banner",
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
                ("title", models.CharField(blank=True, default="", max_length=50)),
                (
                    "image",
                    cloudinary.models.CloudinaryField(
                        blank=True, default="", max_length=255, verbose_name="image"
                    ),
                ),
                ("slug", models.SlugField(blank=True, default="")),
                ("sub_title", models.CharField(blank=True, default="", max_length=50)),
                ("price", models.DecimalField(decimal_places=2, max_digits=100)),
                ("oldprice", models.DecimalField(decimal_places=2, max_digits=100)),
            ],
            options={
                "abstract": False,
                "base_manager_name": "prefetch_manager",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="BlogCategory",
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
                ("title", models.CharField(blank=True, default="", max_length=50)),
                (
                    "image",
                    cloudinary.models.CloudinaryField(
                        blank=True, default="", max_length=255, verbose_name="image"
                    ),
                ),
                ("slug", models.SlugField(blank=True, default="")),
            ],
            options={
                "verbose_name_plural": "Blog Categories",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="Post",
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
                ("title", models.CharField(blank=True, default="", max_length=50)),
                (
                    "image",
                    cloudinary.models.CloudinaryField(
                        blank=True, default="", max_length=255, verbose_name="image"
                    ),
                ),
                ("slug", models.SlugField(blank=True, default="")),
                (
                    "content",
                    ckeditor_uploader.fields.RichTextUploadingField(
                        default="", null=True, verbose_name="Description"
                    ),
                ),
                (
                    "category",
                    auto_prefetch.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="blog.blogcategory",
                        verbose_name="Blog Category",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Posts",
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
    ]
