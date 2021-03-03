from teammanager.models import Gameresult


class GameresultWrapper(object):
    def __init__(self, gameinfo):
        self.gameinfo = gameinfo

    def save_home_first_half(self, first_half, points_against):
        self._save(first_half, 0, points_against, True)

    def save_away_first_half(self, first_half, points_against):
        self._save(first_half, 0, points_against, False)

    def _save(self, first_half, second_half, points_against, is_home):
        gameresult = Gameresult.objects.get(gameinfo=self.gameinfo, isHome=is_home)
        if first_half is not None:
            gameresult.fh = first_half
        gameresult.sh = second_half
        gameresult.pa = points_against
        gameresult.save()

    def save_home_second_half(self, second_half, points_against):
        self._save(None, second_half, points_against, True)

    def save_away_second_half(self, second_half, points_against):
        self._save(None, second_half, points_against, False)
