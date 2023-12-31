from collections import defaultdict
import numpy as np
import math
from enum import Enum

MEDIAN_INCOME = 61740
MINORITY_CUTOFF = 2 / 3 * MEDIAN_INCOME

class MATCH_TYPE(Enum):
    STANDARD_DA = 0,
    MODIFIED_DA = 1,
    RANDOM = 2,


class ADVERSITY_FN(Enum):
    EXPONENTIAL = 0,
    SIGMOID = 1,
    INVERSE = 2,
    LOGARITHMIC = 3,
    # EXPO distribution, not to be confused with exponential function (2)
    EXPO = 4,


class College():
    def __init__(self, id, reserve_prop, spots, reputation):
        self.id = id
        self.reserve_prop = reserve_prop
        self.spots = spots
        self.reputation = reputation

    def set_preferences(self, value_per_student):
        self.value_per_student = value_per_student


class Student():
    def __init__(self, id, income, student_score, utility_per_college):
        self.id = id
        self.income = income
        self.student_score = student_score
        self.utility_per_college = utility_per_college


def simulate(
    numColleges=10,  # The number of colleges in the simulation
    numStudents=50,  # The number of students in the simulation
    reserve_prop=0.2,  # The proportion of spots reserved for disadvantaged students
    spots=5,  # The number of spots available in each college
    # Whether to use the modified matching algorithm [may be removed]
    is_modified_match=False,
    adversity_max_magnitude=100  # The maximum magnitude of adversity scores
):
    # Simulation function for project

    # First, generate all colleges
    college_reputations = np.random.normal(
        loc=50, scale=math.sqrt(15.0), size=numColleges)
    colleges = []
    for i in range(numColleges):
        colleges.append(
            College(i, reserve_prop, spots, college_reputations[i]))

    # Initialize all students starting from income and score distributions
    incomes = simulate_incomes(numStudents)
    sat_scores = simulate_sat_scores(incomes)
    students = []

    # Create all student objects
    for (id, income, sat) in zip(range(numStudents), incomes, sat_scores):
        # Generate a value for all colleges
        utility_arr = np.array([np.random.normal(
            loc=college.reputation, scale=math.sqrt(2.0)) for college in colleges])
        students.append(Student(id, income, sat, utility_arr))
    
    # Generate college rankings of students
    for college in colleges:
        value_per_student = generate_value_per_student(students)
        if (is_modified_match):
            # Using Default Parameters
            value_per_student += generate_adversity_score(
                students, adversity_max_magnitude)
        college.set_preferences(list(value_per_student))

    # Run the matching algorithm
    matching_students, matching_schools = deferred_acceptance(students, colleges, is_modified_match)
                                                              
    return matching_students, matching_schools


def generate_value_per_student(students):
    return np.array([np.random.normal(loc=student.student_score, scale=math.sqrt(5.0)) for student in students])


def generate_adversity_score(
    students,  # List of student objects for which to generate adversity scores
    adversity_max_magnitude=100,  # The maximum magnitude of adversity scores
    # The mode of adversity score distribution (EXPONENTIAL, NORMAL, etc.). See enum above
    mode=ADVERSITY_FN.EXPONENTIAL,
    # The income cutoff for adversity scaling factors (above which, no adversity adjustment)
    income_cutoff=150000
):
    # Given a mode and a cutoff, use data from students and adversity corr to calculate final adversity score scaling factor.

    scales = []  # Scale takes on some value between 0 and 1
    if (mode == ADVERSITY_FN.INVERSE):
        scales = [(1/((2*student.income/MEDIAN_INCOME)+1))
                  if student.income < income_cutoff else 0
                  for student in students]
    elif (mode == ADVERSITY_FN.SIGMOID):
        scales = [2-2*(1/(1+np.e**(-2*students.income/MEDIAN_INCOME)))
                  if student.income < income_cutoff else 0
                  for student in students]
    elif (mode == ADVERSITY_FN.EXPO):
        return [np.random.exponential(scale=MEDIAN_INCOME/student.income)
                if student.income < income_cutoff else 0
                for student in students]
    elif (mode == ADVERSITY_FN.EXPONENTIAL):
        scales = [math.e ** (-student.income / MEDIAN_INCOME)
                  if student.income < income_cutoff else 0
                  for student in students]
    elif (mode == ADVERSITY_FN.LOGARITHMIC):
        scales = [-math.log((2*student.income/MEDIAN_INCOME)+math.e)+2
                  if student.income < income_cutoff else 0
                  for student in students]
        
    return adversity_max_magnitude*np.array(scales)


def simulate_incomes(numStudents, mean=11.0302, sigma=0.8179):
    # Simulate income using a log-normal distribution
    income = np.random.lognormal(mean, sigma, numStudents)
    return income


def simulate_sat_scores(incomes):
    # Calculate mean SAT scores based on incomes
    mean_scores = 0.001666 * incomes + 970

    # Simulate SAT scores using a normal distribution
    sat_scores = np.random.normal(loc=mean_scores, scale=math.sqrt(200))

    return sat_scores

def deferred_acceptance(students, schools, minority_reserve_da = False):
    # Get the number of students and schools
    num_students = len(students)
    
    # Indicates students and schools that are free for matching
    avail_students = set(range(num_students))

    # Stores the student-school matching
    matching_students = defaultdict(lambda: None)
    matching_schools = defaultdict(lambda: [])

    # Get the preference lists of students and schools
    students_pref = [list(np.argsort(s.utility_per_college))[::-1] for s in students]
    schools_pref = [list(np.argsort(s.value_per_student))[::-1] for s in schools]
    
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
                minority.sort(key=schools_pref[i].index)

                # Accept students to the reserve and remove from general consideration pool
                reserve = min(len(minority), round(schools[i].reserve_prop * schools[i].spots))

                accepted = minority[:reserve]

                for j in accepted:
                    considered.remove(j)

            # Sort the pool of considered students by school preference
            considered.sort(key=schools_pref[i].index)
            
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
                students_pref[j].remove(i)
                if len(students_pref[j]) == 0:
                    avail_students -= set([j])
                                          
    return matching_students, matching_schools