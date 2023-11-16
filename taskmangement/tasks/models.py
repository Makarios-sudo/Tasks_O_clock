from django.db import models
from django.utils.translation import gettext_lazy as _
from taskmangement.utilities.utils import BaseModelMixin, Status, Urgency_Level


# Create your models here.

class Team(BaseModelMixin):
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    name = models.CharField(
        _("Name"), 
        blank=False, 
        max_length=255, 
        db_index=True
    )
    description = models.TextField(
        _("Description"),
        unique=True,
        max_length=500,
        db_index=True,
    )
    lead = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        null=True, blank=True,
        unique=True, db_index=True,  
        related_name="team_lead"
    )
    members = models.ManyToManyField(
        "users.User",
        blank=True, db_index=True,  
        related_name="team_members"
    )

    def __str__(self) -> str:
        return self.name


class Collaborate(BaseModelMixin):
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True, blank=True,
        db_index=True,
    )
    title = models.CharField(
        _("title"), 
        blank=False, 
        max_length=255, 
        db_index=True
    )
    description = models.TextField(
        _("Description"),
        unique=True,
        max_length=500,
        db_index=True,
    )
    assigned_by = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True, blank=True,
        db_index=True,
        related_name="collabo_created_by"
    )
    assigned_to = models.ManyToManyField(
        "Team",
        blank=True, 
        db_index=True,  
        related_name="collabo_created_for"
    )
    urgency_level = models.CharField(
        _("urgency_level"),
        choices=Urgency_Level.choices,
        default=Urgency_Level.HIGH,
        max_length=50,
        db_index=True,
    )
    deadline = models.DateTimeField(
        auto_now=False, 
        auto_now_add=False, 
        db_index=True
    )
    
    def __str__(self) -> str:
        return self.title


class Task(BaseModelMixin):
    title = models.CharField(
        _("title"), 
        blank=False, 
        max_length=255, 
        db_index=True
    )
    description = models.TextField(
        _("Description"),
        unique=True,
        max_length=500,
        db_index=True,
    )
    source = models.ForeignKey(
        "Collaborate",
        on_delete=models.CASCADE,
        null=True, blank=True,
        db_index=True,
    )
    assigned_by = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True, blank=True,
        db_index=True,
        related_name="task_created_by"
    )
    assigned_to = models.ManyToManyField(
        "users.User",
        blank=True, 
        db_index=True, 
        related_name="task_created_to" 
    )
    urgency_level = models.CharField(
        _("urgency_level"),
        choices=Urgency_Level.choices,
        default=Urgency_Level.HIGH,
        max_length=50,
        db_index=True,
    )
    deadline = models.DateTimeField(
        auto_now=False, 
        auto_now_add=False, 
        db_index=True
    )

    def __str__(self) -> str:
        return self.title


class ActionPoint(BaseModelMixin):
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True, blank=True,
        db_index=True,
    )
    task = models.ForeignKey(
        "Task",
        on_delete=models.CASCADE,
        null=True, blank=True,
        db_index=True,
    )
    blocker = models.TextField(
        _("Blocker"),
        unique=True,
        max_length=500,
        db_index=True,
    )
    status = models.CharField(
        _("Status"),
        choices=Status.choices,
        default=Status.PENDING,
        max_length=50,
        db_index=True,
    )
    reviewed = models.BooleanField(
        _("Reviewed"),
        default=False,
        db_index=True,
    )

    def __str__(self) -> str:
        return self.task.title
    

class FeedBack(BaseModelMixin):
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True, blank=True,
        db_index=True,
    )
    action_point = models.ForeignKey(
        "ActionPoint",
        on_delete=models.CASCADE,
        null=True, blank=True,
        db_index=True,
    )
    suggestion = models.TextField(
        _("Suggestion"),
        unique=True,
        max_length=500,
        db_index=True,
    )
    approved = models.BooleanField(
        _("Approved"),
        default=False,
        db_index=True,
    )
    
    def __str__(self) -> str:
        return self.action_point.status
