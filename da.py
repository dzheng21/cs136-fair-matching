from collections import defaultdict
import numpy as np

def deferred_acceptance(students_pref, schools_pref, schools_capacity):
    # Get the number of students and schools
    num_students = len(students_pref)
    num_schools = len(schools_pref)
    
    # Indicates students and schools that are free for matching
    avail_students = set(range(num_students))

    # Stores the student-school matching
    matching_students = defaultdict(lambda: None)
    matching_schools = defaultdict(lambda: [])

    # Run the deferred acceptance algorithm (while schools are available)
    while len(avail_students) > 0:
        # Get student proposals to their top-choice school
        proposals = defaultdict(lambda: [])
        for i in avail_students:
            proposals[students_pref[i][0]].append(i)

        # Consider the proposals each school received and tentatively accept students
        for i in proposals.keys():
            # Sort the pool of considered students by school preference
            considered = proposals[i] + matching_schools[i]
            considered.sort(key=lambda x: schools_pref[i].index(x))

            # Accept students up to the school's capacity
            num_to_accept = min(len(considered), schools_capacity[i])
            accepted = considered[:num_to_accept]
            rejected = considered[num_to_accept:]

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





   



                    

        
                
                    

            
                
