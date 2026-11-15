
-- ============================================
-- Smart Lost & Found Management Portal
-- Database Schema
-- ============================================

-- 1. Users table
-- Stores registered students and administrators.

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_no TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('student', 'admin')) DEFAULT 'student'
);

-- 2. Locations table
-- Stores campus locations and their Canvas coordinates.

CREATE TABLE IF NOT EXISTS locations (
    loc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    x_coord INTEGER NOT NULL,
    y_coord INTEGER NOT NULL
);

-- 3. Campus edges table
-- Stores undirected weighted connections between campus locations.

CREATE TABLE IF NOT EXISTS campus_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_loc_id INTEGER REFERENCES locations(loc_id),
    dst_loc_id INTEGER REFERENCES locations(loc_id),
    distance_meters REAL NOT NULL
);

-- 4. Items table
-- Stores lost and found item reports.

CREATE TABLE IF NOT EXISTS items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(user_id),
    type TEXT CHECK(type IN ('LOST', 'FOUND')) NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    serial_tag TEXT,
    loc_id INTEGER REFERENCES locations(loc_id),
    cluster_root_id INTEGER,
    item_weight INTEGER DEFAULT 1,
    priority_value INTEGER DEFAULT 10,
    deadline_hours INTEGER DEFAULT 48,
    status TEXT CHECK(status IN ('OPEN', 'MATCHED', 'CLAIMED')) DEFAULT 'OPEN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Matches table
-- Stores potential matches between lost and found items.

CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lost_item_id INTEGER REFERENCES items(item_id),
    found_item_id INTEGER REFERENCES items(item_id),
    lcs_score REAL NOT NULL,
    spatial_dist REAL NOT NULL,
    confidence_score REAL NOT NULL,
    assigned_slot INTEGER,
    status TEXT CHECK(status IN ('PENDING', 'APPROVED', 'COLLECTED')) DEFAULT 'PENDING'
);
