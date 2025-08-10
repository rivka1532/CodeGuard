import matplotlib.pyplot as plt
from io import BytesIO

import numpy as np

from app.services.analyzer import analyze_code
from app.services.utils import load_history_for_file


def generate_analysis_graph(files: dict[str, str]) -> bytes:
    """
    מקבל מילון {filename: code_str} ומחזיר PNG של גרפים משולבים.
    """
    func_lengths = []
    issue_counts: dict[str, int] = {}
    file_issue_counts: dict[str, int] = {}

    for filename, code in files.items():
        if not filename.endswith(".py"):
            continue
        alerts = analyze_code(code, filename)  # מחזיר רשימת dict של אזהרות

        for alert in alerts:
            alert_type = alert.get("type", "Unknown")
            issue_counts[alert_type] = issue_counts.get(alert_type, 0) + 1
            file_issue_counts[filename] = file_issue_counts.get(filename, 0) + 1

            if alert_type == "Long Function":
                length = alert.get("lines", 0)
                if isinstance(length, int) and length > 0:
                    func_lengths.append(length)

    if not func_lengths:
        func_lengths = [0]  # למניעת קריסה בהיסטוגרמה

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    # 1. Histogram - Function Lengths
    axs[0, 0].hist(func_lengths, bins=range(0, max(func_lengths) + 5, 5), color='skyblue', edgecolor='black')
    axs[0, 0].set_title('Function Length Distribution')
    axs[0, 0].set_xlabel('Function Length (lines)')
    axs[0, 0].set_ylabel('Count')
    axs[0, 0].set_yticks(range(0, 21, 5))

    # 2. Pie Chart - Issue Types
    if issue_counts:
        labels = list(issue_counts.keys())
        sizes = list(issue_counts.values())
    else:
        labels = ['No Issues']
        sizes = [1]

    axs[0, 1].pie(sizes, labels=labels, autopct='%1.1f%%', colors=plt.cm.Pastel1.colors)
    axs[0, 1].set_title('Issue Types Distribution')

    # 3. Bar Chart - Issues by Type
    axs[1, 0].bar(issue_counts.keys(), issue_counts.values(), color='orange', edgecolor='black')
    axs[1, 0].set_title('Issues by Type')
    axs[1, 0].set_ylabel('Count')
    axs[1, 0].tick_params(axis='x', rotation=45)

    # 4. Bar Chart - Issues by File
    axs[1, 1].set_title('Issues Over Time')
    axs[1, 1].set_xlabel('Push Timestamp')
    axs[1, 1].set_ylabel('Total Issues')
    axs[1, 1].tick_params(axis='x', rotation=15)

    any_data = False

    for filename in files.keys():
        timestamps, issues_over_time = load_history_for_file(filename)
        if timestamps and issues_over_time:
            axs[1, 1].plot(timestamps, issues_over_time, marker='o', label=filename)
            any_data = True

    if any_data:
        axs[1, 1].legend()
        axs[1, 1].tick_params(axis='x', rotation=30)
    else:
        axs[1, 1].text(0.5, 0.5, "No history data", ha='center', va='center')

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf.read()
