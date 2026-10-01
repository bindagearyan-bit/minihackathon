-- 1. Grant API permissions to service_role, anon, and authenticated
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL ROUTINES IN SCHEMA public TO anon, authenticated, service_role;

-- 2. Seed 8 Departments
INSERT INTO public.departments (name, students) VALUES
('Computer', 480),
('Mechanical', 400),
('Civil', 350),
('Electrical', 380),
('E&TC', 360),
('Chemistry Lab', 120),
('Hostel & Mess', 900),
('Admin', 150)
ON CONFLICT (name) DO NOTHING;

-- 3. Seed 48 Monthly Usage History Rows
INSERT INTO public.monthly_usages (department_id, month, units_kwh, amount_inr, co2_kg) VALUES
((SELECT id FROM public.departments WHERE name = 'Computer'), '2026-05', 8500, 97750, 6035.0),
((SELECT id FROM public.departments WHERE name = 'Mechanical'), '2026-05', 7100, 81650, 5041.0),
((SELECT id FROM public.departments WHERE name = 'Civil'), '2026-05', 4750, 54625, 3372.5),
((SELECT id FROM public.departments WHERE name = 'Electrical'), '2026-05', 6850, 78775, 4863.5),
((SELECT id FROM public.departments WHERE name = 'E&TC'), '2026-05', 5350, 61525, 3798.5),
((SELECT id FROM public.departments WHERE name = 'Chemistry Lab'), '2026-05', 3100, 35650, 2201.0),
((SELECT id FROM public.departments WHERE name = 'Hostel & Mess'), '2026-05', 11100, 127650, 7881.0),
((SELECT id FROM public.departments WHERE name = 'Admin'), '2026-05', 3600, 41400, 2556.0),
((SELECT id FROM public.departments WHERE name = 'Computer'), '2026-06', 8600, 98900, 6106.0),
((SELECT id FROM public.departments WHERE name = 'Mechanical'), '2026-06', 7050, 81075, 5005.5),
((SELECT id FROM public.departments WHERE name = 'Civil'), '2026-06', 4800, 55200, 3408.0),
((SELECT id FROM public.departments WHERE name = 'Electrical'), '2026-06', 6900, 79350, 4899.0),
((SELECT id FROM public.departments WHERE name = 'E&TC'), '2026-06', 5400, 62100, 3834.0),
((SELECT id FROM public.departments WHERE name = 'Chemistry Lab'), '2026-06', 3150, 36225, 2236.5),
((SELECT id FROM public.departments WHERE name = 'Hostel & Mess'), '2026-06', 11250, 129375, 7987.5),
((SELECT id FROM public.departments WHERE name = 'Admin'), '2026-06', 3620, 41630, 2570.2),
((SELECT id FROM public.departments WHERE name = 'Computer'), '2026-07', 8900, 102350, 6319.0),
((SELECT id FROM public.departments WHERE name = 'Mechanical'), '2026-07', 7300, 83950, 5183.0),
((SELECT id FROM public.departments WHERE name = 'Civil'), '2026-07', 4900, 56350, 3479.0),
((SELECT id FROM public.departments WHERE name = 'Electrical'), '2026-07', 7000, 80500, 4970.0),
((SELECT id FROM public.departments WHERE name = 'E&TC'), '2026-07', 5500, 63250, 3905.0),
((SELECT id FROM public.departments WHERE name = 'Chemistry Lab'), '2026-07', 2906, 33419, 2063.3),
((SELECT id FROM public.departments WHERE name = 'Hostel & Mess'), '2026-07', 11400, 131100, 8094.0),
((SELECT id FROM public.departments WHERE name = 'Admin'), '2026-07', 3700, 42550, 2627.0),
((SELECT id FROM public.departments WHERE name = 'Computer'), '2026-08', 8450, 97175, 5999.5),
((SELECT id FROM public.departments WHERE name = 'Mechanical'), '2026-08', 7000, 80500, 4970.0),
((SELECT id FROM public.departments WHERE name = 'Civil'), '2026-08', 4700, 54050, 3337.0),
((SELECT id FROM public.departments WHERE name = 'Electrical'), '2026-08', 6800, 78200, 4828.0),
((SELECT id FROM public.departments WHERE name = 'E&TC'), '2026-08', 5350, 61525, 3798.5),
((SELECT id FROM public.departments WHERE name = 'Chemistry Lab'), '2026-08', 3180, 36570, 2257.8),
((SELECT id FROM public.departments WHERE name = 'Hostel & Mess'), '2026-08', 11100, 127650, 7881.0),
((SELECT id FROM public.departments WHERE name = 'Admin'), '2026-08', 3600, 41400, 2556.0),
((SELECT id FROM public.departments WHERE name = 'Computer'), '2026-09', 8750, 100625, 6212.5),
((SELECT id FROM public.departments WHERE name = 'Mechanical'), '2026-09', 7200, 82800, 5112.0),
((SELECT id FROM public.departments WHERE name = 'Civil'), '2026-09', 4850, 55775, 3443.5),
((SELECT id FROM public.departments WHERE name = 'Electrical'), '2026-09', 6950, 79925, 4934.5),
((SELECT id FROM public.departments WHERE name = 'E&TC'), '2026-09', 5450, 62675, 3869.5),
((SELECT id FROM public.departments WHERE name = 'Chemistry Lab'), '2026-09', 3454, 39721, 2452.3),
((SELECT id FROM public.departments WHERE name = 'Hostel & Mess'), '2026-09', 11300, 129950, 8023.0),
((SELECT id FROM public.departments WHERE name = 'Admin'), '2026-09', 3650, 41975, 2591.5),
((SELECT id FROM public.departments WHERE name = 'Computer'), '2026-10', 8650, 99475, 6141.5),
((SELECT id FROM public.departments WHERE name = 'Mechanical'), '2026-10', 7150, 82225, 5076.5),
((SELECT id FROM public.departments WHERE name = 'Civil'), '2026-10', 4800, 55200, 3408.0),
((SELECT id FROM public.departments WHERE name = 'Electrical'), '2026-10', 6900, 79350, 4899.0),
((SELECT id FROM public.departments WHERE name = 'E&TC'), '2026-10', 5420, 62330, 3848.2),
((SELECT id FROM public.departments WHERE name = 'Chemistry Lab'), '2026-10', 4544, 52256, 3226.2),
((SELECT id FROM public.departments WHERE name = 'Hostel & Mess'), '2026-10', 11200, 128800, 7952.0),
((SELECT id FROM public.departments WHERE name = 'Admin'), '2026-10', 3676, 42274, 2609.9);

-- 4. Seed 14 Mess Meals
INSERT INTO public.mess_meals (day, slot, meal_name, meal_type, votes) VALUES
('Monday', 'lunch', 'Poha', 'veg', 0),
('Monday', 'dinner', 'Varan Bhaat', 'veg', 0),
('Tuesday', 'lunch', 'Misal Pav', 'veg', 0),
('Tuesday', 'dinner', 'Egg Curry', 'egg', 0),
('Wednesday', 'lunch', 'Pithla Bhakri', 'veg', 0),
('Wednesday', 'dinner', 'Chicken Rassa', 'chicken', 0),
('Thursday', 'lunch', 'Veg Pulao', 'veg', 0),
('Thursday', 'dinner', 'Dal Tadka with Rice', 'veg', 0),
('Friday', 'lunch', 'Usal Pav', 'veg', 0),
('Friday', 'dinner', 'Egg Bhurji', 'egg', 0),
('Saturday', 'lunch', 'Sabudana Khichdi', 'veg', 0),
('Saturday', 'dinner', 'Mutton Thali', 'mutton', 0),
('Sunday', 'lunch', 'Puri Bhaji', 'veg', 0),
('Sunday', 'dinner', 'Chicken Biryani', 'chicken', 0);
