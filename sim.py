import numpy as np
import math
from enum import Enum

MEDIAN_INCOME = 61740


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
    def __init__(id, reserve_prop, spots, reputation):
        self.id = id
        self.reserve_prop = reserve_prop
        self.spots = spots
        self.reputation = reputation

    def set_preferences(value_per_student):
        self.value_per_student = value_per_student


class Student():
    def __init__(id, income, student_score, utility_per_college):
        self.id = id
        self.income = income
        self.student_score = student_score
        self.utility_per_college = []


def simulate(
    numColleges=10,  # The number of colleges in the simulation
    numStudents=50,  # The number of students in the simulation
    reserve_prop=0.2,  # The proportion of spots reserved for disadvantaged students
    spots=5,  # The number of spots available in each college
    # Whether to use the modified matching algorithm [may be removed]
    is_modified_match=True,
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
        utility_arr = [np.random.normal(
            loc=college.reputation, scale=math.sqrt(2.0)) for college in colleges]
        students.append(Student(id, income, sat, utility_arr))

    # Generate college rankings of students
    for college in colleges:
        value_per_student = generate_value_per_student(students)
        if (is_modified_match):
            # Using Default Parameters
            value_per_student += generate_adversity_score(
                students, adversity_max_magnitude)
        college.set_preferences(value_per_student)
    return


def generate_value_per_student(students):
    return [np.random.normal(loc=student.student_score, scale=math.sqrt(5.0)) for student in students]


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
        scales = [2-2(1/(1+np.e**(-students.income/61740)))
                  for student in students]
    elif (mode == ADVERSITY_FN.SIGMOID):
        scales = [2-2(1/(1+np.e**(-students.income/61740)))
                  for student in students]
    elif (mode == ADVERSITY_FN.EXPO):
        return [np.random.exponential(scale=MEDIAN_INCOME/student.income)
                for student in students]
    elif (mode == ADVERSITY_FN.EXPO):
        scales = [2-2(1/(1+np.e**(-students.income/61740)))
                  for student in students]
    elif (mode == ADVERSITY_FN.LOGARITHMIC):
        scales = [2-2(1/(1+np.e**(-students.income/61740)))
                  for student in students]
    final_scales = []
    for (student, scale) in zip(students, scales):
        final_scale = scale
        if student.income >= income_cutoff:
            final_scale = 0
        final_scales.append(scales)
    return adversity_max_magnitude*final_scales


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
