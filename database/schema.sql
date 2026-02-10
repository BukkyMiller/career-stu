-- Career STU Database Schema
-- DuckDB tables for learner data

-- LEARNERS
CREATE TABLE IF NOT EXISTS learners (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE,
    name VARCHAR,
    status VARCHAR DEFAULT 'new',  -- new, active, paused, completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learner_profiles (
    learner_id VARCHAR PRIMARY KEY REFERENCES learners(id),
    current_job_title VARCHAR,
    current_industry VARCHAR,
    years_experience INTEGER,
    education_level VARCHAR,
    weekly_study_hours INTEGER,
    preferred_study_times VARCHAR,
    has_family_obligations BOOLEAN DEFAULT FALSE,
    employment_status VARCHAR,
    preferred_format VARCHAR DEFAULT 'any',
    disposition VARCHAR,  -- unclear, discontent, promotion, called
    inferred_riasec_code VARCHAR,  -- Learner's RIASEC profile
    profile_complete BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SKILLS
CREATE TABLE IF NOT EXISTS learner_skills (
    id VARCHAR PRIMARY KEY,
    learner_id VARCHAR REFERENCES learners(id),
    skill_name VARCHAR,
    proficiency_level VARCHAR,  -- none, beginner, intermediate, advanced, expert
    evidence_source VARCHAR,  -- self_reported, validated, credential
    validated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(learner_id, skill_name)
);

-- GOALS
CREATE TABLE IF NOT EXISTS learner_goals (
    id VARCHAR PRIMARY KEY,
    learner_id VARCHAR REFERENCES learners(id),
    target_job_title VARCHAR,
    target_riasec_code VARCHAR,
    status VARCHAR DEFAULT 'exploring',  -- exploring, committed, achieved, changed
    is_feasible BOOLEAN,
    estimated_time_months INTEGER,
    salary_estimate INTEGER,
    market_demand VARCHAR,  -- from salary_reference Labor Market Tag
    committed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PATHWAYS
CREATE TABLE IF NOT EXISTS pathways (
    id VARCHAR PRIMARY KEY,
    learner_id VARCHAR REFERENCES learners(id),
    goal_id VARCHAR REFERENCES learner_goals(id),
    status VARCHAR DEFAULT 'active',  -- active, paused, completed, superseded
    total_skills INTEGER,
    completed_skills INTEGER DEFAULT 0,
    estimated_hours INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pathway_skills (
    id VARCHAR PRIMARY KEY,
    pathway_id VARCHAR REFERENCES pathways(id),
    skill_name VARCHAR,
    sequence_order INTEGER,
    status VARCHAR DEFAULT 'not_started',  -- not_started, in_progress, completed
    estimated_hours INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- CONVERSATIONS
CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR PRIMARY KEY,
    learner_id VARCHAR REFERENCES learners(id),
    mode VARCHAR,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    summary TEXT
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_learner_status ON learners(status);
CREATE INDEX IF NOT EXISTS idx_learner_skills_learner_id ON learner_skills(learner_id);
CREATE INDEX IF NOT EXISTS idx_learner_goals_learner_id ON learner_goals(learner_id);
CREATE INDEX IF NOT EXISTS idx_learner_goals_status ON learner_goals(status);
CREATE INDEX IF NOT EXISTS idx_pathways_learner_id ON pathways(learner_id);
CREATE INDEX IF NOT EXISTS idx_pathways_status ON pathways(status);
CREATE INDEX IF NOT EXISTS idx_pathway_skills_pathway_id ON pathway_skills(pathway_id);
CREATE INDEX IF NOT EXISTS idx_conversations_learner_id ON conversations(learner_id);
