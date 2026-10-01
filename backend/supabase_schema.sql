-- ====================================================================
-- Campus Carbon Footprint Auditor (UN SDG 13: Climate Action)
-- Supabase PostgreSQL Database Schema
-- Project ID: kttqcugrqroesetwkieb (Region: ap-south-1)
-- ====================================================================

-- 1. Departments Table
CREATE TABLE IF NOT EXISTS public.departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    students INTEGER NOT NULL DEFAULT 100
);

-- 2. Monthly Electricity Usage History Table (Charts, Leaderboard, Anomalies)
CREATE TABLE IF NOT EXISTS public.monthly_usages (
    id SERIAL PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES public.departments(id) ON DELETE CASCADE,
    month VARCHAR(10) NOT NULL,          -- Format: 'YYYY-MM', e.g., '2026-10'
    units_kwh DOUBLE PRECISION NOT NULL,  -- Electricity in kWh
    amount_inr DOUBLE PRECISION NOT NULL, -- Total bill cost in ₹
    co2_kg DOUBLE PRECISION NOT NULL      -- Carbon footprint in kg CO2
);

-- 3. Scanned Bills Table (OCR Bills uploaded by users)
CREATE TABLE IF NOT EXISTS public.bills (
    id SERIAL PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES public.departments(id) ON DELETE CASCADE,
    bill_month VARCHAR(50) NOT NULL,      -- Example: 'September 2026'
    units_kwh DOUBLE PRECISION NOT NULL,
    amount_inr DOUBLE PRECISION NOT NULL,
    co2_kg DOUBLE PRECISION NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    raw_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Hostel Mess Meals Table (Weekly Menu & Carbon Scores)
CREATE TABLE IF NOT EXISTS public.mess_meals (
    id SERIAL PRIMARY KEY,
    day VARCHAR(20) NOT NULL,            -- Monday - Sunday
    slot VARCHAR(20) NOT NULL,           -- lunch / dinner
    meal_name VARCHAR(100) NOT NULL,     -- e.g., 'Varan Bhaat', 'Mutton Thali'
    meal_type VARCHAR(20) NOT NULL,      -- veg, egg, chicken, mutton
    votes INTEGER DEFAULT 0              -- Green Day pledge votes
);

-- Indexes for high-speed queries on dashboard overview & leaderboard
CREATE INDEX IF NOT EXISTS idx_monthly_usages_month ON public.monthly_usages(month);
CREATE INDEX IF NOT EXISTS idx_monthly_usages_dept ON public.monthly_usages(department_id);
CREATE INDEX IF NOT EXISTS idx_bills_dept ON public.bills(department_id);
CREATE INDEX IF NOT EXISTS idx_mess_meals_day ON public.mess_meals(day);

-- Enable Row Level Security (RLS) and allow public read/write for hackathon demo
ALTER TABLE public.departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.monthly_usages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mess_meals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to departments" ON public.departments FOR SELECT USING (true);
CREATE POLICY "Allow public insert to departments" ON public.departments FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read access to monthly_usages" ON public.monthly_usages FOR SELECT USING (true);
CREATE POLICY "Allow public insert to monthly_usages" ON public.monthly_usages FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read access to bills" ON public.bills FOR SELECT USING (true);
CREATE POLICY "Allow public insert to bills" ON public.bills FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read access to mess_meals" ON public.mess_meals FOR SELECT USING (true);
CREATE POLICY "Allow public insert/update to mess_meals" ON public.mess_meals FOR ALL USING (true);
