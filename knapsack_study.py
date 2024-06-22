import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from queue import PriorityQueue

# Function to read topics from a CSV file
def read_topics_from_csv(filename):
    topics = []
    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            topic = row['Module']
            study_time = float(row['Cost'])
            frequency = float(row['Value'])
            topics.append((topic, study_time, frequency))
    return topics

# Node class for branch and bound
class Node:
    def __init__(self, level, profit, bound, weight, items):
        self.level = level
        self.profit = profit
        self.bound = bound
        self.weight = weight
        self.items = items

    def __lt__(self, other):
        return self.bound > other.bound

# Function to calculate upper bound of profit in subtree rooted with 'node'
def bound(node, n, max_study_time, topics):
    if node.weight >= max_study_time:
        return 0
    
    profit_bound = node.profit
    j = node.level + 1
    total_weight = node.weight

    while j < n and total_weight + topics[j][1] <= max_study_time:
        total_weight += topics[j][1]
        profit_bound += topics[j][2]
        j += 1

    if j < n:
        profit_bound += (max_study_time - total_weight) * topics[j][2] / topics[j][1]

    return profit_bound

# Branch and bound function to determine the optimal set of topics to study
def knapsack_branch_and_bound(max_study_time, topics):
    topics.sort(key=lambda x: x[2] / x[1], reverse=True)
    n = len(topics)
    pq = PriorityQueue()
    u = Node(-1, 0, 0, 0, [])
    v = Node(-1, 0, 0, 0, [])
    u.bound = bound(u, n, max_study_time, topics)
    pq.put(u)

    max_profit = 0
    best_items = []

    while not pq.empty():
        u = pq.get()

        if u.bound > max_profit:
            v.level = u.level + 1

            # Take the current item
            v.weight = u.weight + topics[v.level][1]
            v.profit = u.profit + topics[v.level][2]
            v.items = u.items + [topics[v.level]]

            if v.weight <= max_study_time and v.profit > max_profit:
                max_profit = v.profit
                best_items = v.items

            v.bound = bound(v, n, max_study_time, topics)

            if v.bound > max_profit:
                pq.put(Node(v.level, v.profit, v.bound, v.weight, v.items))

            # Do not take the current item
            v.weight = u.weight
            v.profit = u.profit
            v.items = u.items
            v.bound = bound(v, n, max_study_time, topics)

            if v.bound > max_profit:
                pq.put(Node(v.level, v.profit, v.bound, v.weight, v.items))

    return best_items, max_profit

# Dynamic programming function to determine the optimal set of topics to study
def knapsack_dynamic_programming(topics, max_study_time):
    n = len(topics)
    dp = [[0 for _ in range(int(max_study_time * 100) + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        topic, study_time, frequency = topics[i - 1]
        for w in range(int(max_study_time * 100) + 1):
            if int(study_time * 100) <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - int(study_time * 100)] + frequency)
            else:
                dp[i][w] = dp[i - 1][w]

    # Backtracking to find the topics included in the optimal solution
    result = []
    w = int(max_study_time * 100)
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            topic, study_time, frequency = topics[i - 1]
            result.append(topics[i - 1])
            w -= int(study_time * 100)

    return result, dp[n][int(max_study_time * 100)]

# Greedy algorithm function to determine the optimal set of topics to study
def knapsack_greedy(topics, max_study_time):
    topics.sort(key=lambda x: x[2] / x[1], reverse=True)
    total_time = 0
    total_value = 0
    selected_topics = []

    for topic, study_time, frequency in topics:
        if total_time + study_time <= max_study_time:
            selected_topics.append((topic, study_time, frequency))
            total_time += study_time
            total_value += frequency

    return selected_topics, total_value

# Function to calculate and display the optimal set of topics to study
def calculate_study_plan(filename, algorithm):
    topics = read_topics_from_csv(filename)
    if not topics:
        return

    max_study_time = 6  # maximum study time in hours
    if algorithm == 'dynamic_programming':
        selected_topics, max_value = knapsack_dynamic_programming(topics, max_study_time)
    elif algorithm == 'branch_and_bound':
        selected_topics, max_value = knapsack_branch_and_bound(max_study_time, topics)
    elif algorithm == 'greedy':
        selected_topics, max_value = knapsack_greedy(topics, max_study_time)

    result_text = "Optimal topics to study:\n"
    for topic, study_time, frequency in selected_topics:
        result_text += f"Topic: {topic}, Study Time: {study_time:.2f}, Value: {frequency:.2f}\n"
    result_text += f"\nMaximum value of topics: {max_value:.2f}"

    result_label.config(text=result_text)

# Function to open a file dialog and select the CSV file
def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        calculate_study_plan(file_path, algorithm.get())

# Creating the main window
root = tk.Tk()
root.title("Study Plan Optimizer")
root.geometry("600x450")

# Title label
title_label = tk.Label(root, text="Study Plan Optimizer", font=("Helvetica", 16))
title_label.pack(pady=10)

# Frame for algorithm selection
algorithm_frame = tk.Frame(root)
algorithm_frame.pack(pady=10)

algorithm = tk.StringVar(value='dynamic_programming')

dynamic_rb = tk.Radiobutton(algorithm_frame, text="Dynamic Programming (Optimal)", variable=algorithm, value='dynamic_programming')
dynamic_rb.pack(side=tk.LEFT, padx=10)

branch_rb = tk.Radiobutton(algorithm_frame, text="Branch and Bound (Optimal)", variable=algorithm, value='branch_and_bound')
branch_rb.pack(side=tk.LEFT, padx=10)

greedy_rb = tk.Radiobutton(algorithm_frame, text="Greedy Algorithm (Approximate)", variable=algorithm, value='greedy')
greedy_rb.pack(side=tk.LEFT, padx=10)

# Explanation label
explanation_label = tk.Label(root, text="Dynamic Programming and Branch and Bound guarantee optimal solutions.\nGreedy Algorithm is faster but may not provide the optimal solution.", font=("Helvetica", 10), fg="blue")
explanation_label.pack(pady=10)

# Upload button to upload the CSV file
upload_button = tk.Button(root, text="Upload CSV File", command=upload_file, font=("Helvetica", 14))
upload_button.pack(pady=20)

# Label to display the results
result_label = tk.Label(root, text="", justify=tk.LEFT, font=("Helvetica", 12), wraplength=500)
result_label.pack(pady=20)

# Start the main loop
root.mainloop()
