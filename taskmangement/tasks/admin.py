from django.contrib import admin

from taskmangement.tasks.models import (
    ActionPoint,
    Collaborate,
    FeedBack,
    Task, 
    Team
)

admin.site.register(Team)
admin.site.register(Collaborate)
admin.site.register(Task)
admin.site.register(ActionPoint)
admin.site.register(FeedBack)

