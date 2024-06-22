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
def knapsack(max_study_time, topics):
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

# Function to calculate and display the optimal set of topics to study
def calculate_study_plan(filename):
    topics = read_topics_from_csv(filename)
    if not topics:
        return

    max_study_time = 6  # maximum study time in hours
    selected_topics, max_profit = knapsack(max_study_time, topics)

    result_text = "Optimal topics to study:\n"
    for topic, study_time, frequency in selected_topics:
        result_text += f"Topic: {topic}, Study Time: {study_time:.2f}, Value: {frequency:.2f}\n"
    result_text += f"\nMaximum value of topics: {max_profit:.2f}"

    result_label.config(text=result_text)

# Function to open a file dialog and select the CSV file
def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        calculate_study_plan(file_path)

# Creating the main window
root = tk.Tk()
root.title("Study Plan Optimizer")

# Upload button to upload the CSV file
upload_button = tk.Button(root, text="Upload CSV File", command=upload_file)
upload_button.pack(pady=20)

# Label to display the results
result_label = tk.Label(root, text="", justify=tk.LEFT)
result_label.pack(pady=20)

# Start the main loop
root.mainloop()
