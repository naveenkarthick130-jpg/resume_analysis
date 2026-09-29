"""Integration tests for the Flask routes and templates (no database required)."""

import io
import os
import unittest

from app import UPLOAD_FOLDER, app
from analysis.job_match import analyze_jobs


class TemplateRenderingTests(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.resume = {
            "id": 7,
            "name": "Naveen Karthik",
            "email": "naveen.karthik@example.com",
            "phone": "+91 9876543210",
            "skills": ["Python", "Flask", "SQL"],
            "education": ["B.Tech"],
            "experience": ["intern"],
            "projects": ["Resume Analyzer Web Application"],
            "certifications": ["AWS Certified Cloud Practitioner"],
            "score": 88.0,
            "ats_score": 91.0,
            "created_at": "2026-01-01 10:00:00",
        }

    def render(self, template, **context):
        with self.app.test_request_context("/"):
            return self.app.jinja_env.get_template(template).render(**context)

    def test_saved_report_page_renders_decoded_lists(self):
        html = self.render(
            "view_resume.html",
            resume=self.resume,
            job_results=analyze_jobs("python flask sql", self.resume["skills"]),
        )

        self.assertIn("Naveen Karthik", html)
        self.assertIn("AWS Certified Cloud Practitioner", html)
        self.assertIn("Python", html)
        self.assertIn("/resume/7/delete", html)
        self.assertIn("/resume/7/job/python-developer", html)
        self.assertNotIn("```", html)
        self.assertNotIn("['B.Tech']", html)

    def test_saved_report_page_handles_empty_sections(self):
        empty = dict(
            self.resume,
            skills=[],
            education=[],
            experience=[],
            projects=[],
            certifications=[],
        )
        html = self.render("view_resume.html", resume=empty, job_results=[])

        self.assertIn("No skills were detected", html)
        self.assertIn("No job matches available", html)

    def test_result_page_uses_the_passed_flag_for_ats_checks(self):
        report = {
            "resume_text": "python sql git developer",
            "resume_id": 7,
            "save_error": None,
            "name": "Naveen Karthik",
            "email": "a@b.com",
            "phone": "9876543210",
            "skills": ["Python"],
            "education": ["B.Tech"],
            "experience": ["developer"],
            "projects": ["Resume Analyzer"],
            "certifications": [],
            "languages": ["English"],
            "score": 80.0,
            "score_breakdown": {"Skills": 20},
            "score_suggestions": [],
            "ats_result": {
                "score": 70,
                "found_keywords": ["python", "sql"],
                "checks": [
                    {
                        "name": "Skills Section",
                        "status": "Missing",
                        "passed": False,
                        "message": "Add a clear skills section.",
                    },
                ],
            },
            "job_results": analyze_jobs("python", ["Python"]),
            "skill_gap": [{"job": "Python Developer", "matched": [], "missing": []}],
            "suggestions": ["Add more projects."],
        }
        html = self.render("result.html", **report)

        self.assertIn("Saved to your history as report #7", html)
        self.assertIn("python-developer", html)

    def test_job_detail_page_renders_matched_and_missing_skills(self):
        html = self.render(
            "job_result.html",
            resume_id=7,
            job_role="Python Developer",
            match_percentage=64,
            matched_skills=["Python", "SQL"],
            missing_skills=["Docker"],
        )

        self.assertIn("Python Developer", html)
        self.assertIn("Docker", html)
        self.assertIn("/resume/7", html)
        self.assertNotIn("forloop", html)


class RouteTests(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Resume", response.data)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_unknown_page_shows_the_error_screen(self):
        response = self.client.get("/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Page not found", response.data)

    def test_history_page_survives_a_missing_database(self):
        response = self.client.get("/history")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Resume", response.data)

    def test_upload_without_a_file_is_rejected(self):
        response = self.client.post("/upload", data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Upload problem", response.data)

    def test_upload_with_a_non_pdf_is_rejected(self):
        response = self.client.post(
            "/upload",
            data={"resume": (io.BytesIO(b"hello"), "notes.txt")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_broken_pdf_is_rejected_and_not_kept(self):
        before = set(os.listdir(UPLOAD_FOLDER))

        response = self.client.post(
            "/upload",
            data={"resume": (io.BytesIO(b"not really a pdf"), "broken.pdf")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(os.listdir(UPLOAD_FOLDER)), before)


if __name__ == "__main__":
    unittest.main()
