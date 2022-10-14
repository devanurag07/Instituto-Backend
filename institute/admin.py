from django.contrib import admin

# Register your models here.
from institute.models import Institute, OwnerProfile, TeacherProfile, TeacherRequest, Subject, SubjectAccess

admin.site.register([Institute, OwnerProfile, TeacherProfile,
                    TeacherRequest, Subject, SubjectAccess])
