CREATE DATABASE IF NOT EXISTS resume_analyzer;
USE resume_analyzer;

CREATE TABLE IF NOT EXISTS resumes (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(320) NULL,
    phone VARCHAR(50) NULL,
    skills JSON NOT NULL,
    education JSON NOT NULL,
    experience JSON NOT NULL,
    projects JSON NOT NULL,
    certifications JSON NOT NULL,
    score DECIMAL(5, 2) NOT NULL DEFAULT 0,
    ats_score DECIMAL(5, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_resumes_email (email),
    INDEX idx_resumes_created_at (created_at)
);
