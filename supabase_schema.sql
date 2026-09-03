-- ============================================================
-- TASSIMO BTP CONSTRUCTION SARL
-- AI BUSINESS, CONSTRUCTION & TRAINING PLATFORM
-- DATABASE FOUNDATION
-- ============================================================

create extension if not exists "uuid-ossp";

-- ============================================================
-- 1. COMPANY PROFILE
-- ============================================================

create table if not exists company_profile (
    id uuid primary key default uuid_generate_v4(),
    business_name text not null default 'TASSIMO BTP CONSTRUCTION SARL',
    ceo_name text not null default 'TAGNE Simo Innocant',
    location text default 'Douala – Logpom, Cameroon',
    slogan text default 'Together, let us build excellence.',
    logo_url text,
    phone text,
    email text,
    website text,
    address text,
    default_language text default 'en'
        check (default_language in ('en', 'fr')),
    currency text default 'XAF',
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================
-- 2. USERS / STAFF
-- ============================================================

create table if not exists users (
    id uuid primary key default uuid_generate_v4(),
    auth_user_id uuid unique,
    full_name text not null,
    email text unique,
    phone text,
    role text not null default 'staff'
        check (role in (
            'ceo',
            'admin',
            'manager',
            'sales',
            'construction',
            'finance',
            'training',
            'marketing',
            'staff',
            'student'
        )),
    preferred_language text default 'en'
        check (preferred_language in ('en', 'fr')),
    is_active boolean default true,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================
-- 3. CUSTOMERS / PROSPECTS
-- ============================================================

create table if not exists customers (
    id uuid primary key default uuid_generate_v4(),

    full_name text not null,
    phone text,
    email text,

    source text,
    preferred_language text default 'en'
        check (preferred_language in ('en', 'fr')),

    customer_type text default 'prospect'
        check (customer_type in ('prospect', 'customer', 'student', 'partner')),

    stage text default 'cold'
        check (stage in (
            'cold',
            'interested',
            'qualified',
            'very_hot',
            'client',
            'lost'
        )),

    service_interest text
        check (service_interest in (
            'construction',
            'renovation',
            'design',
            'civil_engineering',
            'training',
            'other'
        )),

    location text,
    budget numeric(15,2),

    project_type text,
    land_location text,
    land_size numeric(12,2),
    desired_floor_area numeric(12,2),
    bedrooms integer,

    finish_level text,

    has_land boolean,
    has_plan boolean,

    plan_only boolean default false,
    complete_construction boolean default false,

    interest_score integer default 0
        check (interest_score between 0 and 100),

    last_interaction_at timestamptz,
    next_action text,
    next_follow_up_at timestamptz,

    notes text,

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================
-- 4. CUSTOMER CONVERSATIONS
-- ============================================================

create table if not exists conversations (
    id uuid primary key default uuid_generate_v4(),

    customer_id uuid references customers(id) on delete cascade,

    channel text not null default 'website'
        check (channel in (
            'website',
            'whatsapp',
            'facebook',
            'instagram',
            'email',
            'phone',
            'other'
        )),

    external_conversation_id text,

    status text default 'open'
        check (status in (
            'open',
            'waiting_customer',
            'waiting_ceo',
            'closed'
        )),

    language text default 'en'
        check (language in ('en', 'fr')),

    ai_enabled boolean default true,

    last_message_at timestamptz,

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================
-- 5. CONVERSATION MESSAGES
-- ============================================================

create table if not exists messages (
    id uuid primary key default uuid_generate_v4(),

    conversation_id uuid references conversations(id) on delete cascade,

    sender_type text not null
        check (sender_type in (
            'customer',
            'ai',
            'ceo',
            'staff',
            'system'
        )),

    message_text text not null,

    language text default 'en'
        check (language in ('en', 'fr')),

    ai_generated boolean default false,

    requires_approval boolean default false,
    approved boolean default false,

    created_at timestamptz default now()
);

-- ============================================================
-- 6. LEADS / SALES OPPORTUNITIES
-- ============================================================

create table if not exists sales_opportunities (
    id uuid primary key default uuid_generate_v4(),

    customer_id uuid references customers(id) on delete cascade,

    title text not null,

    service_type text,

    estimated_value numeric(15,2),

    stage text default 'new'
        check (stage in (
            'new',
            'qualified',
            'proposal',
            'negotiation',
            'won',
            'lost'
        )),

    probability integer default 0
        check (probability between 0 and 100),

    expected_close_date date,

    assigned_to uuid references users(id),

    notes text,

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================
-- 7. CONSTRUCTION PROJECTS
-- ============================================================

create table if not exists projects (
    id uuid primary key default uuid_generate_v4(),

    customer_id uuid references customers(id) on delete set null,

    project_name text not null,

    project_type text,

    location text,

    land_size numeric(12,2),
    floor_area numeric(12,2),

    number_of_floors integer,
    bedrooms integer,

    finish_level text,

    status text default 'lead'
        check (status in (
            'lead',
            'planning',
            'quotation',
            'approved',
            'active',
            'on_hold',
            'completed',
            'cancelled'
        )),

    estimated_budget numeric(15,2),
    approved_budget numeric(15,2),

    start_date date,
    expected_completion_date date,
    actual_completion_date date,

    progress_percent integer default 0
        check (progress_percent between 0 and 100),

    notes text,

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================
-- 8. PROJECT DOCUMENTS / PLANS
-- ============================================================

create table if not exists project_documents (
    id uuid primary key default uuid_generate_v4(),

    project_id uuid references projects(id) on delete cascade,

    customer_id uuid references customers(id) on delete set null,

    document_name text not null,

    document_type text
        check (document_type in (
            'architectural_plan',
            'structural_plan',
            'electrical_plan',
            'plumbing_plan',
            'boq',
            'drawing',
            'site_photo',
            'quotation',
            'invoice',
            'contract',
            'other'
        )),

    file_url text,

    ai_analysis text,

    ai_confidence numeric(5,2),

    requires_professional_review boolean default true,

    created_at timestamptz default now()
);

-- ============================================================
-- 9. ESTIMATES
-- ============================================================

create table if not exists estimates (
    id uuid primary key default uuid_generate_v4(),

    project_id uuid references projects(id) on delete cascade,

    customer_id uuid references customers(id) on delete set null,

    estimate_number text unique,

    subtotal numeric(15,2) default 0,

    vat_rate numeric(5,2) default 0,
    vat_amount numeric(15,2) default 0,

    discount numeric(15,2) default 0,

    total_amount numeric(15,2) default 0,

    customer_budget numeric(15,2),

    budget_difference numeric(15,2),

    status text default 'draft'
        check (status in (
            'draft',
            'ai_preliminary',
            'pending_review',
            'approved',
            'sent',
            'accepted',
            'rejected'
        )),

    ai_generated boolean default false,

    ceo_approved boolean default false,

    uncertainty_notes text,

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================
-- 10. ESTIMATE ITEMS / BOQ ITEMS
-- ============================================================

create table if not exists estimate_items (
    id uuid primary key default uuid_generate_v4(),

    estimate_id uuid references estimates(id) on delete cascade,

    category text not null,

    description text not null,

    quantity numeric(15,3) default 0,

    unit text,

    unit_cost numeric(15,2) default 0,

    labour_cost numeric(15,2) default 0,

    material_cost numeric(15,2) default 0,

    total_cost numeric(15,2) default 0,

    ai_generated boolean default false,

    professionally_verified boolean default false,

    created_at timestamptz default now()
);

-- ============================================================
-- 11. MATERIALS / COST DATABASE
-- ============================================================

create table if not exists materials (
    id uuid primary key default uuid_generate_v4(),

    name text not null,

    category text,

    unit text not null,

    default_unit_cost numeric(15,2) default 0,

    supplier_name text,

    supplier_phone text,

    minimum_stock numeric(15,3) default 0,

    current_stock numeric(15,3) default 0,

    is_active boolean default true,

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================
-- 12. INVENTORY TRANSACTIONS
-- ============================================================

create table if not exists inventory_transactions (
    id uuid primary key default uuid_generate_v4(),

    material_id uuid references materials(id) on delete cascade,

    project_id uuid references projects(id) on delete set null,

    transaction_type text not null
        check (transaction_type in (
            'purchase',
            'usage',
            'adjustment',
            'return'
        )),

    quantity numeric(15,3) not null,

    unit_cost numeric(15,2) default 0,

    reference text,

    created_by uuid references users(id),

    created_at timestamptz default now()
);

-- ============================================================
-- 13. EXPENSES
-- ============================================================

create table if not exists expenses (
    id uuid primary key default uuid_generate_v4(),

    project_id uuid references projects(id) on delete set null,

    category text not null
        check (category in (
            'materials',
            'labour',
            'transport',
            'equipment',
            'subcontractor',
            'site',
            'administration',
            'marketing',
            'training',
            'other'
        )),

    description text not null,

    amount numeric(15,2) not null,

    expense_date date default current_date,

    payment_method text,

    receipt_url text,

    approved boolean default false,

    created_by uuid references users(id),

    created_at timestamptz default now()
);

-- ============================================================
-- 14. PAYMENTS / REVENUE
-- ============================================================

create table if not exists payments (
    id uuid primary key default uuid_generate_v4(),

    customer_id uuid references customers(id) on delete set null,

    project_id uuid references projects(id) on delete set null,

    reference text unique,

    amount numeric(15,2) not null,

    currency text default 'XAF',

    payment_type text
        check (payment_type in (
            'construction',
            'renovation',
            'design',
            'training',
            'course',
            'other'
        )),

    payment_method text,

    status text default 'pending'
        check (status in (
            'pending',
            'successful',
            'failed',
            'refunded'
        )),

    provider text,

    transaction_id text,

    paid_at timestamptz,

    created_at timestamptz default now()
);

-- ============================================================
-- 15. TRAINING COURSES
-- ============================================================

create table if not exists courses (
    id uuid primary key default uuid_generate_v4(),

    title text not null,

    description text,

    language text default 'en'
        check (language in ('en', 'fr')),

    level text
        check (level in (
            'beginner',
            'intermediate',
            'advanced'
        )),

    category text,

    software_name text,

    duration text,

    price numeric(15,2) default 0,

    training_format text
        check (training_format in (
            'in_person',
            'online',
            'recorded',
            'hybrid'
        )),

    is_digital boolean default false,

    is_active boolean default true,

    certificate_available boolean default false,

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================
-- 16. COURSE MODULES / LESSONS
-- ============================================================

create table if not exists course_lessons (
    id uuid primary key default uuid_generate_v4(),

    course_id uuid references courses(id) on delete cascade,

    title text not null,

    description text,

    lesson_order integer default 1,

    video_url text,

    duration_minutes integer,

    is_preview boolean default false,

    is_active boolean default true,

    created_at timestamptz default now()
);

-- ============================================================
-- 17. STUDENT ACCOUNTS / ENROLLMENTS
-- ============================================================

create table if not exists enrollments (
    id uuid primary key default uuid_generate_v4(),

    customer_id uuid references customers(id) on delete cascade,

    course_id uuid references courses(id) on delete cascade,

    payment_id uuid references payments(id) on delete set null,

    status text default 'active'
        check (status in (
            'pending',
            'active',
            'completed',
            'cancelled'
        )),

    enrolled_at timestamptz default now(),
    completed_at timestamptz,

    unique(customer_id, course_id)
);

-- ============================================================
-- 18. COURSE PROGRESS
-- ============================================================

create table if not exists course_progress (
    id uuid primary key default uuid_generate_v4(),

    enrollment_id uuid references enrollments(id) on delete cascade,

    lesson_id uuid references course_lessons(id) on delete cascade,

    completed boolean default false,

    progress_percent integer default 0
        check (progress_percent between 0 and 100),

    last_watched_at timestamptz,

    unique(enrollment_id, lesson_id)
);

-- ============================================================
-- 19. MARKETING CONTENT
-- ============================================================

create table if not exists marketing_content (
    id uuid primary key default uuid_generate_v4(),

    title text,

    content_text text,

    content_type text
        check (content_type in (
            'post',
            'reel',
            'short',
            'video',
            'image',
            'poster',
            'article',
            'advertisement'
        )),

    platform text,

    language text default 'en'
        check (language in ('en', 'fr')),

    media_url text,

    hashtags text,

    call_to_action text,

    status text default 'draft'
        check (status in (
            'draft',
            'approved',
            'scheduled',
            'published',
            'failed'
        )),

    scheduled_at timestamptz,

    published_at timestamptz,

    ai_generated boolean default false,

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================
-- 20. AI TASKS / COMMANDS
-- ============================================================

create table if not exists ai_tasks (
    id uuid primary key default uuid_generate_v4(),

    user_id uuid references users(id) on delete set null,

    task_type text not null,

    command text not null,

    module text,

    status text default 'pending'
        check (status in (
            'pending',
            'processing',
            'waiting_approval',
            'completed',
            'failed',
            'cancelled'
        )),

    result text,

    requires_approval boolean default false,

    approved_by uuid references users(id),

    approved_at timestamptz,

    created_at timestamptz default now(),
    completed_at timestamptz
);

-- ============================================================
-- 21. AUTOMATIONS
-- ============================================================

create table if not exists automations (
    id uuid primary key default uuid_generate_v4(),

    name text not null,

    description text,

    trigger_type text not null,

    trigger_config jsonb default '{}'::jsonb,

    action_type text not null,

    action_config jsonb default '{}'::jsonb,

    automation_level text default 'approval_required'
        check (automation_level in (
            'automatic',
            'approval_required',
            'ceo_approval'
        )),

    is_active boolean default true,

    last_run_at timestamptz,

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================
-- 22. APPOINTMENTS
-- ============================================================

create table if not exists appointments (
    id uuid primary key default uuid_generate_v4(),

    customer_id uuid references customers(id) on delete cascade,

    project_id uuid references projects(id) on delete set null,

    title text not null,

    appointment_type text,

    appointment_date timestamptz not null,

    location text,

    status text default 'scheduled'
        check (status in (
            'scheduled',
            'completed',
            'cancelled',
            'rescheduled'
        )),

    notes text,

    created_at timestamptz default now()
);

-- ============================================================
-- 23. NOTIFICATIONS
-- ============================================================

create table if not exists notifications (
    id uuid primary key default uuid_generate_v4(),

    user_id uuid references users(id) on delete cascade,

    title text not null,

    message text not null,

    notification_type text,

    priority text default 'normal'
        check (priority in (
            'low',
            'normal',
            'high',
            'critical'
        )),

    is_read boolean default false,

    created_at timestamptz default now()
);

-- ============================================================
-- 24. BUSINESS SETTINGS
-- ============================================================

create table if not exists business_settings (
    id uuid primary key default uuid_generate_v4(),

    setting_key text unique not null,

    setting_value jsonb,

    description text,

    updated_at timestamptz default now()
);

-- ============================================================
-- 25. INTEGRATIONS
-- ============================================================

create table if not exists integrations (
    id uuid primary key default uuid_generate_v4(),

    provider text not null,

    integration_type text,

    account_name text,

    account_id text,

    is_connected boolean default false,

    access_token text,

    refresh_token text,

    expires_at timestamptz,

    settings jsonb default '{}'::jsonb,

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================
-- INDEXES
-- ============================================================

create index if not exists idx_customers_phone
on customers(phone);

create index if not exists idx_customers_stage
on customers(stage);

create index if not exists idx_customers_service_interest
on customers(service_interest);

create index if not exists idx_customers_follow_up
on customers(next_follow_up_at);

create index if not exists idx_conversations_customer
on conversations(customer_id);

create index if not exists idx_messages_conversation
on messages(conversation_id);

create index if not exists idx_projects_customer
on projects(customer_id);

create index if not exists idx_projects_status
on projects(status);

create index if not exists idx_expenses_project
on expenses(project_id);

create index if not exists idx_payments_customer
on payments(customer_id);

create index if not exists idx_payments_project
on payments(project_id);

create index if not exists idx_payments_status
on payments(status);

create index if not exists idx_enrollments_customer
on enrollments(customer_id);

create index if not exists idx_marketing_status
on marketing_content(status);

create index if not exists idx_ai_tasks_status
on ai_tasks(status);

-- ============================================================
-- DEFAULT COMPANY RECORD
-- ============================================================

insert into company_profile (
    business_name,
    ceo_name,
    location,
    slogan,
    default_language,
    currency
)
select
    'TASSIMO BTP CONSTRUCTION SARL',
    'TAGNE Simo Innocant',
    'Douala – Logpom, Cameroon',
    'Together, let us build excellence.',
    'en',
    'XAF'
where not exists (
    select 1 from company_profile
);

-- ============================================================
-- DEFAULT BUSINESS SETTINGS
-- ============================================================

insert into business_settings (setting_key, setting_value, description)
values
(
    'supported_languages',
    '["en","fr"]'::jsonb,
    'Languages supported throughout the platform'
),
(
    'default_currency',
    '"XAF"'::jsonb,
    'Default business currency'
),
(
    'automation_policy',
    '"approval_required"'::jsonb,
    'Default AI automation safety level'
),
(
    'construction_estimate_policy',
    '"preliminary_professional_review_required"'::jsonb,
    'AI construction estimates require professional verification'
)
on conflict (setting_key) do nothing;

-- ============================================================
-- END OF TASSIMO DATABASE FOUNDATION
-- ============================================================
