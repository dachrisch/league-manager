from http import HTTPStatus

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from league_manager.utils.decorators import get_user_request_permission
from league_manager.utils.view_utils import UserRequestPermission
from passcheck.service.passcheck_service import PasscheckService, PasscheckServicePlayers, PasscheckException


class PasscheckGamesAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @get_user_request_permission
    def get(self, request, *args, **kwargs):
        user_permission = kwargs.get('user_permission')
        gameday_id = kwargs.get('gameday')
        team_id = request.user.username
        passcheck = PasscheckService(user_permission=user_permission)
        try:
            return Response(passcheck.get_passcheck_games(team_id=team_id, gameday_id=gameday_id), status=HTTPStatus.OK)
        except PasscheckException as exception:
            raise PermissionDenied(detail=str(exception))


class PasscheckGamesStatusAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @get_user_request_permission
    def get(self, request, *args, **kwargs):
        user_permission = kwargs.get('user_permission')
        passcheck = PasscheckService(user_permission=user_permission)
        return Response(passcheck.get_passcheck_status(officials_team=request.user.username), status=HTTPStatus.OK)



class PasscheckRosterAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @get_user_request_permission
    def get(self, request, **kwargs):
        team = kwargs.get('pk')
        gameday_id = kwargs.get('gameday')
        user_permission: UserRequestPermission = kwargs.get('user_permission')
        user_permission.is_user = True
        if team:
            passcheck = PasscheckService(user_permission)
            try:
                return Response(passcheck.get_roster_with_validation(team, gameday_id), status=HTTPStatus.OK)
            except PasscheckException as exception:
                raise PermissionDenied(detail=str(exception))

    def put(self, request, **kwargs):
        data = request.data
        team_id = kwargs.get('pk')
        gameday_id = kwargs.get('gameday')
        passcheckservice = PasscheckServicePlayers()
        passcheckservice.create_roster_and_passcheck_verification(team_id, gameday_id, request.user, data)
        return Response(status=HTTPStatus.OK)
