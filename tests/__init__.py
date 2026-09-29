"""Shared test helpers."""

import os
import sys
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SAMPLE_RESUME_TEXT = """
Naveen Karthik
naveen.karthik@example.com
+91 9876543210

Summary
Python developer with hands-on experience building web applications.

Skills
Python, Flask, Django, SQL, MySQL, Git, GitHub, Machine Learning

Experience
Software Developer Intern at Acme Solutions
Built REST API endpoints using Flask and MySQL.

Projects
Resume Analyzer Web Application
Built a Flask app that scores resumes and recommends job roles.
Sentiment Analysis Dashboard

Education
B.Tech in Computer Science

Certifications
AWS Certified Cloud Practitioner

Languages
English, Tamil, Hindi
"""
