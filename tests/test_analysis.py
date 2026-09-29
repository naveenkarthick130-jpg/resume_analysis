"""Unit tests for the analysis pipeline (no database required)."""

import unittest

from analysis.advanced_scorer import calculate_advanced_score
from analysis.ats_checker import check_ats
from analysis.job_match import JOB_DESCRIPTIONS, analyze_jobs, slugify_role
from analysis.resume import (
    extract_certifications,
    extract_education,
    extract_email,
    extract_experience,
    extract_languages,
    extract_name,
    extract_phone,
    extract_projects,
    extract_skills,
)
from analysis.skill_gap import JOB_SKILLS, analyze_skill_gap
from analysis.suggestion import generate_suggestions
from tests import SAMPLE_RESUME_TEXT


class ResumeExtractionTests(unittest.TestCase):

    def setUp(self):
        self.skills = extract_skills(SAMPLE_RESUME_TEXT)

    def test_extracts_name(self):
        self.assertEqual(extract_name(SAMPLE_RESUME_TEXT), "Naveen Karthik")

    def test_extracts_email(self):
        self.assertEqual(
            extract_email(SAMPLE_RESUME_TEXT),
            "naveen.karthik@example.com",
        )

    def test_extracts_indian_phone_number(self):
        self.assertIn("9876543210", extract_phone(SAMPLE_RESUME_TEXT))

    def test_extracts_international_phone_number(self):
        self.assertEqual(
            extract_phone("John Doe +1 415-555-0132"),
            "+1 415-555-0132",
        )

    def test_missing_contact_details_return_not_found(self):
        self.assertEqual(extract_name(""), "Not found")
        self.assertEqual(extract_email("no email here"), "Not found")
        self.assertEqual(extract_phone("no phone here"), "Not found")

    def test_extracts_skills(self):
        for skill in (
            "Python",
            "Flask",
            "Django",
            "SQL",
            "MySQL",
            "Git",
            "GitHub",
            "Machine Learning",
        ):
            self.assertIn(skill, self.skills)

    def test_extracts_education(self):
        self.assertEqual(extract_education(SAMPLE_RESUME_TEXT), ["B.Tech"])

    def test_extracts_experience_keywords(self):
        experience = extract_experience(SAMPLE_RESUME_TEXT)
        self.assertIn("intern", experience)
        self.assertIn("developer", experience)

    def test_extracts_projects_and_stops_at_next_section(self):
        projects = extract_projects(SAMPLE_RESUME_TEXT)
        self.assertIn("Resume Analyzer Web Application", projects)
        self.assertIn("Sentiment Analysis Dashboard", projects)
        self.assertNotIn("B.Tech in Computer Science", projects)

    def test_extracts_certifications(self):
        self.assertEqual(
            extract_certifications(SAMPLE_RESUME_TEXT),
            ["AWS Certified Cloud Practitioner"],
        )

    def test_extracts_languages(self):
        self.assertEqual(
            extract_languages(SAMPLE_RESUME_TEXT),
            ["English", "Tamil", "Hindi"],
        )


class ResumeScoringTests(unittest.TestCase):

    def setUp(self):
        self.skills = extract_skills(SAMPLE_RESUME_TEXT)
        self.education = extract_education(SAMPLE_RESUME_TEXT)
        self.experience = extract_experience(SAMPLE_RESUME_TEXT)
        self.projects = extract_projects(SAMPLE_RESUME_TEXT)
        self.certifications = extract_certifications(SAMPLE_RESUME_TEXT)
        self.score, self.breakdown, self.suggestions = calculate_advanced_score(
            extract_name(SAMPLE_RESUME_TEXT),
            extract_email(SAMPLE_RESUME_TEXT),
            extract_phone(SAMPLE_RESUME_TEXT),
            self.skills,
            self.education,
            self.experience,
            self.projects,
            self.certifications,
        )

    def test_score_is_bounded_and_matches_the_breakdown(self):
        self.assertGreater(self.score, 0)
        self.assertLessEqual(self.score, 100)
        self.assertEqual(sum(self.breakdown.values()), self.score)

    def test_breakdown_has_every_weighted_section(self):
        for section in (
            "Contact Information",
            "Skills",
            "Education",
            "Experience",
            "Projects",
            "Certifications",
            "Resume Content",
        ):
            self.assertIn(section, self.breakdown)

    def test_empty_resume_scores_zero_and_gets_advice(self):
        score, _, suggestions = calculate_advanced_score(
            "Not found",
            "Not found",
            "Not found",
            [],
            [],
            [],
            [],
            [],
        )
        self.assertEqual(score, 0)
        self.assertGreaterEqual(len(suggestions), 5)

    def test_complete_resume_gets_a_single_positive_remark(self):
        suggestions = generate_suggestions(
            self.skills,
            self.education,
            self.experience,
            self.projects,
            self.certifications,
        )
        self.assertEqual(len(suggestions), 1)
        self.assertIn("major sections", suggestions[0])

    def test_incomplete_resume_gets_targeted_suggestions(self):
        suggestions = generate_suggestions([], [], [], [], [])
        self.assertEqual(len(suggestions), 5)


class AtsCheckerTests(unittest.TestCase):

    def setUp(self):
        self.result = check_ats(
            SAMPLE_RESUME_TEXT,
            extract_skills(SAMPLE_RESUME_TEXT),
            extract_education(SAMPLE_RESUME_TEXT),
            extract_experience(SAMPLE_RESUME_TEXT),
            extract_projects(SAMPLE_RESUME_TEXT),
        )

    def test_returns_score_keywords_and_checks(self):
        self.assertIn("score", self.result)
        self.assertIn("found_keywords", self.result)
        self.assertIn("checks", self.result)

    def test_every_check_exposes_a_passed_boolean(self):
        self.assertTrue(self.result["checks"])
        for check in self.result["checks"]:
            self.assertIsInstance(check["passed"], bool)
            self.assertTrue(check["name"])
            self.assertTrue(check["message"])

    def test_complete_resume_passes_every_section_check(self):
        for check in self.result["checks"]:
            self.assertTrue(check["passed"], check["name"])

    def test_missing_sections_fail_their_checks(self):
        result = check_ats("just some text", [], [], [], [])
        failed = [
            check["name"]
            for check in result["checks"]
            if not check["passed"]
        ]
        self.assertEqual(
            failed,
            ["Skills Section", "Education", "Experience", "Projects"],
        )
        self.assertLess(result["score"], 50)


class SkillGapTests(unittest.TestCase):

    def test_lists_missing_skills_per_job_role(self):
        gaps = analyze_skill_gap(["Python", "SQL", "Flask"])
        self.assertEqual(len(gaps), len(JOB_SKILLS))

        by_job = {gap["job"]: gap for gap in gaps}
        self.assertIn("Flask", by_job["Python Developer"]["matched"])
        self.assertIn("Docker", by_job["Python Developer"]["missing"])

    def test_matched_and_missing_cover_the_required_skills(self):
        for gap in analyze_skill_gap(["Python", "Docker"]):
            required = JOB_SKILLS[gap["job"]]
            self.assertEqual(
                sorted(gap["matched"] + gap["missing"]),
                sorted(required),
            )

    def test_matching_ignores_case_and_spacing(self):
        gaps = analyze_skill_gap(["  python ", "sql"])
        by_job = {gap["job"]: gap for gap in gaps}
        self.assertIn("Python", by_job["Python Developer"]["matched"])


class JobMatchTests(unittest.TestCase):

    def setUp(self):
        self.results = analyze_jobs(
            SAMPLE_RESUME_TEXT,
            extract_skills(SAMPLE_RESUME_TEXT),
        )

    def test_slugs_are_url_safe(self):
        self.assertEqual(slugify_role("Python Developer"), "python-developer")
        self.assertEqual(
            slugify_role("Machine Learning Engineer"),
            "machine-learning-engineer",
        )

    def test_every_role_is_scored_with_all_fields(self):
        self.assertEqual(len(self.results), len(JOB_DESCRIPTIONS))

        for job in self.results:
            for key in (
                "job_role",
                "slug",
                "match_percentage",
                "skill_percentage",
                "text_percentage",
                "matched_skills",
                "missing_skills",
            ):
                self.assertIn(key, job)

            self.assertEqual(
                job["match_percentage"],
                round(
                    (job["skill_percentage"] * 0.7)
                    + (job["text_percentage"] * 0.3)
                ),
            )

    def test_results_are_sorted_by_match_percentage(self):
        percentages = [job["match_percentage"] for job in self.results]
        self.assertEqual(percentages, sorted(percentages, reverse=True))

    def test_python_developer_is_the_best_match_for_the_sample(self):
        best = self.results[0]
        self.assertEqual(best["job_role"], "Python Developer")
        self.assertIn("Flask", best["matched_skills"])
        self.assertIn("Docker", best["missing_skills"])

    def test_empty_input_returns_zero_matches(self):
        for job in analyze_jobs(""):
            self.assertEqual(job["match_percentage"], 0)
            self.assertEqual(job["matched_skills"], [])


if __name__ == "__main__":
    unittest.main()
