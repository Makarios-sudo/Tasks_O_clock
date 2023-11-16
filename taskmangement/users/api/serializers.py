from django.contrib.auth import get_user_model
from rest_framework import serializers
from taskmangement.tasks.api import serializers as v1_tasksApp_serializer
from taskmangement.users.models import User, Organization
from taskmangement.tasks import models as v1_tasksModel
from taskmangement.tasks import models as tasks_model
from taskmangement.utilities.utils import make_distinct
from django.db.models import Q

User = get_user_model()

class RegisterSerializer:
    class UserSignup(serializers.ModelSerializer):
        password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
        password2 = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
        is_organization_admin = serializers.BooleanField(required=True)
        metadata = serializers.JSONField(required=True)
        
        class Meta:
            model = User
            fields = [
                "name", 
                "email", 
                "is_organization_admin",  
                "metadata", 
                "password", 
                "password2"
            ]

        def validate(self, attrs):
            if attrs["password2"] != attrs["password"]:
                raise serializers.ValidationError("Passwords do not match")
            return attrs

        def create(self, validated_data):
            email = validated_data.pop("email")
            name = validated_data.pop("name")
            is_organization_admin = validated_data.pop("is_organization_admin")
            metadata = validated_data.pop("metadata")
            password = validated_data.pop("password")
            
            user = User.objects.create_user(
                username=email,
                name=name,
                email=email,
                is_organization_admin=is_organization_admin,
                password=password,
                metadata=metadata
            )
            user.save()
            return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
   
class UserSerializer:
    class BaseRetrieve(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = [ 
                      "name", 
                      "email", 
                      "is_organization_admin", 
                      "is_organization_staff",
                      "metadata", 
                      "id", 
                      "created_at" 
                    ]
          
    class Retrieve(BaseRetrieve):
        organization = serializers.SerializerMethodField()
        team = serializers.SerializerMethodField()
        team_position = serializers.SerializerMethodField()
        
        def get_organization(self, obj:User):
            pass
        
        def get_team(self, obj:User):
            pass
        
        def get_team_position(self, obj:User):
            pass
        
        class Meta:
            model = User
            fields = [ 
                      "id",
                      "name", 
                      "email", 
                      "metadata", 
                      "is_organization_admin",
                      "organization",
                      "team",
                      "team_position"
                    ]
    
    class RetrievePublic(serializers.ModelSerializer):
        avatar = serializers.SerializerMethodField()
        
        def get_avatar(self, obj: User):
            metadata = obj.metadata
            if metadata is None or not metadata.get("avatar"):
                return None
            return metadata.get("avatar")
            
        class Meta:
            model = User
            fields = [ 
                "name", 
                "email", 
                "avatar", 
                "id"
            ]
    
    class UpdateMe(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = [ "metadata"]
      
class OrganizationSerializer:
    class BaseRetrieve(serializers.ModelSerializer):
        class Meta:
            model = Organization
            fields = [ 
                      "name", 
                      "email", 
                      "location", 
                      "country", 
                      "postal_code",
                      "description",
                      "metadata",
                      "id", 
                      "created_at",
                      "teams"
                    ]
    
    class Retrieve(BaseRetrieve):
        teams = serializers.SerializerMethodField()
        staffs = serializers.SerializerMethodField()
    
        def get_teams(self, obj:Organization):
            return v1_tasksApp_serializer.TeamSerializer.PublicRetrieve(
               obj.teams.all(), many=True
            ).data[:5]
            
        def get_staffs(self, obj:Organization):
            all_staffs = make_distinct(
                User.object.filter(
                    Q(team_lead__id__in=obj.teams.all()) |
                    Q(team_members__id__in=obj.teams.all())
                )
            )
            
            return UserSerializer.RetrievePublic(
               all_staffs, many=True
            ).data[:5]
            
        class Meta:
            model = Organization
            fields = [ 
                      "name", 
                      "email", 
                      "location", 
                      "country", 
                      "postal_code",
                      "description",
                      "metadata",
                      "id", 
                      "created_at",
                      "teams_count",
                      "teams",
                      "staffs_count",
                      "staffs"
                    ]
    
    class AddTeam(serializers.Serializer):
        teams_ids = serializers.ListField(
            child=serializers.PrimaryKeyRelatedField(
                queryset = v1_tasksModel.Team.objects.all(),
            )
        )
                        
        def validate_teams_ids(self, teams_ids):
            user=self.context.get("user")
            
            if not all(
                team.owner == user for team in teams_ids
            ):
                raise serializers.ValidationError(
                    "You are not the owner of the team(s)."
                )
            return teams_ids
   