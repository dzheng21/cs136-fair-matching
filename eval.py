def calculate_aggregate_utility(students, student_matchings, income_threshold=61740):
    total_utility = 0.0
    total_utility_under = 0.0
    total_utility_over = 0.0

    for i in range(len(students)):
        utility_for_match = students[i].utility_per_college[student_matchings[i]]
        if students[i].income < income_threshold:
            total_utility_under += utility_for_match
        else:
            total_utility_over += utility_for_match
        total_utility += utility_for_match
    return total_utility, total_utility_under, total_utility_over
