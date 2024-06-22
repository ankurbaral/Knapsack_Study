import csv
import tkinter as tk
from tkinter import filedialog, messagebox

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

# Knapsack function to determine the optimal set of topics to study
def knapsack(topics, max_study_time):
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

# Function to calculate and display the optimal set of topics to study
def calculate_study_plan(filename):
    topics = read_topics_from_csv(filename)
    if not topics:
        return

    max_study_time = 6  # maximum study time in hours
    selected_topics, max_frequency = knapsack(topics, max_study_time)

    result_text = "Optimal topics to study:\n"
    for topic, study_time, frequency in selected_topics:
        result_text += f"Topic: {topic}, Study Time: {study_time:.2f}, Frequency: {frequency:.2f}\n"
    result_text += f"\nMaximum frequency of topics: {max_frequency:.2f}"

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
