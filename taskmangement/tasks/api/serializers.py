from rest_framework import serializers
from taskmangement.tasks import models as v1_tasksApp
from taskmangement.users import models as v1_usersApp

      
class TeamSerializer:
    class BaseRetrieve(serializers.ModelSerializer):
        class Meta:
            model = v1_tasksApp.Team
            fields = [ 
                      "name", 
                      "description", 
                      "lead", 
                      "members",
                      "id",
                      "created_at"
                    ]
            
    class PublicRetrieve(serializers.ModelSerializer):
        class Meta:
            model = v1_tasksApp.Team
            fields = [ 
                      "name", 
                      "description", 
                      "id"
                    ]
    
    class TeamNewLead(serializers.Serializer):
        name = serializers.CharField(required=True)
        email = serializers.EmailField(required=True)
                
        def validate_email(self, email):
            
            if v1_usersApp.User.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    "This email already exist, Use another email"
                )
            return email
        
    class NewMembers(serializers.Serializer):
        members = serializers.ListField(
            child=serializers.DictField(
                child=serializers.CharField(write_only=True, required=True),
                allow_empty=False
            )
        )

        def validate_members(self, value):
            email_set = set()
            for user_data in value:
                email = user_data.get('email')
                if email in email_set:
                    raise serializers.ValidationError("Duplicate email addresses are not allowed.")
                email_set.add(email)

            existing_emails = v1_usersApp.User.objects.filter(email__in=[user_data['email'] for user_data in value])
            existing_email_set = set(existing_emails.values_list('email', flat=True))

            duplicate_emails = [user_data['email'] for user_data in value if user_data['email'] in existing_email_set]

            if duplicate_emails:
                raise serializers.ValidationError(f"The following email addresses already exist: {', '.join(duplicate_emails)}")

            return value
                
    class AddLeadByExisting(BaseRetrieve):
        class Meta:
            model = v1_tasksApp.Team
            fields = [ "lead"]  
        
    class AddMembersByExisiting(serializers.Serializer): 
        existing_ids = serializers.ListField(
            child=serializers.PrimaryKeyRelatedField(
                queryset = v1_usersApp.User.objects.all()
            )
        ) 
        
                        
        def validate_existing_ids(self, existing_ids):
            team=self.context.get("team")
            organization = team.organization_teams.first()
            organization_exisiting_users = organization.all_staffs_ids
            
            for user_id in existing_ids:
                if user_id not in organization_exisiting_users:
                    raise serializers.ValidationError(
                        "one or many users are'nt in the orgainzarion"
                    )
                    
            return existing_ids
           
            
            
            
            
        