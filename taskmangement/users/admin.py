from django.contrib import admin 

from taskmangement.users.models import (
    User,
    Organization

)

admin.site.register(User)
admin.site.register(Organization)