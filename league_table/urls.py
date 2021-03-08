from django.urls import path

from league_table.views import LeagueTableView

urlpatterns = [
    path('', LeagueTableView.as_view(), name='league-table-overall'),
    path('<str:season>/<str:league>', LeagueTableView.as_view(), name='league-table-league'),
]
