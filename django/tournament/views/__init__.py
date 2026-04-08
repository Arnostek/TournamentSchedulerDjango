# Views module
from .base import TournamentListView, TournamentDetail
from .tournament import TournamentDetailView, TVView, PrintsView
from .division import (
    DivisionSystemView,
    DivisionRankingView,
    DivisionCrossTablesView,
    DivisionTablesView,
)
from .schedule import ScheduleView
from .protocols import ProtocolsView
from .match import SetScore, DelScore, SwitchMatch, FinishGroup, ReopenGroup, AddTiePoints
from .conflicts import ConflictsView

__all__ = [
    # Base
    'TournamentListView',
    'TournamentDetail',
    # Tournament
    'TournamentDetailView',
    'TVView',
    'PrintsView',
    # Division
    'DivisionSystemView',
    'DivisionRankingView',
    'DivisionCrossTablesView',
    'DivisionTablesView',
    # Schedule
    'ScheduleView',
    'ProtocolsView',
    # Match operations
    'SetScore',
    'DelScore',
    'SwitchMatch',
    'FinishGroup',
    'ReopenGroup',
    'AddTiePoints',
    # Conflicts
    'ConflictsView',
]
