from io import BytesIO

import auto_prefetch
from cloudinary import uploader
from cloudinary.models import CloudinaryField
from django.db import models
from django.db.models.query import QuerySet
from model_utils import FieldTracker

from acctmarket2.utils.media import MediaHelper


class VisibleManager(auto_prefetch.Manager):
    def get_queryset(self) -> QuerySet:
        """filters queryset to return only visible items"""
        return super().get_queryset().filter(visible=True)


class TimeBasedModel(auto_prefetch.Model):
    visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(auto_prefetch.Model.Meta):
        abstract = True

    objects = auto_prefetch.Manager()
    items = VisibleManager()


class TitleTimeBasedModel(TimeBasedModel):
    title = models.CharField(max_length=50, default="", blank=True)

    class Meta(auto_prefetch.Model.Meta):
        abstract = True
        ordering = ["title", "created_at"]

    def __str__(self):
        return self.title


class TitleandUIDTimeBasedModel(TimeBasedModel):
    title = models.CharField(max_length=50, default="", blank=True)

    tracker = FieldTracker()

    class Meta(auto_prefetch.Model.Meta):
        abstract = True
        ordering = ["title", "-created_at", "-updated_at"]

    def __str__(self):
        return str(self.id)


class UIDTimeBasedModel(TimeBasedModel):
    tracker = FieldTracker()

    class Meta(auto_prefetch.Model.Meta):
        abstract = True
        ordering = ["-created_at"]


class BaseModel(UIDTimeBasedModel):
    created_by = auto_prefetch.ForeignKey(
        "users.Account",
        on_delete=models.CASCADE,
        related_name="created_by",
    )

    class Meta(auto_prefetch.Model.Meta):
        abstract = True


class ImageTitleTimeBaseModels(TitleTimeBasedModel):
    # Using CloudinaryField for image upload
    image = CloudinaryField("image", default="", blank=True)

    class Meta(auto_prefetch.Model.Meta):
        abstract = True

    def save(self, *args, **kwargs):
        if self.image and not str(self.image).startswith("http"):
            if hasattr(self.image, "file"):
                # Ensure the file object has a name attribute
                if isinstance(self.image.file, BytesIO) and not hasattr(
                    self.image.file, "name"
                ):
                    self.image.file.name = "temporary_image_name.jpg"
                upload_path = MediaHelper.get_image_upload_path(
                    self, self.image.file.name
                )
                upload_result = uploader.upload(
                    self.image.file, folder=upload_path)
                self.image = upload_result["public_id"]
        super(ImageTitleTimeBaseModels, self).save(*args, **kwargs)
