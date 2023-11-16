from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .manager import UserManager
from taskmangement.utilities.utils import BaseModelMixin, generate_id, make_distinct
from taskmangement.tasks import models as tasks_model
from django.db.models import F,Count


class User(AbstractUser):
    object = UserManager()

    id = models.CharField(
        primary_key=True,
        default=generate_id,
        editable=True,
        max_length=255,
    )
    name = models.CharField(
        _("Name"), 
        blank=False, 
        max_length=255, 
        db_index=True
    )
    email = models.CharField(
        _("Email"),
        unique=True,
        max_length=225,
        db_index=True,
    )
    metadata = models.JSONField(
        _("metaadata"), 
        default=dict, 
        blank=True, 
        null=True
    )
    is_organization_admin = models.BooleanField( _("is_admin"), default=False,)
    is_organization_staff = models.BooleanField( _("is_staff"), default=False,)
    is_active = models.BooleanField(_("is_active"), default=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    
    REQUIRED_FIELDS = ["is_organization_admin", "metadata"]
    
    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def __str__(self) -> str:
        return self.email
    
    
class Organization(BaseModelMixin):
    owner = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organization_admin",
    )
    name = models.CharField(
        _("Name"), 
        blank=False, 
        max_length=255, 
        db_index=True
    )
    email = models.CharField(
        _("Email"),
        unique=True,
        max_length=225,
        db_index=True,
    )
    location = models.CharField(
        _("Location"),
        unique=True,
        max_length=225,
        db_index=True,
    )
    country = models.CharField(
        _("Country"),
        unique=True,
        max_length=225,
        db_index=True,
    )
    postal_code = models.CharField(
        _("Postal_Code"),
        unique=True,
        max_length=225,
        db_index=True,
    )
    description = models.TextField(
        _("Description"),
        unique=True,
        max_length=500,
        db_index=True,
    )
    metadata = models.JSONField(
        _("metaadata"), 
        default=dict, 
        blank=True, 
        null=True
    )
    teams = models.ManyToManyField(
        "tasks.Team",
        blank=True, db_index=True,  
        related_name="organization_teams"
    )
   
    def __str__(self) -> str:
        return self.name
    
    def teams_count(self) -> int:
        return self.teams.all().count()
    
    def staffs_count(self) -> int:
        total_count = self.teams.aggregate(
            total_count=Count(F("members"), distinct=True) + 
            Count(F("lead"), distinct=True)
        )
        return total_count['total_count'] or 0.0

    # @property
    # def all_staffs(self, user:User, *args, **kwargs):
    #     self.teams.values_list("members", flat=True)
        
    @property
    def all_staffs_ids(self, *args, **kwargs):
        from itertools import chain
        
        user_ids = set()
        
        for team in self.teams.all():
            members = team.members.values_list('id', flat=True)
            lead_id = team.lead_id

            if lead_id:
                members = chain(members, [lead_id])

            user_ids.update(members)


        return list(user_ids)