-- ============================================
-- Smart Resource Allocation — PostgreSQL Schema
-- ============================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- AUTH TABLES (used by Node.js auth service)
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    password_hash VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    role VARCHAR(50) DEFAULT 'volunteer' CHECK (role IN ('admin', 'coordinator', 'volunteer', 'reporter', 'donor')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deactivated')),
    avatar_url TEXT,
    phone VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

CREATE TABLE email_otps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    otp_hash VARCHAR(255) NOT NULL,
    purpose VARCHAR(50) NOT NULL CHECK (purpose IN ('signup_verification', 'forgot_password', 'email_change')),
    resend_count INTEGER DEFAULT 0,
    verify_attempt_count INTEGER DEFAULT 0,
    is_used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent TEXT
);

CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_name VARCHAR(255)
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    email VARCHAR(255),
    event_type VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}',
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- PLATFORM TABLES (used by FastAPI)
-- ============================================

CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255),
    village VARCHAR(255),
    district VARCHAR(255),
    ward VARCHAR(100),
    state VARCHAR(255),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    risk_index DOUBLE PRECISION DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE community_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    severity INTEGER DEFAULT 5 CHECK (severity BETWEEN 1 AND 10),
    urgency_score DOUBLE PRECISION DEFAULT 0,
    priority_level VARCHAR(20) DEFAULT 'medium' CHECK (priority_level IN ('low', 'medium', 'high', 'critical')),
    people_affected INTEGER DEFAULT 1,
    vulnerable_group VARCHAR(255),
    source_type VARCHAR(50) DEFAULT 'web_form' CHECK (source_type IN ('web_form', 'mobile_app', 'csv_upload', 'field_report', 'voice_note', 'image', 'phone_call', 'whatsapp')),
    reporter_id UUID REFERENCES users(id) ON DELETE SET NULL,
    location_id UUID REFERENCES locations(id),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    address_text TEXT,
    verification_status VARCHAR(30) DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'rejected', 'needs_review')),
    verified_by UUID REFERENCES users(id),
    ai_classification JSONB DEFAULT '{}',
    ai_priority_explanation TEXT,
    images TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE volunteers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    skill_tags TEXT[] DEFAULT '{}',
    languages TEXT[] DEFAULT '{}',
    availability VARCHAR(20) DEFAULT 'available' CHECK (availability IN ('available', 'busy', 'offline', 'on_leave')),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    reliability_score DOUBLE PRECISION DEFAULT 50,
    total_tasks_completed INTEGER DEFAULT 0,
    current_workload INTEGER DEFAULT 0,
    preferred_causes TEXT[] DEFAULT '{}',
    travel_radius_km DOUBLE PRECISION DEFAULT 10,
    transport_access VARCHAR(50) DEFAULT 'none',
    gender VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE resource_inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    quantity INTEGER DEFAULT 0,
    unit VARCHAR(50) DEFAULT 'units',
    warehouse_location VARCHAR(255),
    warehouse_latitude DOUBLE PRECISION,
    warehouse_longitude DOUBLE PRECISION,
    expiry_date DATE,
    availability_status VARCHAR(20) DEFAULT 'available' CHECK (availability_status IN ('available', 'reserved', 'depleted', 'expired')),
    managed_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID REFERENCES community_reports(id) ON DELETE CASCADE,
    assigned_volunteer_id UUID REFERENCES volunteers(id),
    assigned_by UUID REFERENCES users(id),
    task_type VARCHAR(100),
    title VARCHAR(500),
    description TEXT,
    status VARCHAR(30) DEFAULT 'reported' CHECK (status IN ('reported', 'verified', 'prioritized', 'assigned', 'acknowledged', 'in_progress', 'completed', 'validated', 'closed', 'follow_up_required')),
    priority_level VARCHAR(20) DEFAULT 'medium',
    priority_score DOUBLE PRECISION DEFAULT 0,
    deadline TIMESTAMPTZ,
    resources_needed JSONB DEFAULT '[]',
    ai_match_explanation TEXT,
    ai_match_score DOUBLE PRECISION,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    validated_at TIMESTAMPTZ,
    proof_urls TEXT[] DEFAULT '{}',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE impact_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    report_id UUID REFERENCES community_reports(id),
    volunteer_id UUID REFERENCES volunteers(id),
    beneficiaries_served INTEGER DEFAULT 0,
    time_to_resolve_hours DOUBLE PRECISION,
    resource_cost DOUBLE PRECISION DEFAULT 0,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    satisfaction_score INTEGER CHECK (satisfaction_score BETWEEN 1 AND 5),
    proof_url TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    type VARCHAR(50) DEFAULT 'info' CHECK (type IN ('info', 'warning', 'critical', 'assignment', 'update')),
    is_read BOOLEAN DEFAULT FALSE,
    action_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_email_otps_email_purpose ON email_otps(email, purpose);
CREATE INDEX idx_password_reset_user ON password_reset_tokens(user_id);
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_event ON audit_logs(event_type);

CREATE INDEX idx_reports_category ON community_reports(category);
CREATE INDEX idx_reports_priority ON community_reports(priority_level);
CREATE INDEX idx_reports_location ON community_reports(location_id);
CREATE INDEX idx_reports_reporter ON community_reports(reporter_id);
CREATE INDEX idx_reports_created ON community_reports(created_at DESC);

CREATE INDEX idx_volunteers_user ON volunteers(user_id);
CREATE INDEX idx_volunteers_availability ON volunteers(availability);
CREATE INDEX idx_volunteers_skills ON volunteers USING GIN(skill_tags);

CREATE INDEX idx_tasks_report ON tasks(report_id);
CREATE INDEX idx_tasks_volunteer ON tasks(assigned_volunteer_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority_level);

CREATE INDEX idx_impact_task ON impact_records(task_id);
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);

-- ============================================
-- TRIGGER: auto-update updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_reports_updated BEFORE UPDATE ON community_reports FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_volunteers_updated BEFORE UPDATE ON volunteers FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_tasks_updated BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_resources_updated BEFORE UPDATE ON resource_inventory FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE antml:parameter>
<parameter name="Complexity">5
