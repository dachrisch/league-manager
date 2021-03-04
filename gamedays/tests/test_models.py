from django.test import TestCase

from gamedays.tests.setup_factories.db_setup import DBSetup
from teammanager.models import Gameinfo, GameOfficial, TeamLog, Gameresult


class TestGameOfficials(TestCase):

    def test_officials_are_created(self):
        DBSetup().g62_status_empty()

        assert len(GameOfficial.objects.all()) == 0
        official = GameOfficial(gameinfo=Gameinfo.objects.all().first(), name='Horst', position='Scorecard')
        official.save()
        assert len(GameOfficial.objects.all()) == 1


class TestTeamlog(TestCase):
    def test_save_score(self):
        DBSetup().g62_status_empty()
        gameinfo = Gameinfo.objects.first()
        team = Gameresult.objects.filter(gameinfo=gameinfo).first().team
        teamlog = TeamLog(gameinfo=gameinfo, team=team,
                          sequence=1, event="td", player=19, value=6, half=1)
        teamlog.save()
        assert len(TeamLog.objects.all()) == 1
        assert str(teamlog) == '1__A1#1 Player: 19 Value: 6 - Half: 1'

    def test_save_PAT_no_good(self):
        DBSetup().g62_status_empty()
        gameinfo = Gameinfo.objects.first()
        team = Gameresult.objects.filter(gameinfo=gameinfo).first().team
        teamlog: TeamLog = TeamLog(gameinfo=gameinfo, team=team, sequence=1,
                                   event='pat1', value=0, half=1)
        teamlog.save()
        assert len(TeamLog.objects.all()) == 1

    def test_save_with_change_of_possession(self):
        DBSetup().g62_status_empty()
        gameinfo = Gameinfo.objects.first()
        team = Gameresult.objects.filter(gameinfo=gameinfo).first().team
        teamlog = TeamLog(gameinfo=gameinfo, team=team, sequence=1, cop=True, half=2)
        teamlog.save()
        assert len(TeamLog.objects.all()) == 1
        assert str(teamlog) == '1__A1#1 CoP: True - Half: 2'

    def test_score_is_marked_as_deleted(self):
        DBSetup().g62_status_empty()
        gameinfo = Gameinfo.objects.first()
        team = Gameresult.objects.filter(gameinfo=gameinfo).first().team
        teamlog = TeamLog(gameinfo=gameinfo, team=team,
                          sequence=1, event="td", player=19, value=6, half=1, isDeleted=True)
        teamlog.save()
        assert str(teamlog) == '1__A1#1 Player: 19 Value: 6 - Half: 1 [DELETED]'
        teamlog = TeamLog(gameinfo=gameinfo, team=team, sequence=2, cop=True,
                          half=2, isDeleted=True)
        teamlog.save()
        assert str(teamlog) == '1__A1#2 CoP: True - Half: 2 [DELETED]'
