"""
Modular builders for tournament group generation.
Breaks down repeated logic into small, controllable components.
"""


class PhaseManager:
    """Manages phase iteration and group creation orchestration."""
    
    def __init__(self, division):
        self.division = division
        self.phase = 1
        self.group_ranks_cache = {}
    
    def next_phase(self):
        """Increment to next phase."""
        self.phase += 1
        return self.phase
    
    def create_groups(self, group_names, teams, referee_groups=None):
        """Create groups in current phase and cache their ranks."""
        self.division.CreateGroups(group_names, teams, self.phase, referee_groups)
        # Cache ranks for easy access in next steps
        all_groups = ''.join(group_names) if isinstance(group_names, list) else group_names
        self.group_ranks_cache[all_groups] = self.division.GetGroupsRanks(group_names)
        return self.group_ranks_cache[all_groups]
    
    def get_ranks(self, group_names):
        """Get current ranks from group (or fetch if not cached)."""
        groups_key = ''.join(group_names) if isinstance(group_names, list) else group_names
        if groups_key not in self.group_ranks_cache:
            self.group_ranks_cache[groups_key] = self.division.GetGroupsRanks(group_names)
        return self.group_ranks_cache[groups_key]
    
    def create_and_rank(self, group_name, teams, place):
        """Create a group and immediately assign its ranking placement."""
        self.division.CreateGroups([group_name], teams, self.phase)
        self.division.CreateRanks(place, self.division.GetGroupsRanks([group_name]))


class PlacementBuilder:
    """Handles placement match generation (5th, 7th, 9th, 11th, etc.)"""
    
    def __init__(self, phase_manager):
        self.pm = phase_manager
    
    def create_placement(self, place, teams):
        """
        Create a single placement match.
        
        Args:
            place (int): Place number (5, 7, 9, 11, etc.)
            teams (list): List of 2 teams for this placement match
        """
        group_name = f'{place}th'
        self.pm.division.CreateGroups([group_name], teams, self.pm.phase)
        self.pm.division.CreateRanks(place, self.pm.division.GetGroupsRanks([group_name]))
    
    def create_placements_from_ranges(self, placements_dict):
        """
        Create multiple placements in one phase.
        
        Args:
            placements_dict (dict): {place: teams_list} mapping
            
        Example:
            builder.create_placements_from_ranges({
                5: ranks[4:6],
                7: ranks[6:8],
                9: ranks[8:10]
            })
        """
        for place, teams in sorted(placements_dict.items(), reverse=True):
            self.create_placement(place, teams)
    
    def create_placement_bracket(self, source_group_names, start_place=5, skip_places=None):
        """
        Generate placement matches from remaining teams after winners.
        Automatically creates 5th, 7th, 9th, etc., from ranked teams.
        
        Args:
            source_group_names (list): Groups to draw teams from
            start_place (int): Start place number (default 5)
            skip_places (list): Places to skip (e.g., [6] to only do odd placements)
        """
        skip_places = skip_places or []
        ranks = self.pm.get_ranks(source_group_names)
        
        place = start_place
        team_idx = start_place - 1  # -1 because placement starts after winners
        
        while team_idx + 1 < len(ranks):
            if place not in skip_places:
                teams = ranks[team_idx:team_idx + 2]
                if len(teams) == 2:
                    self.create_placement(place, teams)
                team_idx += 2
            place += 2


class SemiFinalBuilder:
    """Handles semi-final and final match orchestration."""
    
    def __init__(self, phase_manager):
        self.pm = phase_manager
    
    def create_semifinals(self, top4_teams, semi_group_names=None):
        """
        Create two semi-final groups from top 4 teams.
        
        Args:
            top4_teams (list): First 4 ranked teams
            semi_group_names (tuple): Names for the two semi groups (default: 'SemiA', 'SemiB')
        """
        if semi_group_names is None:
            semi_group_names = ('SemiA', 'SemiB')
        
        self.pm.create_groups(
            list(semi_group_names),
            [top4_teams[0], top4_teams[1], top4_teams[2], top4_teams[3]],
            self.pm.phase
        )
    
    def create_third_place(self, semi_group_names=None):
        """Create 3rd place match from semi-final losers."""
        if semi_group_names is None:
            semi_group_names = ['SemiA', 'SemiB']
        
        semi_ranks = self.pm.get_ranks(semi_group_names)
        self.pm.next_phase()
        self.pm.create_and_rank('3rd', semi_ranks[2:4], 3)
        return semi_ranks
    
    def create_final(self, semi_group_names=None):
        """Create final match from semi-final winners."""
        if semi_group_names is None:
            semi_group_names = ['SemiA', 'SemiB']
        
        semi_ranks = self.pm.get_ranks(semi_group_names)
        self.pm.next_phase()
        self.pm.create_and_rank('final', semi_ranks[0:2], 1)


class LastThreeBuilder:
    """Handles last-3 place match generation for odd-numbered tournaments."""
    
    def __init__(self, phase_manager):
        self.pm = phase_manager
    
    def create_last3_group(self, source_groups, group_name='Last3'):
        """
        Create last-3 group from final 3 teams.
        
        Args:
            source_groups (list): Groups to pull teams from
            group_name (str): Name for the last3 group
        """
        ranks = self.pm.get_ranks(source_groups)
        last_3_teams = ranks[-3:]
        
        self.pm.division.CreateGroups([group_name], last_3_teams, self.pm.phase, [group_name])
        self.pm.division.CreateRanks(len(ranks) - 2, self.pm.division.GetGroupsRanks([group_name]))


class RefereeBuilder:
    """Handles referee assignment to final matches."""
    
    def __init__(self, phase_manager, division):
        self.pm = phase_manager
        self.division = division
    
    def assign_group_referees(self, group_name, referee_teams):
        """
        Assign referees from teams to a specific group's matches.
        
        Args:
            group_name (str): Target group name
            referee_teams (list): List of team objects to use as referees
        """
        group = self.division.GetGroup(group_name)
        referees_stack = referee_teams.copy()
        referees_stack.reverse()  # Reverse for pop() to maintain order
        
        for match in group.match_set.all():
            if referees_stack:
                match.referee = referees_stack.pop()
                match.save()
    
    def assign_multiple_referees(self, referee_map):
        """
        Assign referees to multiple groups at once.
        
        Args:
            referee_map (dict): {group_name: referee_teams_list}
            
        Example:
            builder.assign_multiple_referees({
                '3rd': [ranks[5]],
                'final': [ranks[4]]
            })
        """
        for group_name, referee_teams in referee_map.items():
            self.assign_group_referees(group_name, referee_teams)
