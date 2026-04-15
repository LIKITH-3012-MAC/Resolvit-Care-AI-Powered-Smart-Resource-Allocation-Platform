-- ============================================
-- Smart Resource Allocation — Seed Data
-- ============================================

-- Admin user (password: Admin@123456)
INSERT INTO users (id, email, name, password_hash, email_verified, role, status) VALUES
('a0000000-0000-0000-0000-000000000001', 'admin@smartresource.org', 'System Admin', '$2b$10$rICGmJqXiFQvYqFpOT5cAeVJGqKjKz5L7bPzYbZkV8pM7qHJ9wB2e', true, 'admin', 'active');

-- Coordinators
INSERT INTO users (id, email, name, password_hash, email_verified, role) VALUES
('c0000000-0000-0000-0000-000000000001', 'priya.coordinator@ngo.org', 'Priya Sharma', '$2b$10$rICGmJqXiFQvYqFpOT5cAeVJGqKjKz5L7bPzYbZkV8pM7qHJ9wB2e', true, 'coordinator'),
('c0000000-0000-0000-0000-000000000002', 'ramesh.field@ngo.org', 'Ramesh Kumar', '$2b$10$rICGmJqXiFQvYqFpOT5cAeVJGqKjKz5L7bPzYbZkV8pM7qHJ9wB2e', true, 'coordinator');

-- Volunteers
INSERT INTO users (id, email, name, password_hash, email_verified, role) VALUES
('v0000000-0000-0000-0000-000000000001', 'anita.vol@gmail.com', 'Anita Devi', '$2b$10$rICGmJqXiFQvYqFpOT5cAeVJGqKjKz5L7bPzYbZkV8pM7qHJ9wB2e', true, 'volunteer'),
('v0000000-0000-0000-0000-000000000002', 'suresh.med@gmail.com', 'Dr. Suresh Reddy', '$2b$10$rICGmJqXiFQvYqFpOT5cAeVJGqKjKz5L7bPzYbZkV8pM7qHJ9wB2e', true, 'volunteer'),
('v0000000-0000-0000-0000-000000000003', 'kavitha.teach@gmail.com', 'Kavitha Nair', '$2b$10$rICGmJqXiFQvYqFpOT5cAeVJGqKjKz5L7bPzYbZkV8pM7qHJ9wB2e', true, 'volunteer'),
('v0000000-0000-0000-0000-000000000004', 'vijay.log@gmail.com', 'Vijay Patel', '$2b$10$rICGmJqXiFQvYqFpOT5cAeVJGqKjKz5L7bPzYbZkV8pM7qHJ9wB2e', true, 'volunteer'),
('v0000000-0000-0000-0000-000000000005', 'meera.emr@gmail.com', 'Meera Iyer', '$2b$10$rICGmJqXiFQvYqFpOT5cAeVJGqKjKz5L7bPzYbZkV8pM7qHJ9wB2e', true, 'volunteer'),
('v0000000-0000-0000-0000-000000000006', 'raju.food@gmail.com', 'Raju Yadav', '$2b$10$rICGmJqXiFQvYqFpOT5cAeVJGqKjKz5L7bPzYbZkV8pM7qHJ9wB2e', true, 'volunteer');

-- Reporters
INSERT INTO users (id, email, name, password_hash, email_verified, role) VALUES
('r0000000-0000-0000-0000-000000000001', 'village.leader@gmail.com', 'Srinivas Goud', '$2b$10$rICGmJqXiFQvYqFpOT5cAeVJGqKjKz5L7bPzYbZkV8pM7qHJ9wB2e', true, 'reporter'),
('r0000000-0000-0000-0000-000000000002', 'citizen.reporter@gmail.com', 'Lakshmi Bai', '$2b$10$rICGmJqXiFQvYqFpOT5cAeVJGqKjKz5L7bPzYbZkV8pM7qHJ9wB2e', true, 'reporter');

-- Locations (Hyderabad area)
INSERT INTO locations (id, name, district, ward, state, latitude, longitude, risk_index) VALUES
('l0000000-0000-0000-0000-000000000001', 'Kukatpally Ward 7', 'Hyderabad', 'Ward 7', 'Telangana', 17.4947, 78.3996, 0.72),
('l0000000-0000-0000-0000-000000000002', 'Secunderabad Old City', 'Hyderabad', 'Ward 12', 'Telangana', 17.4399, 78.4983, 0.58),
('l0000000-0000-0000-0000-000000000003', 'LB Nagar Colony', 'Hyderabad', 'Ward 23', 'Telangana', 17.3457, 78.5522, 0.45),
('l0000000-0000-0000-0000-000000000004', 'Medchal Village', 'Medchal-Malkajgiri', 'Ward 3', 'Telangana', 17.6297, 78.4817, 0.81),
('l0000000-0000-0000-0000-000000000005', 'Chandrayangutta', 'Hyderabad', 'Ward 18', 'Telangana', 17.3340, 78.5040, 0.67),
('l0000000-0000-0000-0000-000000000006', 'Shamshabad Rural', 'Rangareddy', 'Ward 1', 'Telangana', 17.2473, 78.4263, 0.89);

-- Volunteer profiles
INSERT INTO volunteers (user_id, skill_tags, languages, availability, latitude, longitude, reliability_score, total_tasks_completed, travel_radius_km, transport_access, gender) VALUES
('v0000000-0000-0000-0000-000000000001', ARRAY['food_distribution', 'logistics', 'community_outreach'], ARRAY['Telugu', 'Hindi', 'English'], 'available', 17.4950, 78.3990, 78, 42, 15, 'two_wheeler', 'female'),
('v0000000-0000-0000-0000-000000000002', ARRAY['medical', 'first_aid', 'health_camp', 'vaccination'], ARRAY['Telugu', 'English'], 'available', 17.4400, 78.4980, 92, 87, 25, 'car', 'male'),
('v0000000-0000-0000-0000-000000000003', ARRAY['teaching', 'education', 'child_welfare', 'counseling'], ARRAY['Malayalam', 'English', 'Hindi'], 'available', 17.3460, 78.5520, 85, 63, 10, 'public_transport', 'female'),
('v0000000-0000-0000-0000-000000000004', ARRAY['logistics', 'transport', 'warehouse', 'food_distribution'], ARRAY['Gujarati', 'Hindi', 'English'], 'available', 17.6300, 78.4820, 71, 35, 30, 'truck', 'male'),
('v0000000-0000-0000-0000-000000000005', ARRAY['emergency_response', 'first_aid', 'women_support', 'counseling'], ARRAY['Tamil', 'English', 'Telugu'], 'busy', 17.3345, 78.5045, 95, 112, 20, 'car', 'female'),
('v0000000-0000-0000-0000-000000000006', ARRAY['food_distribution', 'cooking', 'logistics'], ARRAY['Telugu', 'Hindi'], 'available', 17.2478, 78.4268, 65, 28, 12, 'two_wheeler', 'male');

-- Community reports
INSERT INTO community_reports (id, title, description, category, subcategory, severity, urgency_score, priority_level, people_affected, vulnerable_group, source_type, reporter_id, location_id, latitude, longitude, verification_status, ai_classification, ai_priority_explanation) VALUES
('rp000000-0000-0000-0000-000000000001', 'Urgent food shortage in Ward 7', 'Three families in Ward 7 have not received food supplies for 5 days. One elderly person is diabetic and needs special diet. Children are malnourished.', 'food_support', 'food_shortage', 9, 84.5, 'critical', 15, 'elderly, children', 'field_report', 'r0000000-0000-0000-0000-000000000001', 'l0000000-0000-0000-0000-000000000001', 17.4947, 78.3996, 'verified', '{"primary": "food_support", "confidence": 0.94, "secondary": "medical_support"}', 'Marked CRITICAL: 15 people affected including elderly diabetic patient and malnourished children. No support for 5 days. High severity (9/10).'),

('rp000000-0000-0000-0000-000000000002', 'Medical camp needed in Old City', 'Over 30 residents in Secunderabad Old City area suffering from seasonal fever. No nearby health facility. Need mobile health camp urgently.', 'medical_emergency', 'health_camp_needed', 8, 76.2, 'critical', 30, 'elderly, children', 'web_form', 'r0000000-0000-0000-0000-000000000002', 'l0000000-0000-0000-0000-000000000002', 17.4399, 78.4983, 'verified', '{"primary": "medical_emergency", "confidence": 0.91, "secondary": "health_camp"}', 'Marked CRITICAL: 30 people affected with seasonal illness. No nearby health facility. Time-sensitive health emergency.'),

('rp000000-0000-0000-0000-000000000003', 'School supplies needed for 20 children', 'Village school in LB Nagar has 20 students without basic supplies - books, uniforms, bags. Children might drop out.', 'education_support', 'school_supplies', 5, 48.3, 'medium', 20, 'children', 'mobile_app', 'r0000000-0000-0000-0000-000000000001', 'l0000000-0000-0000-0000-000000000003', 17.3457, 78.5522, 'verified', '{"primary": "education_support", "confidence": 0.88}', 'Medium priority: 20 children affected but not life-threatening. Risk of school dropout if unaddressed.'),

('rp000000-0000-0000-0000-000000000004', 'Flooding in Medchal — families displaced', 'Heavy rain caused flooding in low-lying areas. 8 families displaced, need temporary shelter and clean water. Roads blocked.', 'disaster_relief', 'flood_displacement', 10, 92.7, 'critical', 40, 'families, children, elderly', 'phone_call', 'r0000000-0000-0000-0000-000000000002', 'l0000000-0000-0000-0000-000000000004', 17.6297, 78.4817, 'verified', '{"primary": "disaster_relief", "confidence": 0.97, "secondary": "shelter_need"}', 'EMERGENCY: 40 people displaced by flooding. Includes families with children and elderly. Roads blocked limiting access. Maximum urgency.'),

('rp000000-0000-0000-0000-000000000005', 'Women safety concern at night', 'Streetlights broken in Chandrayangutta colony. Women feel unsafe walking at night. Multiple harassment reports.', 'women_safety', 'infrastructure_safety', 7, 62.1, 'high', 50, 'women', 'whatsapp', 'r0000000-0000-0000-0000-000000000001', 'l0000000-0000-0000-0000-000000000005', 17.3340, 78.5040, 'pending', '{"primary": "women_safety", "confidence": 0.86, "secondary": "infrastructure"}', 'High priority: Safety concern affecting 50+ women. Broken infrastructure creating unsafe conditions. Multiple reports confirm issue.'),

('rp000000-0000-0000-0000-000000000006', 'Medicine delivery for 5 bedridden patients', 'Five elderly bedridden patients in Shamshabad need monthly medicine delivery. Family members unable to travel to city pharmacy.', 'medical_support', 'medicine_delivery', 6, 55.8, 'high', 5, 'elderly, bedridden', 'field_report', 'r0000000-0000-0000-0000-000000000002', 'l0000000-0000-0000-0000-000000000006', 17.2473, 78.4263, 'verified', '{"primary": "medical_support", "confidence": 0.92}', 'High priority: 5 bedridden elderly patients without access to medicines. Ongoing need requiring regular support.');

-- Tasks
INSERT INTO tasks (id, report_id, assigned_volunteer_id, assigned_by, task_type, title, description, status, priority_level, priority_score, ai_match_explanation, ai_match_score) VALUES
('t0000000-0000-0000-0000-000000000001', 'rp000000-0000-0000-0000-000000000001', (SELECT id FROM volunteers WHERE user_id='v0000000-0000-0000-0000-000000000001'), 'a0000000-0000-0000-0000-000000000001', 'food_distribution', 'Deliver food kits to Ward 7 families', 'Deliver emergency food kits to 3 families. Include diabetic-friendly items for elderly person.', 'in_progress', 'critical', 84.5, 'Assigned to Anita Devi: food_distribution skill match, 0.2km proximity, Telugu language support, 78% reliability, currently available.', 0.91),

('t0000000-0000-0000-0000-000000000002', 'rp000000-0000-0000-0000-000000000002', (SELECT id FROM volunteers WHERE user_id='v0000000-0000-0000-0000-000000000002'), 'c0000000-0000-0000-0000-000000000001', 'health_camp', 'Organize mobile health camp in Old City', 'Set up mobile health camp for fever outbreak. Need basic medicines, ORS, paracetamol supplies.', 'assigned', 'critical', 76.2, 'Assigned to Dr. Suresh Reddy: medical + health_camp skills, 0.1km proximity, highest reliability (92%), car access for equipment transport.', 0.95),

('t0000000-0000-0000-0000-000000000003', 'rp000000-0000-0000-0000-000000000004', (SELECT id FROM volunteers WHERE user_id='v0000000-0000-0000-0000-000000000004'), 'a0000000-0000-0000-0000-000000000001', 'disaster_response', 'Emergency shelter setup for flood victims', 'Coordinate shelter arrangement for 8 displaced families. Transport blankets, water, and essential supplies.', 'acknowledged', 'critical', 92.7, 'Assigned to Vijay Patel: logistics + transport skills, truck access (critical for blocked roads), 30km travel radius covers area.', 0.88);

-- Resources
INSERT INTO resource_inventory (name, type, quantity, unit, warehouse_location, warehouse_latitude, warehouse_longitude, availability_status) VALUES
('Emergency Food Kit', 'food', 150, 'kits', 'Central Warehouse, Kukatpally', 17.4850, 78.3950, 'available'),
('Basic Medicine Pack', 'medicine', 200, 'packs', 'Health Center, Secunderabad', 17.4350, 78.5000, 'available'),
('Sanitary Kit', 'hygiene', 80, 'kits', 'Central Warehouse, Kukatpally', 17.4850, 78.3950, 'available'),
('Emergency Blanket', 'shelter', 300, 'pieces', 'Disaster Relief Store, Medchal', 17.6200, 78.4750, 'available'),
('Water Purification Tablets', 'water', 500, 'strips', 'Health Center, Secunderabad', 17.4350, 78.5000, 'available'),
('School Supply Kit', 'education', 100, 'kits', 'NGO Office, LB Nagar', 17.3500, 78.5500, 'available'),
('Temporary Shelter Tent', 'shelter', 25, 'units', 'Disaster Relief Store, Medchal', 17.6200, 78.4750, 'available'),
('First Aid Box', 'medical', 50, 'boxes', 'Health Center, Secunderabad', 17.4350, 78.5000, 'available');

-- Impact records for completed/in-progress tasks
INSERT INTO impact_records (task_id, report_id, volunteer_id, beneficiaries_served, time_to_resolve_hours, resource_cost, notes) VALUES
('t0000000-0000-0000-0000-000000000001', 'rp000000-0000-0000-0000-000000000001', (SELECT id FROM volunteers WHERE user_id='v0000000-0000-0000-0000-000000000001'), 15, 4.5, 2500, 'Food kits delivered successfully. Diabetic-specific items included.');

-- Notifications
INSERT INTO notifications (user_id, title, message, type) VALUES
('v0000000-0000-0000-0000-000000000001', 'New Task Assigned', 'You have been assigned to deliver food kits to Ward 7. Priority: CRITICAL', 'assignment'),
('v0000000-0000-0000-0000-000000000002', 'New Task Assigned', 'You have been assigned to organize a health camp in Old City. Priority: CRITICAL', 'assignment'),
('a0000000-0000-0000-0000-000000000001', 'Critical Alert', 'Flooding in Medchal has displaced 40 people. Emergency response initiated.', 'critical'),
('c0000000-0000-0000-0000-000000000001', 'Pending Verification', '2 new community reports require your verification.', 'info');
