"""
TOURNAMENT SYSTEM REFACTORING GUIDE
====================================

This guide explains the new modular builder system and how to migrate
your existing tournament systems to use it.

WHY CONSOLIDATE?
----------------
Your tournament systems had ~50% repeated code across:
  - Phase management and group creation 
  - Placement match generation (5th, 7th, 9th, 11th)
  - Semi-final and final orchestration
  - Referee assignment patterns

The new builder system reduces this by providing reusable components for
each of these concerns.

AVAILABLE BUILDERS
------------------

1. PhaseManager (self.phase)
   - Manages phase iteration
   - Creates groups and caches ranks for reuse
   - Provides convenience methods for group creation
   
   Methods:
     next_phase()              → Increment phase counter
     create_groups()           → Create groups and cache ranks
     get_ranks()               → Get cached or fresh ranks
     create_and_rank()         → Create group + assign placement rank

2. PlacementBuilder (self.placements)
   - Handles placement match generation (5th, 7th, 9th, 11th, etc.)
   - Eliminates repeated code for "position matches"
   
   Methods:
     create_placement()        → Create single placement match
     create_placements_from_ranges()  → Create multiple in batch
     create_placement_bracket()       → Auto-generate bracket from remaining teams

3. SemiFinalBuilder (self.semis)
   - Handles semi-final and final orchestration
   - Provides clean separation of semi/final logic
   
   Methods:
     create_semifinals()       → Create two semi-final groups
     create_third_place()      → Create 3rd place match from semi losers
     create_final()            → Create final match from semi winners

4. LastThreeBuilder (self.last3_builder)
   - Handles odd-numbered tournament final groups
   - Manages the "Last3" group creation
   
   Methods:
     create_last3_group()      → Create final 3 teams group & ranking

5. RefereeBuilder (self.referees)
   - Handles referee assignment to final matches
   - Replaces manual loop-based assignment
   
   Methods:
     assign_group_referees()   → Assign refs to single group
     assign_multiple_referees() → Assign refs to multiple groups at once


MIGRATION EXAMPLES
------------------

BEFORE - Original TwoGroups8Teams (repetitive):

    def _createSystem(self):
        phase = 1
        self.division.CreateGroups(['A','B'], self.division.seed_placeholders, phase, ['B','A'])
        
        phase += 1
        a_ranks = self.division.GetGroupsRanks(['A'])
        b_ranks = self.division.GetGroupsRanks(['B'])
        self.division.CreateGroups(['C','D'], [a_ranks[0],a_ranks[2],...], phase, ['D','C'])
        
        phase += 1
        self.division.CreateGroups(['7th'], self.division.GetGroupsRanks(['D'])[2:4], phase)
        self.division.CreateRanks(7, self.division.GetGroupsRanks(['7th']))
        
        self.division.CreateGroups(['5th'], self.division.GetGroupsRanks(['D'])[0:2], phase)
        self.division.CreateRanks(5, self.division.GetGroupsRanks(['5th']))
        
        phase += 1
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['C'])[2:4], phase)
        self.division.CreateRanks(3, self.division.GetGroupsRanks(['3rd']))
        
        phase += 1
        self.division.CreateGroups(['Final'], self.division.GetGroupsRanks(['C'])[0:2], phase)
        self.division.CreateRanks(1, self.division.GetGroupsRanks(['Final']))


AFTER - Using builders (clean & modular):

    def _createSystem(self):
        # Phase 1
        self.phase.create_groups(['A', 'B'], self.division.seed_placeholders, 
                                 referee_groups=['B', 'A'])
        
        # Phase 2
        self.phase.next_phase()
        a_ranks = self.phase.get_ranks(['A'])
        b_ranks = self.phase.get_ranks(['B'])
        self.phase.create_groups(['C', 'D'], [a_ranks[0], a_ranks[2], ...], 
                                 referee_groups=['D', 'C'])
        
        # Phase 3 - Placements
        self.phase.next_phase()
        c_ranks = self.phase.get_ranks(['C'])
        d_ranks = self.phase.get_ranks(['D'])
        
        self.placements.create_placements_from_ranges({
            7: d_ranks[2:4],
            5: d_ranks[0:2],
        })
        
        # Phase 4 - Finals
        self.phase.next_phase()
        self.phase.create_and_rank('3rd', c_ranks[2:4], 3)
        self.phase.create_and_rank('Final', c_ranks[0:2], 1)


KEY CHANGES:
- Manual phase increment → phase.next_phase()
- Repeated GetGroupsRanks → phase.get_ranks() (auto-cached)
- Repeated CreateGroups + CreateRanks → placements.create_placements_from_ranges()
- Manual final logic → phase.create_and_rank()
- Manual referee loops → referees.assign_multiple_referees()


REFACTORING CHECKLIST
---------------------

For each of your tournament systems:

□ 1. Replace manual phase tracking with self.phase.next_phase()
     - Remove: phase = 1
     - Remove: phase += 1 (use self.phase.next_phase() instead)
     - Use: self.phase.phase (if you need the phase number)

□ 2. Replace GetGroupsRanks calls with self.phase.get_ranks()
     - Benefits: auto-caching, consistent naming
     - self.phase.get_ranks(['A', 'B']) instead of self.division.GetGroupsRanks(['A', 'B'])

□ 3. Convert placement match creation to placements builder
     - Find patterns like: CreateGroups + CreateRanks for 5th, 7th, 9th
     - Replace with: self.placements.create_placements_from_ranges({5: teams, 7: teams})

□ 4. Convert finals/semi logic to builders
     - Replace semi creation with self.semis.create_semifinals()
     - Replace 3rd place with self.semis.create_third_place()
     - Replace final with self.semis.create_final()

□ 5. Convert referee assignment to RefereeBuilder
     - Replace manual loops with self.referees.assign_multiple_referees({...})


QUICK START - 3 STEPS
--------------------

1. Update your __init__ to keep existing pattern:
   super().__init__(tournament, division_name, division_slug, num_of_teams, semi=True)
   (Builders are auto-initialized in base class)

2. Update _createSystem():
   a. Replace phase management with self.phase methods
   b. Extract getranks() calls into variables  
   c. Use placements.create_placements_from_ranges() for placement matches
   d. Use phase.create_and_rank() for finals

3. Update _addReferees():
   a. Collect all referee assignments into a dict
   b. Use self.referees.assign_multiple_referees(referee_dict)


COMMON PATTERNS
---------------

Pattern: Creating base groups
    OLD: self.division.CreateGroups(['A', 'B'], teams, phase)
    NEW: self.phase.create_groups(['A', 'B'], teams)

Pattern: Getting ranks multiple times
    OLD: 
        a_ranks = self.division.GetGroupsRanks(['A'])
        a_ranks = self.division.GetGroupsRanks(['A'])  # repeated!
    NEW:
        a_ranks = self.phase.get_ranks(['A'])  # cached, only called once

Pattern: Creating placement matches
    OLD:
        self.division.CreateGroups(['5th'], teams[4:6], phase)
        self.division.CreateRanks(5, self.division.GetGroupsRanks(['5th']))
        self.division.CreateGroups(['7th'], teams[6:8], phase)
        self.division.CreateRanks(7, self.division.GetGroupsRanks(['7th']))
    NEW:
        self.placements.create_placements_from_ranges({
            5: teams[4:6],
            7: teams[6:8],
        })

Pattern: Finals from semi-finals
    OLD:
        phase += 1
        self.division.CreateGroups(['3rd'], semi_ranks[2:4], phase)
        self.division.CreateRanks(3, self.division.GetGroupsRanks(['3rd']))
        phase += 1
        self.division.CreateGroups(['Final'], semi_ranks[0:2], phase)
        self.division.CreateRanks(1, self.division.GetGroupsRanks(['Final']))
    NEW:
        self.phase.next_phase()
        self.phase.create_and_rank('3rd', semi_ranks[2:4], 3)
        self.phase.next_phase()
        self.phase.create_and_rank('Final', semi_ranks[0:2], 1)

Pattern: Referee assignment
    OLD:
        self._GroupAddReferees('3rd', [a_ranks[5]])
        self._GroupAddReferees('final', [a_ranks[4]])
    NEW:
        self.referees.assign_multiple_referees({
            '3rd': [a_ranks[5]],
            'final': [a_ranks[4]],
        })


TESTING YOUR CHANGES
--------------------

After refactoring a system:

1. Ensure it initializes without errors:
   from django.tournament.systems import NewSystem
   system = NewSystem(tournament, 'name', 'slug', 16)

2. Verify groups are created:
   division.group_set.count()  # Should match expected phase groups

3. Verify rankings are assigned:
   division.rank_set.count()  # Should equal team count

4. Run your existing tests if you have them

5. Compare output with original system to ensure same structure


REFERENCE FILES
---------------

- TournamentBuilders.py      → Implementation of all builder classes
- REFACTORING_EXAMPLES.py    → Example refactored systems
- DivisionSystemBase.py      → Updated base class with builders
- This file                   → Migration guide (you are here)


QUESTIONS?
----------

If unsure about a pattern:
1. Check REFACTORING_EXAMPLES.py for similar tournament type
2. Look at specific builder method docstrings in TournamentBuilders.py
3. Compare old vs new approach in examples
   
The builders are designed to handle ~90% of common tournament structures.
For complex custom logic, you can still use self.division directly while
using builders for repetitive parts.
"""

# End of guide
