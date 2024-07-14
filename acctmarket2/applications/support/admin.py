from django.contrib import admin
from acctmarket2.applications.support.models import ContactUs



@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject")
