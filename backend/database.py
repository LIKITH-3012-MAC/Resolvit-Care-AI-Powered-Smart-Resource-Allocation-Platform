"""
Smart Resource Allocation — Database Layer
Async PostgreSQL connection pool using asyncpg.
Auto-creates tables on first run.
"""

import ssl
import asyncpg
from backend.config import settings

class MockPool:
    """Mock database pool for local development when Postgres is unavailable."""
    class MockConn:
        async def fetch(self, q, *a): return []
        async def fetchrow(self, q, *a): return None
        async def execute(self, q, *a): return "SUCCESS"
        async def fetchval(self, q, *a): return None
        async def close(self): pass
    
    async def acquire(self):
        return self.MockConn()
    async def release(self, conn):
        pass
    async def close(self):
        pass

pool = None

async def init_db():
    """Initialize the global connection pool."""
    global pool
    if pool is not None:
        return
        
    raw_url = settings.DATABASE_URL
    # Convert SQLAlchemy dialect prefixes to asyncpg-compatible format
    clean_url = raw_url.replace("postgresql+asyncpg://", "postgresql://").replace("postgres://", "postgresql://")
    
    needs_ssl = any(x in clean_url for x in ["ssl=require", "aivencloud", "neon", "supabase"])
    clean_url = clean_url.split("?")[0] if "?" in clean_url else clean_url
    
    ssl_ctx = None
    if needs_ssl:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        
    try:
        pool = await asyncpg.create_pool(
            clean_url,
            ssl=ssl_ctx,
            min_size=5,
            max_size=20,
            command_timeout=30
        )
        print("  ✅ Database connection pool initialized")
    except Exception as e:
        if settings.DEBUG:
            print(f"  ⚠️ Failed to connect to DB: {e}. Falling back to MockPool for development.")
            pool = MockPool()
        else:
            print(f"  ❌ Failed to initialize database pool: {e}")
            raise

async def close_db():
    """Close the global connection pool."""
    global pool
    if pool:
        await pool.close()
        pool = None
        print("  🔌 Database connection pool closed")

async def get_db():
    """Dependency for FastAPI to get a connection from the pool."""
    if pool is None:
        await init_db()
    async with pool.acquire() as conn:
        yield conn

async def fetch_all(query: str, *args):
    """Execute query and return all rows as list of dicts."""
    if pool is None: await init_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *args)
        return [dict(row) for row in rows]

async def fetch_one(query: str, *args):
    """Execute query and return single row as dict."""
    if pool is None: await init_db()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *args)
        return dict(row) if row else None

async def execute(query: str, *args):
    """Execute a statement (INSERT/UPDATE/DELETE)."""
    if pool is None: await init_db()
    async with pool.acquire() as conn:
        return await conn.execute(query, *args)

async def execute_returning(query: str, *args):
    """Execute a statement and return the result row."""
    if pool is None: await init_db()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *args)
        return dict(row) if row else None


async def _get_conn():
    """Internal helper to get a raw connection from the pool."""
    if pool is None:
        await init_db()
    return await pool.acquire()


# ──── Schema Auto-Creation ────

SCHEMA_SQL = """
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    password_hash VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    role VARCHAR(50) DEFAULT 'volunteer' CHECK (role IN ('admin', 'coordinator', 'volunteer', 'reporter', 'donor')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deactivated')),
    auth_provider VARCHAR(20) DEFAULT 'database',
    auth0_sub VARCHAR(255),
    avatar_url TEXT,
    phone VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

-- Email OTPs
CREATE TABLE IF NOT EXISTS email_otps (
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

-- Password Reset Tokens
CREATE TABLE IF NOT EXISTS password_reset_tokens (
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

-- Refresh Tokens
CREATE TABLE IF NOT EXISTS refresh_tokens (
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

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    email VARCHAR(255),
    event_type VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}',
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Locations
CREATE TABLE IF NOT EXISTS locations (
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

-- Community Reports
CREATE TABLE IF NOT EXISTS community_reports (
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
    source_type VARCHAR(50) DEFAULT 'web_form',
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

-- Volunteers
CREATE TABLE IF NOT EXISTS volunteers (
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

-- Resource Inventory
CREATE TABLE IF NOT EXISTS resource_inventory (
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

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (
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

-- Impact Records
CREATE TABLE IF NOT EXISTS impact_records (
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

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    type VARCHAR(50) DEFAULT 'info' CHECK (type IN ('info', 'warning', 'critical', 'assignment', 'update')),
    is_read BOOLEAN DEFAULT FALSE,
    action_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI Knowledge Base
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

INDEXES_SQL = """
-- Indexes (IF NOT EXISTS requires PG 9.5+)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_reports_category ON community_reports(category);
CREATE INDEX IF NOT EXISTS idx_reports_priority ON community_reports(priority_level);
CREATE INDEX IF NOT EXISTS idx_reports_created ON community_reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_volunteers_availability ON volunteers(availability);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority_level);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read);
"""

SEED_ADMIN_SQL = """
-- Seed admin user if not exists (password: Admin@123456)
INSERT INTO users (email, name, password_hash, role, email_verified, status)
VALUES ('admin@smartresource.org', 'System Admin', 
        '$2b$12$LJ3m4ys3GZvPMiKcPCsP6eSFD.e7GJR5E3TCp0KW1VkzR3xS6Y8ge',
        'admin', TRUE, 'active')
ON CONFLICT (email) DO NOTHING;
"""


async def ensure_schema():
    """Create all tables if they don't exist, then seed admin user."""
    if pool is None: await init_db()
    async with pool.acquire() as conn:
        try:
            try:
                await conn.execute(SCHEMA_SQL)
                print("  ✅ Tables created/verified")
            except Exception as e:
                print(f"  ⚠️ Schema creation note: {e}")

            # Migration: add auth0 columns if they don't exist
            migrations = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(20) DEFAULT 'database'",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS auth0_sub VARCHAR(255)",
            ]
            for sql in migrations:
                try:
                    await conn.execute(sql)
                except Exception:
                    pass

            try:
                await conn.execute(INDEXES_SQL)
                print("  ✅ Indexes created/verified")
            except Exception as e:
                print(f"  ⚠️ Index creation note: {e}")

            try:
                import bcrypt
                admin = await conn.fetchrow("SELECT id FROM users WHERE email = 'admin@smartresource.org'")
                if not admin:
                    pw_hash = bcrypt.hashpw("Admin@123456".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                    await conn.execute(
                        """INSERT INTO users (email, name, password_hash, role, email_verified, status)
                           VALUES ($1, $2, $3, $4, TRUE, 'active')""",
                        "admin@smartresource.org", "System Admin", pw_hash, "admin"
                    )
                    print("  ✅ Admin user seeded (admin@smartresource.org / Admin@123456)")
                else:
                    print("  ✅ Admin user exists")
            except Exception as e:
                print(f"  ⚠️ Admin seed note: {e}")
        except Exception as e:
            print(f"  ❌ Database schema/seed error: {e}")
            raise
