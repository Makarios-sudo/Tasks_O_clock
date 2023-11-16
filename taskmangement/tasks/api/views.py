
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, status, viewsets
from taskmangement.tasks.api.serializers import TeamSerializer
from taskmangement.users import custom_exceptions
from taskmangement.tasks import models as v1_tasksApp
from taskmangement.users import models as v1_usersApp
from taskmangement.users.api.serializers import UserSerializer
from taskmangement.users.permissions import IsOrganizationAdmin
from taskmangement.utilities.utils import make_distinct, new_account_password_prompt
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class =  TeamSerializer.BaseRetrieve
    permission_classes = [IsOrganizationAdmin]
    
    def get_queryset(self):
        user:v1_usersApp.User=self.request.user
        return make_distinct(
            v1_tasksApp.Team.objects.filter(
                owner=user, active=True
            )
        )
        
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=["POST"], permission_classes=[IsOrganizationAdmin])
    def add_team_lead(self, request, *args, **kwargs):
        user:v1_usersApp.User = self.request.user
        team:v1_tasksApp.Team = get_object_or_404(v1_tasksApp.Team, id=kwargs.get("pk"))
        
        if user != team.owner:
            raise custom_exceptions.Forbidden(
                "You do not have the permission to perform this action"
            )
        
        serializer = TeamSerializer.TeamNewLead(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data.get("name")
        email = serializer.validated_data.get("email")
        
        if team.lead:
            raise custom_exceptions.Forbidden(
                "This team has a lead already, to change the lead,use update team"
            )
        
        new_user =v1_usersApp.User.objects.create(
            username=email,
            email=email,
            name=name,
            is_organization_admin=False,
            is_organization_staff=True,
            metadata=None
        )

        password = make_password(f"{name}{email}")
        user.set_password(password)
        user.save()
        
        team.lead = new_user
        team.save()
        new_account_password_prompt(email=email, name=name, password=user.password)
        return Response(
            {"message":f"{team.lead} is added successfuly",},
            status=status.HTTP_201_CREATED
        )
     
    @action(detail=True, methods=["POST"], permission_classes=[IsOrganizationAdmin])
    def add_team_lead_by_existing(self, request, *args, **kwargs):
        user:v1_usersApp.User = self.request.user
        team:v1_tasksApp.Team = get_object_or_404(v1_tasksApp.Team, id=kwargs.get("pk"))
        
        if user != team.owner:
            raise custom_exceptions.Forbidden(
                "You do not have the permission to perform this action"
            )
        
        serializer = TeamSerializer.AddLeadByExisting(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_lead = serializer.validated_data.get("lead")
        team.lead = new_lead
        team.save()
        return Response(
            {"message":f"{team.lead} is added successfuly",},
            status=status.HTTP_201_CREATED
        )
            
    @action(detail=True, methods=["POST"], permission_classes=[IsOrganizationAdmin])
    def add_team_members(self, request, *args, **kwargs):
        user:v1_usersApp.User = self.request.user
        team:v1_tasksApp.Team = get_object_or_404(
            v1_tasksApp.Team, id=kwargs.get("pk")
        )
        
        if user != team.owner:
            raise custom_exceptions.Forbidden(
                "You do not have permission to take this action"
            )
        
        serializer = TeamSerializer.NewMembers(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data_list = serializer.validated_data['members']

        created_users = []
        for user_data in user_data_list:
            users = v1_usersApp.User.objects.create(
                username=user_data['email'],  
                name=user_data['name'],
                email=user_data['email'],
                is_organization_admin=False,  
                is_organization_staff=True,
                password=make_password(user_data['name'],user_data['email']),
                metadata=None
            )
            created_users.append(users)
            
        team.members.add(*created_users)
        team.save()
        for user in created_users:
            new_account_password_prompt(
                email=user_data["email"], 
                name=user_data["name"],
                password=user.password
            )

        return Response({
            'message': 'members added successfully'}, 
            status=status.HTTP_201_CREATED
        )

      
    @action(detail=True, methods=["POST"], permission_classes=[IsOrganizationAdmin])
    def add_team_members_by_existing(self, request, *args, **kwargs):
        user:v1_usersApp.User = self.request.user
        team:v1_tasksApp.Team = get_object_or_404(v1_tasksApp.Team, id=kwargs.get("pk"))
        
        if user != team.owner:
            raise custom_exceptions.Forbidden(
                "You do not have the permission to perform this action"
            )
        
        serializer = TeamSerializer.AddMembersByExisiting(
            data=request.data, context={"team":team}
        )
        serializer.is_valid(raise_exception=True)
        existing_members = serializer.validated_data.get("existing_ids")
        
        organization = team.organization_teams.first()
        print(f"======organization====={organization.all_staffs_ids}")
        print(type(organization))
      
        team.members.add(*existing_members)
        # team.save()
        return Response(
            {"message":"members are added successfuly",},
            status=status.HTTP_201_CREATED
        )
       