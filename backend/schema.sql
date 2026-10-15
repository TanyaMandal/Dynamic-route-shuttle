-- Supabase / PostgreSQL Schema for Dynamic Employee Shuttle Routing System
-- PRD MCA Minor Project

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'employee' CHECK (role IN ('employee', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Shuttles Table
CREATE TABLE IF NOT EXISTS shuttles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    seat_capacity INTEGER NOT NULL CHECK (seat_capacity > 0),
    start_location_name VARCHAR(150) NOT NULL,
    start_lat DOUBLE PRECISION NOT NULL,
    start_lng DOUBLE PRECISION NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'broken', 'maintenance')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Pickup Requests Table
CREATE TABLE IF NOT EXISTS pickup_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    employee_name VARCHAR(255) NOT NULL,
    pickup_lat DOUBLE PRECISION NOT NULL,
    pickup_lng DOUBLE PRECISION NOT NULL,
    destination VARCHAR(255) NOT NULL DEFAULT 'Central Tech Park Campus',
    dest_lat DOUBLE PRECISION NOT NULL DEFAULT 12.9716,
    dest_lng DOUBLE PRECISION NOT NULL DEFAULT 77.5946,
    arrival_deadline TIME NOT NULL, -- e.g. 09:00:00
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'unserved', 'cancelled')),
    unserved_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Plans Table
CREATE TABLE IF NOT EXISTS plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'finalized' CHECK (status IN ('draft', 'finalized', 'disrupted')),
    total_shuttles_used INTEGER NOT NULL DEFAULT 0,
    total_distance_km DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    total_travel_time_min DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    avg_waiting_time_min DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    vehicle_utilization_pct DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    avg_walking_distance_m DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    deadline_compliance_pct DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    unserved_requests_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Routes Table
CREATE TABLE IF NOT EXISTS routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id UUID REFERENCES plans(id) ON DELETE CASCADE,
    shuttle_id UUID REFERENCES shuttles(id) ON DELETE CASCADE,
    shuttle_name VARCHAR(100) NOT NULL,
    total_distance_km DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    total_duration_min DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    assigned_passengers_count INTEGER NOT NULL DEFAULT 0,
    capacity INTEGER NOT NULL DEFAULT 12,
    route_polyline JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. Route Stops Table
CREATE TABLE IF NOT EXISTS route_stops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_id UUID REFERENCES routes(id) ON DELETE CASCADE,
    sequence_num INTEGER NOT NULL,
    stop_name VARCHAR(255) NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    estimated_arrival_time VARCHAR(20) NOT NULL,
    passenger_count INTEGER NOT NULL DEFAULT 0,
    passenger_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    passenger_details JSONB NOT NULL DEFAULT '[]'::jsonb
);

-- 7. Disruptions Table
CREATE TABLE IF NOT EXISTS disruptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    disruption_type VARCHAR(50) NOT NULL CHECK (disruption_type IN ('road_closure', 'shuttle_breakdown')),
    description TEXT NOT NULL,
    affected_entity_id VARCHAR(255) NOT NULL, -- e.g. edge node pair or shuttle_id
    plan_id UUID REFERENCES plans(id) ON DELETE CASCADE,
    extra_distance_km DOUBLE PRECISION DEFAULT 0.0,
    extra_delay_min DOUBLE PRECISION DEFAULT 0.0,
    passengers_reassigned_count INTEGER DEFAULT 0,
    passengers_unserved_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 8. Plan Comparisons (Optimised vs Baseline)
CREATE TABLE IF NOT EXISTS plan_comparisons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id UUID REFERENCES plans(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    baseline_value DOUBLE PRECISION NOT NULL,
    optimised_value DOUBLE PRECISION NOT NULL,
    improvement_pct DOUBLE PRECISION NOT NULL,
    target_direction VARCHAR(20) NOT NULL -- 'lower' or 'higher'
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_requests_status ON pickup_requests(status);
CREATE INDEX IF NOT EXISTS idx_shuttles_status ON shuttles(status);
CREATE INDEX IF NOT EXISTS idx_routes_plan_id ON routes(plan_id);
CREATE INDEX IF NOT EXISTS idx_route_stops_route_id ON route_stops(route_id);
