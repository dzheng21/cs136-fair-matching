from collections import defaultdict
import numpy as np
from sim import *

MINORITY_CUTOFF = 2 / 3 * MEDIAN_INCOME

def deferred_acceptance(students, schools, minority_reserve_da = False):
    # Get the number of students and schools
    num_students = len(students)
    
    # Indicates students and schools that are free for matching
    avail_students = set(range(num_students))

    # Stores the student-school matching
    matching_students = defaultdict(lambda: None)
    matching_schools = defaultdict(lambda: [])

    # Get the preference lists of students and schools
    students_pref = [np.argsort(-s.utility_per_college) for s in students]
    schools_pref = [np.argsort(-s.value_per_student) for s in schools]

    # Run the deferred acceptance algorithm (while schools are available)
    while len(avail_students) > 0:
        # Get student proposals to their top-choice school
        proposals = defaultdict(lambda: [])
        for i in avail_students:
            proposals[students_pref[i][0]].append(i)

        # Consider the proposals each school received and tentatively accept students
        for i in proposals.keys():
            # Get the pool of students to consider
            considered = proposals[i] + matching_schools[i]
            accepted = []

            if (minority_reserve_da):
                # Separately consider students in minority reserve first
                minority = [j for j in considered if students[j].income < MINORITY_CUTOFF]

                # sort by school preference
                minority.sort(key=lambda x: schools_pref[i].index(x))

                # Accept students to the reserve and remove from general consideration pool
                reserve = min(len(minority), schools[i].reserve_prop * schools[i].spots)

                accepted = minority[:reserve]

                for j in accepted:
                    considered.remove(j)

            # Sort the pool of considered students by school preference
            considered.sort(key=lambda x: schools_pref[i].index(x))

            # Accept students up to the school's capacity
            spots = min(len(considered), schools[i].spots - len(accepted))
            accepted += considered[:spots]
            rejected = considered[spots:]

            # Update matchings
            matching_schools[i] = accepted
            for j in accepted:
                matching_students[j] = i

            # Update students that still need matching
            avail_students -= set(accepted)
            avail_students |= set(rejected)

            # Update the preference lists of rejected students
            for j in rejected:
                students_pref[i].remove(j)          

    return matching_students, matching_schools