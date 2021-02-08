import json

from django.db.models import QuerySet

from gamedays.models import Gameinfo, Gameresult, TeamLog


class GameLogService(object):
    @staticmethod
    def get_gamelog(gameId):
        return GameLog(gameId)


class GameLog(object):
    home_firsthalf_entries: QuerySet[TeamLog] = None
    away_firsthalf_entries: QuerySet[TeamLog] = None
    home_secondhalf_entries: QuerySet[TeamLog] = None
    away_secondhalf_entries: QuerySet[TeamLog] = None

    def __init__(self, gameId):
        self.gameinfo = Gameinfo.objects.get(id=gameId)
        home = Gameresult.objects.get(gameinfo=self.gameinfo, isHome=True).team
        away = Gameresult.objects.get(gameinfo=self.gameinfo, isHome=False).team
        self.gamelog = GameLogObject(gameId, home, away)

    def as_json(self):
        self.gamelog.is_first_half = self.is_firsthalf()
        self.gamelog.home.score = self.get_home_score()
        self.gamelog.away.score = self.get_away_score()
        self.gamelog.home.firsthalf.score = self._calc_score(self.get_entries_home_firsthalf())
        self.gamelog.home.firsthalf.entries = self.create_entries_for_half(self.get_entries_home_firsthalf())
        self.gamelog.away.firsthalf.score = self._calc_score(self.get_entries_away_firsthalf())
        self.gamelog.away.firsthalf.entries = self.create_entries_for_half(self.get_entries_away_firsthalf())
        self.gamelog.home.secondhalf.score = self._calc_score(self.get_entries_home_secondhalf())
        self.gamelog.home.secondhalf.entries = self.create_entries_for_half(self.get_entries_home_secondhalf())
        self.gamelog.away.secondhalf.score = self._calc_score(self.get_entries_away_secondhalf())
        self.gamelog.away.secondhalf.entries = self.create_entries_for_half(self.get_entries_away_secondhalf())
        return json.dumps(self.gamelog, cls=(GameLogEncoder))

    def get_home_team(self):
        return self.gamelog.home.name

    def get_away_team(self):
        return self.gamelog.away.name

    def get_entries_home_firsthalf(self):
        if self.home_firsthalf_entries:
            return self.home_firsthalf_entries
        self.home_firsthalf_entries = self._get_entries_for_team_and_half(team=self.gamelog.home.name, half=1)
        return self.home_firsthalf_entries

    def get_entries_away_firsthalf(self):
        if self.away_firsthalf_entries:
            return self.away_firsthalf_entries
        self.away_firsthalf_entries = self._get_entries_for_team_and_half(team=self.gamelog.away.name, half=1)
        return self.away_firsthalf_entries

    def get_entries_home_secondhalf(self):
        if self.home_secondhalf_entries:
            return self.home_secondhalf_entries
        self.home_secondhalf_entries = self._get_entries_for_team_and_half(team=self.gamelog.home.name, half=2)
        return self.home_secondhalf_entries

    def get_entries_away_secondhalf(self):
        if self.away_secondhalf_entries:
            return self.away_secondhalf_entries
        self.away_secondhalf_entries = self._get_entries_for_team_and_half(team=self.gamelog.away.name, half=2)
        return self.away_secondhalf_entries

    def _get_entries_for_team_and_half(self, team, half):
        return TeamLog.objects.filter(gameinfo=self.gameinfo, team=team, half=half).order_by('-sequence')

    def get_home_score(self):
        return self._calc_score(list(self.get_entries_home_firsthalf()) + list(self.get_entries_home_secondhalf()))

    def get_away_score(self):
        return self._calc_score(list(self.get_entries_away_firsthalf()) + list(self.get_entries_away_secondhalf()))

    def _calc_score(self, half_entries):
        sum = 0
        entry: TeamLog
        for entry in half_entries:
            sum = sum + entry.value
        return sum

    def create_entries_for_half(self, half_entries):
        result = dict()
        entry: TeamLog
        for entry in half_entries:
            if result.get(entry.sequence) is None:
                result[entry.sequence] = {
                    'sequence': entry.sequence
                }
            if entry.cop:
                result[entry.sequence].update({'cop': entry.cop})
            else:
                result[entry.sequence].update({entry.event: entry.player})
        return list(result.values())

    def is_firsthalf(self):
        return self.gameinfo.gameHalftime is None


class Half(object):
    def __init__(self):
        self.score = None
        self.entries = []

    def as_json(self):
        return dict(score=self.score, entries=self.entries)


class Team(object):
    def __init__(self, name):
        self.name = name
        self.score = None
        self.firsthalf = Half()
        self.secondhalf = Half()

    def as_json(self):
        return dict(name=self.name, score=self.score, firsthalf=self.firsthalf, secondhalf=self.secondhalf)


class GameLogObject(object):
    def __init__(self, gameId, home, away):
        self.gameId = gameId
        self.home = Team(home)
        self.away = Team(away)
        self.is_first_half = True

    def as_json(self):
        return dict(gameId=self.gameId, isFirstHalf=self.is_first_half, home=self.home, away=self.away)


class GameLogEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'as_json'):
            return obj.as_json()
        return json.JSONEncoder.default(self, obj)
