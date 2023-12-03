# This file is designed to generate a set of students s_i, with size S, and colleges c_i with size C.
# This file contains all code necessary to generate a set of students s_i with size S and colleges c_i with size C.

# @param r : denotes the number of reserves for each school (assume uniform)
# @param m : denotes the proportion of the population that is minorities/underprivileged ()
# @param M : denotes the number of students that each college can take (can expand this to be state and private for different sizes)
# @param

# let's assume that all students have the same center -> some academic score
# then let's assume that there is a normally distributed adversity score
# assume that there is a normal distribution of all colleges
# assume that there is a normal distribution of students who are majority
# assume that there is a normal distribution of students who are minority

# What variables do we need
# 1. number of students
# 2. number of colleges
# 3. How many students can each college take?
# 4. diversity center ?

class College():
    def __init__(id, reserve_prop, spots, college_score):
        self.id = id
        self.reserve_prop = reserve_prop
        self.spots = spots
        self.college_score = college_score


class Student():
    def __init__(id, priv_index, student_score):
        self.id = id
        self.priv_index = priv_index
        self.student_score = student_score


def simulate(numColleges, numStudents, muCollege=50, varCollege=10, muStudent=50, varStudent=10, varPriv=10):
    # def simulate(numColleges, numStudents, muCollege, varCollege, muStudentPriv, varStudentPriv, muStudentUnder, varStudentUnder):
    # normally distribute with average mu and var college
    return
