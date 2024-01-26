from django.contrib.auth.models import User
from knox.models import AuthToken
from rest_framework.fields import SerializerMethodField, IntegerField, TimeField
from rest_framework.serializers import ModelSerializer, Serializer

from gamedays.models import Gameinfo, Team, Gameday
from league_manager.utils.serializer_utils import ObfuscatorSerializer, ObfuscateField
# importing models
from passcheck.models import Playerlist
from passcheck.service.eligibility_validation import EligibilityValidator, ValidationError


class RosterSerializer(ObfuscatorSerializer):
    first_name = ObfuscateField(field_name='first_name')
    last_name = ObfuscateField(field_name='last_name')
    jersey_number = IntegerField()
    pass_number = IntegerField()
    sex = IntegerField()
    gamedays_counter = SerializerMethodField()

    def get_gamedays_counter(self, obj: dict):
        all_leagues = self.context.get('all_leagues', [])
        gamedays_counters = {}
        for league in all_leagues:
            field_name = f'{league["gamedays__league"]}'
            gamedays_counters[field_name] = obj[field_name]
        return gamedays_counters


class RosterValidationSerializer(RosterSerializer):
    validationError = SerializerMethodField(required=False, method_name='get_validation_error')

    def get_validation_error(self, player: dict):
        validator: EligibilityValidator = self.context.get('validator')
        if not validator:
            return 'Could not validate player due missing validator.'
        try:
            validator.validate(player)
        except ValidationError as exception:
            return str(exception)
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'validationError' in data and data['validationError'] is None:
            del data['validationError']
        ignore_fields = ['sex', 'gamedays_counter']
        for field in ignore_fields:
            del data[field]
        return data


class PasscheckSerializer(ModelSerializer):
    ownLeagueGamedaysPlayed = SerializerMethodField('get_own')
    otherTeamGamedaysPlayed = SerializerMethodField('get_other')

    def get_own(self, obj: Playerlist):
        return 0

    def get_other(self, obj: Playerlist):
        return 0

    class Meta:
        model = Playerlist
        fields = '__all__'


class PasscheckGamesListSerializer(Serializer):
    SCHEDULED_C = 'scheduled'
    FIELD_C = 'field'
    GAMEDAY_ID_C = 'gameday_id'
    AWAY_ID_C = 'away_id'
    AWAY_C = 'away'
    HOME_ID_C = 'home_id'
    HOME_C = 'home'

    ALL_FIELD_VALUES = [GAMEDAY_ID_C, FIELD_C, SCHEDULED_C, HOME_C, HOME_ID_C, AWAY_C, AWAY_ID_C]
    gameday_id = IntegerField()
    field = IntegerField()
    scheduled = TimeField()
    home = SerializerMethodField()
    away = SerializerMethodField()

    def get_home(self, obj: dict):
        return {
            'name': obj[self.HOME_C],
            'id': obj[self.HOME_ID_C],
        }

    def get_away(self, obj: dict):
        return {
            'name': obj[self.AWAY_C],
            'id': obj[self.AWAY_ID_C],
        }

    class Meta:
        model = Gameinfo
        fields = ('id',
                  'field',
                  'scheduled',
                  'officials',
                  'gameday_id',
                  'home',
                  'away')


class PasscheckTeamInfoSerializer(ModelSerializer):
    class Meta:
        model = Gameinfo


class PasscheckOfficialsAuthSerializer(ModelSerializer):
    class Meta:
        model = AuthToken
        fields = ('token_key', 'user_id')


class PasscheckGamedayTeamsSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name')


class PasscheckGamedaysListSerializer(ModelSerializer):
    class Meta:
        model = Gameday
        fields = ('id', 'league_id', 'season_id', 'date')


class PasscheckUsernamesSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class PasscheckServiceSerializer:
    class Meta:
        fields = '__all__'
