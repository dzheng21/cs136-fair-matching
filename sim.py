# This file is designed to generate a set of students s_i, with size S, and colleges c_i with size C.
# This file contains all code necessary to generate a set of students s_i with size S and colleges c_i with size C.

import numpy as np
import math
from enum import Enum


class MATCH_TYPE(Enum):
    STANDARD_DA = 0,
    MODIFIED_DA = 1,
    RANDOM = 2,


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


def simulate(numColleges=10, numStudents=50, reserve_prop=0.2, spots=5, is_modified_match=True, adversity_corr=0.2):
    # Generate all colleges
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
        value_per_student = [np.random.normal(
            loc=student.student_score, scale=math.sqrt(5.0)) for student in students]
        if (is_modified_match):
            value_per_student += adversity_corr * \
                [np.random.exponential(scale=1/student.income)
                 for student in students]
        college.set_preferences(value_per_student)
    return


def simulate_incomes(numStudents, mean=11.0302, sigma=0.8179):
    # Simulate income using a log-normal distribution
    # CHECK THIS FOR VALIDITY
    income = np.random.lognormal(mean, sigma, numStudents)
    return income


def simulate_sat_scores(incomes):
    # Calculate mean SAT scores based on incomes
    mean_scores = 0.001666 * incomes + 970

    # Simulate SAT scores using a normal distribution
    sat_scores = np.random.normal(loc=mean_scores, scale=math.sqrt(200))

    return sat_scores
