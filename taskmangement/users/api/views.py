from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import generics, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from taskmangement.users import custom_exceptions
from taskmangement.users import models as v1_users_app
from taskmangement.users.permissions import IsOrganizationAdmin
from taskmangement.utilities.utils import make_distinct, send_otp_by_mail
from .serializers import (
    ChangePasswordSerializer, 
    OrganizationSerializer, 
    RegisterSerializer, 
    UserSerializer
)
from django.contrib.auth import update_session_auth_hash

User = get_user_model()

class UserRegister(generics.CreateAPIView):
    serializer_class = RegisterSerializer.UserSignup
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        send_otp_by_mail(email=serializer.data["email"])

        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "user": RegisterSerializer.UserSignup(user).data,
                "message": "Registeration Successful,",
            }
        )

class UserLogin(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
      
        return Response(
            {
                "token": token.key,
                "message": "Login Successfull ",
            }
        )

class UserLogout(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request.auth.delete()
        return Response(
            {"detail": "Logged out successfully."}, 
            status=status.HTTP_200_OK
        )
        
class UserChangePassword(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user:User = self.request.user
        serializer = self.serializer_class(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        if user.check_password(serializer.data.get("old_password")):
            user.set_password(serializer.data.get("new_password"))
            user.save()
            update_session_auth_hash(request, user)
            return Response(
                {'message': 'Password changed successfully.'}, 
                status=status.HTTP_200_OK
            )
        return Response(
            {'error': 'Incorrect old password.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
            
class UserViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = UserSerializer.BaseRetrieve
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]
    allowed_methods = ['GET', 'HEAD']
    
    def get_queryset(self):
        user = self.request.user
        return User.objects.exclude(id=user.id).order_by("-created_at")
    
    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserSerializer.Retrieve
        return UserSerializer.BaseRetrieve

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer.BaseRetrieve(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    
    @action(methods=["PUT"], detail=True, permission_classes=[IsAuthenticated])
    def update_me(self, request, *args, **kwargs):
        user:User = get_object_or_404(User, id=kwargs.get("pk"))
        
        if not user:
            raise custom_exceptions.Forbidden(
                "You do not have permission to perform this action"
            )
            
        serializer = UserSerializer.UpdateMe(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {
                "message": "Profile Updated Successfully",
                "data": UserSerializer.Retrieve(user).data,
            },
            status=status.HTTP_200_OK,
        )

class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer.BaseRetrieve
    permission_classes = [IsOrganizationAdmin]
    
    def get_queryset(self):
        user:User=self.request.user
        return make_distinct(
            v1_users_app.Organization.objects.filter(
                owner=user, active=True
            )
        )
    
    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrganizationSerializer.Retrieve
        if self.action in ["list", "update", "delete"]:
            return UserSerializer.BaseRetrieve
        return UserSerializer.BaseRetrieve
    
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data)
    
    @action(methods=["PUT"], detail=True, permission_classes=[IsOrganizationAdmin])
    def add_team(self, request, *args, **kwargs):
        user:User = self.request.user
        organization:v1_users_app.Organization = get_object_or_404(
            v1_users_app.Organization, id=kwargs.get("pk")
        )
        
        if user != organization.owner:
            raise custom_exceptions.Forbidden(
                "You do not have permission to perform this action"
            )
        
        serializer = OrganizationSerializer.AddTeam(
            instance=organization, data=request.data, context={"user":user}
        )
        serializer.is_valid(raise_exception=True)
        added_teams = serializer.validated_data.get("teams_ids")
        organization.teams.add(*added_teams)
        organization.save()
        return Response(
            {
                "meassage":"Added successfully"
            },
            status=status.HTTP_200_OK,
        )
                 
    @action(methods=["DELETE"], detail=True, permission_classes=[IsOrganizationAdmin])
    def delete_team(self, request, *args, **kwargs):
        user:User = self.request.user
        organization:v1_users_app.Organization = get_object_or_404(
            v1_users_app.Organization, id=kwargs.get("pk")
        )
        
        if user != organization.owner:
            raise custom_exceptions.Forbidden(
                "You do not have permission to perform this action"
            )
        
        serializer = OrganizationSerializer.AddTeam(
            instance=organization, data=request.data, context={"user":user}
        )
        serializer.is_valid(raise_exception=True)
        removed_teams = serializer.validated_data.get("teams_ids")
        organization.teams.remove(*removed_teams)
        organization.save()
        return Response(
            {
                "meassage":"Deleted successfully"
            },
            status=status.HTTP_200_OK,
        )