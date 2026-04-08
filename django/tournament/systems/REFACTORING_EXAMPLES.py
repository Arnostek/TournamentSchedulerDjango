"""
EXAMPLE: How to use the new Tournament Builders

This file shows how to refactor existing tournament systems using the modular builders.
You can use this as a reference to consolidate your other systems.

The new approach breaks down tournament generation into smaller, controllable steps:
1. PhaseManager - handles phase iteration and group creation
2. PlacementBuilder - handles placement matches (5th, 7th, 9th, etc.)
3. SemiFinalBuilder - handles semi-finals and finals
4. LastThreeBuilder - handles odd-numbered tournament final groups
5. RefereeBuilder - handles referee assignments

This gives you fine-grained control and eliminates repeated code.
"""

from .DivisionSystemBase import DivisionSystemBase


# ============================================================================
# EXAMPLE 1: Simplified TwoGroups8Teams using builders
# ============================================================================

class TwoGroups8Teams_Refactored(DivisionSystemBase):
    """
    Two groups, Lower and Higher group, finals
    
    Refactored to show how builders reduce code and improve maintainability.
    """
    
    def __init__(self, tournament, division_name, division_slug, num_of_teams):
        super(TwoGroups8Teams_Refactored, self).__init__(
            tournament, division_name, division_slug, num_of_teams, semi=False
        )
        self._createSystem()
        self._createMatches()
        self._addReferees()
    
    def _createSystem(self):
        """System definition using builders - much cleaner!"""
        
        # PHASE 1 - first round
        self.phase.create_groups(
            ['A', 'B'],
            self.division.seed_placeholders,
            referee_groups=['B', 'A']
        )
        
        # PHASE 2 - second round
        self.phase.next_phase()
        a_ranks = self.phase.get_ranks(['A'])
        b_ranks = self.phase.get_ranks(['B'])
        
        # Mix teams from A and B
        mixed_seeds = [
            a_ranks[0], a_ranks[2], b_ranks[2], b_ranks[0],
            a_ranks[1], a_ranks[3], b_ranks[3], b_ranks[1]
        ]
        self.phase.create_groups(['C', 'D'], mixed_seeds, referee_groups=['D', 'C'])
        
        # PHASE 3 - placement matches
        self.phase.next_phase()
        c_ranks = self.phase.get_ranks(['C'])
        d_ranks = self.phase.get_ranks(['D'])
        
        # Use PlacementBuilder for 7th and 5th place matches
        self.placements.create_placements_from_ranges({
            7: d_ranks[2:4],
            5: d_ranks[0:2],
        })
        
        # PHASE 4 - Finals
        self.phase.next_phase()
        self.phase.create_and_rank('3rd', c_ranks[2:4], 3)
        self.phase.create_and_rank('Final', c_ranks[0:2], 1)
    
    def _addReferees(self):
        """Simplified referee assignment using RefereeBuilder."""
        a_ranks = self.phase.get_ranks(['A'])
        b_ranks = self.phase.get_ranks(['B'])
        c_ranks = self.phase.get_ranks(['C'])
        d_ranks = self.phase.get_ranks(['D'])
        
        self.referees.assign_multiple_referees({
            '7th': [d_ranks[1]],
            '5th': [d_ranks[2]],
            '3rd': [d_ranks[0]],
            'Final': [c_ranks[2]],
        })


# ============================================================================
# EXAMPLE 2: Simplified TwoGroups15Teams using builders
# ============================================================================

class TwoGroups15Teams_Refactored(DivisionSystemBase):
    """2 base groups, QF, SF, placements - using builders."""
    
    def __init__(self, tournament, division_name, division_slug, num_of_teams):
        super(TwoGroups15Teams_Refactored, self).__init__(
            tournament, division_name, division_slug, num_of_teams, semi=True
        )
        self._createSystem()
        self._createMatches()
    
    def _createSystem(self):
        """
        BEFORE: 80 lines of repetitive code
        AFTER: 40 lines with clearer intent
        """
        
        # PHASE 1 - base groups
        self.phase.create_groups(['A', 'B'], self.division.seed_placeholders)
        ab_ranks = self.phase.get_ranks(['A', 'B'])
        
        # PHASE 2 - Quarter finals (first 8 teams)
        self.phase.next_phase()
        self.phase.create_groups(
            ['QF1', 'QF2', 'QF3', 'QF4'],
            ab_ranks[:8]
        )
        qf_ranks = self.phase.get_ranks(['QF1', 'QF2', 'QF3', 'QF4'])
        
        # PHASE 3 - Semi finals + secondary groups
        self.phase.next_phase()
        
        # Primary semis from QF winners
        self.phase.create_groups(['SF1', 'SF2'], qf_ranks[:4])
        
        # Secondary semis from QF losers
        self.phase.create_groups(['SF3', 'SF4'], qf_ranks[4:])
        
        # Additional group for teams 9-12
        self.phase.create_groups(['SF5', 'SF6'], ab_ranks[8:12])
        
        # Last 3 teams (13th place starts here)
        self.last3_group = ab_ranks[12:]
        self.phase.division.CreateGroups(['Last3'], self.last3_group, self.phase.phase, ['Last3'])
        self.phase.division.CreateRanks(13, self.phase.division.GetGroupsRanks(['Last3']))
        
        # PHASE 4 - Placement matches using builder
        self.phase.next_phase()
        sf5_sf6_ranks = self.phase.get_ranks(['SF5', 'SF6'])
        sf3_sf4_ranks = self.phase.get_ranks(['SF3', 'SF4'])
        
        self.placements.create_placements_from_ranges({
            11: sf5_sf6_ranks[2:],
            9: sf5_sf6_ranks[:2],
            7: sf3_sf4_ranks[2:],
            5: sf3_sf4_ranks[:2],
        })
        
        # PHASE 5 - Finals
        self.phase.next_phase()
        sf1_sf2_ranks = self.phase.get_ranks(['SF1', 'SF2'])
        
        self.phase.create_and_rank('3rd', sf1_sf2_ranks[2:4], 3)
        self.phase.create_and_rank('Final', sf1_sf2_ranks[0:2], 1)


# ============================================================================
# EXAMPLE 3: ThreeGroups15Teams - demonstrating group combinations
# ============================================================================

class ThreeGroups15Teams_Refactored(DivisionSystemBase):
    """3 base groups, inter-group matches, QF, SF, placements."""
    
    def __init__(self, tournament, division_name, division_slug, num_of_teams):
        super(ThreeGroups15Teams_Refactored, self).__init__(
            tournament, division_name, division_slug, num_of_teams, semi=True
        )
        self._createSystem()
        self._createMatches()
        self._addReferees()
    
    def _createSystem(self):
        
        # PHASE 1 - Three base groups
        self.phase.create_groups(
            ['A', 'B', 'C'],
            self.division.seed_placeholders,
            referee_groups=['A', 'B', 'C']
        )
        
        # PHASE 2 - Inter-group matches (complex seeding with PlacementBuilder)
        self.phase.next_phase()
        a_ranks = self.phase.get_ranks(['A'])
        b_ranks = self.phase.get_ranks(['B'])
        c_ranks = self.phase.get_ranks(['C'])
        
        # Top 6 teams
        self.phase.create_groups(['E'], [a_ranks[0], b_ranks[1], c_ranks[0]], referee_groups=['E'])
        self.phase.create_groups(['F'], [a_ranks[1], b_ranks[0], c_ranks[1]], referee_groups=['F'])
        
        # Places 7-12
        self.phase.create_groups(['G'], [a_ranks[2], b_ranks[3], c_ranks[2]], referee_groups=['G'])
        self.phase.create_groups(['H'], [a_ranks[3], b_ranks[2], c_ranks[3]], referee_groups=['H'])
        
        # PHASE 3 - Semis from top-ranked groups
        self.phase.next_phase()
        ef_ranks = self.phase.get_ranks(['E', 'F'])
        self.phase.create_groups(['SF1', 'SF2'], ef_ranks[:4])
        
        # PHASE 4 - Placements using builder
        self.phase.next_phase()
        gh_ranks = self.phase.get_ranks(['G', 'H'])
        
        self.placements.create_placements_from_ranges({
            11: gh_ranks[4:6],
            9: gh_ranks[2:4],
            7: gh_ranks[:2],
            5: ef_ranks[4:],
        })
        
        # PHASE 5 - Last3 and Finals
        self.phase.next_phase()
        abc_ranks = self.phase.get_ranks(['A', 'B', 'C'])
        self.last3_builder.create_last3_group(['A', 'B', 'C'])
        
        sf_ranks = self.phase.get_ranks(['SF1', 'SF2'])
        self.phase.create_and_rank('3rd', sf_ranks[2:4], 3)
        self.phase.create_and_rank('Final', sf_ranks[0:2], 1)
    
    def _addReferees(self):
        """Clean referee assignment using builder."""
        gh_ranks = self.phase.get_ranks(['G', 'H'])
        ef_ranks = self.phase.get_ranks(['E', 'F'])
        
        self.referees.assign_multiple_referees({
            'SF1': [ef_ranks[4]],
            'SF2': [ef_ranks[5]],
            '11th': [ef_ranks[3]],
            '9th': [ef_ranks[2]],
            '7th': [gh_ranks[2]],
            '5th': [gh_ranks[0]],
            '3rd': [ef_ranks[5]],
            'Final': [ef_ranks[4]],
        })


# ============================================================================
# USAGE NOTES
# ============================================================================
"""
BENEFITS OF REFACTORING:
1. Less code - reduces repetition by ~50%
2. More control - you can customize each phase independently
3. Better readability - phase intent is clear from builder methods
4. Easier debugging - failures are isolated to specific builder operations
5. Reusable - mix and match builders for new tournament types

HOW TO REFACTOR YOUR SYSTEMS:
1. Identify PHASES in your _createSystem() method
2. For each phase, use self.phase.create_groups() or self.phase.next_phase()
3. Replace placement match code with self.placements.create_placements_from_ranges()
4. Replace semi/final code with self.semis and self.phase.create_and_rank()
5. Replace referee code with self.referees.assign_multiple_referees()

EXAMPLE PATTERNS:
- Create base groups: self.phase.create_groups(['A', 'B', 'C'], teams)
- Get ranks: self.phase.get_ranks(['A', 'B', 'C'])
- Next phase: self.phase.next_phase()
- Create placement: self.placements.create_placement(5, teams[4:6])
- Multiple placements: self.placements.create_placements_from_ranges({5: teams, 7: teams})
- Assign referees: self.referees.assign_multiple_referees({'3rd': refs, 'Final': refs})
"""
