"""
Subject Configuration Module
Defines all subjects with their syllabus breakdowns, priorities, and importance.
"""
from typing import List
from .scheduling_engine import Subject


def get_default_subjects() -> List[Subject]:
    """Get the default set of subjects for a BE Computer Science student."""
    return [
        Subject(
            name="ADSA",
            priority=1,
            difficulty=9.5,
            placement_importance=10.0,
            target_hours_per_week=(12.0, 15.0),
            topics=[
                "Arrays",
                "Strings",
                "Recursion",
                "Searching",
                "Sorting",
                "Linked Lists",
                "Stacks",
                "Queues",
                "Trees",
                "Binary Search Trees",
                "AVL Trees",
                "Heaps",
                "Hashing",
                "Graphs - BFS",
                "Graphs - DFS",
                "Graphs - Shortest Paths",
                "Greedy Algorithms",
                "Backtracking",
                "Dynamic Programming",
                "Dynamic Programming Advanced",
            ],
            is_amcat_subject=False
        ),
        Subject(
            name="COA",
            priority=2,
            difficulty=8.5,
            placement_importance=8.0,
            target_hours_per_week=(8.0, 10.0),
            topics=[
                "Number Systems",
                "Boolean Algebra",
                "CPU Organization",
                "Registers",
                "Instruction Cycle",
                "Memory Hierarchy",
                "Cache Memory",
                "Pipelining",
                "Interrupts",
                "Input/Output Organization",
            ],
            is_amcat_subject=False
        ),
        Subject(
            name="DBMS",
            priority=3,
            difficulty=7.5,
            placement_importance=9.0,
            target_hours_per_week=(8.0, 10.0),
            topics=[
                "SQL Queries",
                "Joins",
                "Normalization",
                "Transactions",
                "Indexes",
                "ER Diagrams",
                "Constraints",
                "Practice Query Solving",
            ],
            is_amcat_subject=False
        ),
        Subject(
            name="Probability",
            priority=4,
            difficulty=7.0,
            placement_importance=6.0,
            target_hours_per_week=(6.0, 8.0),
            topics=[
                "Probability Basics",
                "Conditional Probability",
                "Bayes Theorem",
                "Random Variables",
                "Probability Distributions",
                "Mean, Variance, Std Dev",
                "Sampling",
                "Correlation and Regression",
            ],
            is_amcat_subject=False
        ),
        Subject(
            name="Python",
            priority=5,
            difficulty=3.0,
            placement_importance=6.0,
            target_hours_per_week=(2.0, 3.0),
            topics=[
                "Syntax Revision",
                "Data Structures",
                "Functions",
                "OOP Concepts",
                "File Handling",
                "Problem Solving",
            ],
            is_amcat_subject=True
        ),
        Subject(
            name="UHV",
            priority=6,
            difficulty=2.0,
            placement_importance=1.0,
            target_hours_per_week=(1.0, 1.0),
            topics=[
                "Ethics and Values",
                "Self Awareness",
                "Teamwork",
                "Communication",
            ],
            is_amcat_subject=False
        ),
        Subject(
            name="Soft Skills",
            priority=7,
            difficulty=2.0,
            placement_importance=2.0,
            target_hours_per_week=(1.0, 1.0),
            topics=[
                "Resume Building",
                "Interview Preparation",
                "Body Language",
                "Presentation Skills",
                "Group Discussion",
            ],
            is_amcat_subject=False
        ),
    ]


def get_amcat_subjects() -> List[Subject]:
    """Get AMCAT-specific subjects."""
    return [
        Subject(
            name="Quantitative Aptitude",
            priority=1,
            difficulty=7.0,
            placement_importance=10.0,
            target_hours_per_week=(4.0, 5.0),
            topics=[
                "Number Systems",
                "Progressions",
                "Percentages",
                "Profit and Loss",
                "Time and Work",
                "Time, Speed and Distance",
                "Ratio and Proportion",
                "Averages",
                "Mixtures",
                "Quadratic Equations",
                "Simple and Compound Interest",
                "Permutation and Combination",
                "Probability",
            ],
            is_amcat_subject=True
        ),
        Subject(
            name="Logical Reasoning",
            priority=2,
            difficulty=7.0,
            placement_importance=10.0,
            target_hours_per_week=(3.5, 4.5),
            topics=[
                "Blood Relations",
                "Coding-Decoding",
                "Direction Sense",
                "Seating Arrangement",
                "Syllogism",
                "Analogies",
                "Series Completion",
                "Data Sufficiency",
                "Puzzles",
                "Statement and Conclusion",
            ],
            is_amcat_subject=True
        ),
        Subject(
            name="English",
            priority=3,
            difficulty=5.0,
            placement_importance=8.0,
            target_hours_per_week=(2.0, 3.0),
            topics=[
                "Reading Comprehension",
                "Grammar",
                "Vocabulary",
                "Synonyms and Antonyms",
                "Sentence Completion",
                "Error Spotting",
                "Para Jumbles",
                "Fill in the Blanks",
            ],
            is_amcat_subject=True
        ),
        Subject(
            name="Coding Problems",
            priority=4,
            difficulty=8.0,
            placement_importance=10.0,
            target_hours_per_week=(3.0, 4.0),
            topics=[
                "Array Problems",
                "String Problems",
                "Linked List Problems",
                "Tree Problems",
                "Dynamic Programming",
                "Sorting and Searching",
                "Graph Problems",
                "Recursion Problems",
            ],
            is_amcat_subject=True
        ),
        Subject(
            name="Debugging",
            priority=5,
            difficulty=6.0,
            placement_importance=7.0,
            target_hours_per_week=(1.5, 2.0),
            topics=[
                "C Debugging",
                "C++ Debugging",
                "Java Debugging",
                "Python Debugging",
                "Error Identification",
                "Code Correction",
            ],
            is_amcat_subject=True
        ),
        Subject(
            name="Core CS Revision",
            priority=6,
            difficulty=7.0,
            placement_importance=9.0,
            target_hours_per_week=(1.0, 1.5),
            topics=[
                "ADSA Fundamentals",
                "DBMS Queries",
                "Operating Systems",
                "Computer Networks",
                "COA Concepts",
            ],
            is_amcat_subject=True
        ),
    ]


# Priority mapping for quick reference
SUBJECT_PRIORITIES = {
    "ADSA": 1,
    "COA": 2,
    "DBMS": 3,
    "Probability": 4,
    "Python": 5,
    "UHV": 6,
    "Soft Skills": 7,
}


# Target hours per week
TARGET_HOURS = {
    "ADSA": (12, 15),
    "COA": (8, 10),
    "DBMS": (8, 10),
    "Probability": (6, 8),
    "Python": (2, 3),
    "UHV": (1, 1),
    "Soft Skills": (1, 1),
}


# AMCAT target hours
AMCAT_TARGET_HOURS = {
    "Quantitative Aptitude": (4, 5),
    "Logical Reasoning": (3.5, 4.5),
    "English": (2, 3),
    "Coding Problems": (3, 4),
    "Debugging": (1.5, 2),
    "Core CS Revision": (1, 1.5),
}
