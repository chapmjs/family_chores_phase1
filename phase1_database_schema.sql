-- Family Chores App - Phase 1 Database Schema
-- MySQL Database Schema

-- Create database
CREATE DATABASE IF NOT EXISTS family_chores;
USE family_chores;

-- People/Family Members Table
CREATE TABLE people (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chores Master List Table
CREATE TABLE chores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room VARCHAR(50) NOT NULL,
    task VARCHAR(100) NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    estimated_time INT NOT NULL COMMENT 'Estimated time in minutes',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_chore (room, task)
);

-- Daily Chore Assignments Table
CREATE TABLE assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chore_id INT NOT NULL,
    person_id INT NOT NULL,
    assigned_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chore_id) REFERENCES chores(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE,
    UNIQUE KEY unique_assignment (chore_id, assigned_date)
);

-- Chore Completions Table
CREATE TABLE completions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT NOT NULL,
    completed_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actual_minutes INT,
    photo_filename VARCHAR(255),
    notes TEXT,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE
);

-- Insert family members
INSERT INTO people (name) VALUES
    ('Dad'),
    ('Mom'),
    ('Elisa'),
    ('Rebekah'),
    ('Sarah'),
    ('Sophia'),
    ('Moriah'),
    ('Sharon'),
    ('Julia');

-- Insert all chores from the list
INSERT INTO chores (room, task, frequency, estimated_time) VALUES
    ('Bedroom', 'Make bed', 'Daily', 5),
    ('Bedroom', 'Clean off desk', 'Daily', 5),
    ('Entry', 'Sweep or vacuum floor', 'Daily', 10),
    ('Entry', 'Organize Closet', 'Daily', 10),
    ('Entry', 'Wipe windows', 'Daily', 10),
    ('Garage', 'Bikes/Shop area', 'Daily', 20),
    ('Kitchen', 'Rinse Dishes', 'Daily', 20),
    ('Kitchen', 'Load Dishes', 'Daily', 20),
    ('Kitchen', 'Put away Dishes', 'Daily', 20),
    ('Kitchen', 'Pots & Pans', 'Daily', 20),
    ('Kitchen', 'Clear Table', 'Daily', 20),
    ('Kitchen', 'Sweep floor', 'Daily', 20),
    ('Kitchen', 'Clean counters', 'Daily', 20),
    ('Kitchen', 'Put away left overs', 'Daily', 20),
    ('Kitchen', 'Pantry', 'Daily', 15),
    ('Kitchen', 'Take out trash', 'Daily', 5),
    ('Kitchen', 'Breakfast meal prep', 'Daily', 45),
    ('Kitchen', 'Lunch meal prep', 'Daily', 30),
    ('Kitchen', 'Dinner meal prep', 'Daily', 45),
    ('Living Room', 'Clean couches', 'Daily', 10),
    ('Living Room', 'Vacuum floor', 'Daily', 15),
    ('Living Room', 'Dust', 'Daily', 5),
    ('Garage', 'Update 72-hr kits', 'Semi-annually', 30),
    ('Yard', 'Sprinkler system', 'Annual', 300),
    ('Yard', 'Aerate, seed, weed lawn', 'Annual', 180),
    ('Yard', 'Mow Front Lawn', 'Summer-weekly', 45),
    ('Yard', 'Mow Back Lawn', 'Summer-weekly', 60),
    ('Yard', 'Edge lawn', 'Summer-weekly', 45),
    ('Bathroom - Downstairs', 'Clean sink', 'Weekly', 10),
    ('Bathroom - Downstairs', 'Clean toilet', 'Weekly', 10),
    ('Bathroom - Downstairs', 'Wash shower/tub', 'Weekly', 25),
    ('Bathroom - Downstairs', 'Sweep floor', 'Weekly', 5),
    ('Bathroom - Downstairs', 'Take out trash', 'Weekly', 5),
    ('Bathroom - Downstairs', 'Wipe mirror', 'Weekly', 10),
    ('Bathroom - Upstairs', 'Clean sink', 'Weekly', 10),
    ('Bathroom - Upstairs', 'Clean toilet', 'Weekly', 10),
    ('Bathroom - Upstairs', 'Wash shower/tub', 'Weekly', 25),
    ('Bathroom - Upstairs', 'Sweep floor', 'Weekly', 5),
    ('Bathroom - Upstairs', 'Take out trash', 'Weekly', 5),
    ('Bathroom - Upstairs', 'Wipe mirror', 'Weekly', 10),
    ('Bedroom', 'Change sheets', 'Weekly', 15),
    ('Bedroom', 'Vacuum floor', 'Weekly', 15),
    ('Bedroom', 'Wipe windows', 'Weekly', 10),
    ('Cold Storage', 'Organize shelves', 'Weekly', 10),
    ('Cold Storage', 'Clean off floor', 'Weekly', 5),
    ('Family Room', 'Wipe windows', 'Weekly', 20),
    ('Family Room', 'Vacuum floor', 'Weekly', 20),
    ('Family Room', 'Dust', 'Weekly', 10),
    ('Garage', 'Clean out Prius', 'Weekly', 30),
    ('Garage', 'Vacuum Prius', 'Weekly', 30),
    ('Garage', 'Clean out Suburban', 'Weekly', 30),
    ('Garage', 'Vacuum Suburban', 'Weekly', 30),
    ('Garage', 'Clean out Buick', 'Weekly', 30),
    ('Garage', 'Vacuum Buick', 'Weekly', 30),
    ('Garage', 'Clean out Honda', 'Weekly', 30),
    ('Garage', 'Vacuum Honda', 'Weekly', 30),
    ('Garage', 'Organize bikes', 'Weekly', 10),
    ('Garage', 'Organize loft storage', 'Weekly', 15),
    ('Garage', 'Put trash on curb', 'Weekly', 5),
    ('Kitchen', 'Mop floor', 'Weekly', 30),
    ('Kitchen', 'Clean stove', 'Weekly', 15),
    ('Kitchen', 'Clean oven', 'Weekly', 15),
    ('Kitchen', 'Wipe down cabinets', 'Weekly', 10),
    ('Laundry', 'Wash a load', 'Weekly', 10),
    ('Laundry', 'Dry a load', 'Weekly', 10),
    ('Laundry', 'Fold a load', 'Weekly', 20),
    ('Laundry', 'Organize closet', 'Weekly', 30),
    ('Utility/Dad''s Office', 'Take out trash', 'Weekly', 5),
    ('Yard', 'clean trampoline area', 'Weekly', 20);

-- Indexes for performance
CREATE INDEX idx_assignments_date ON assignments(assigned_date);
CREATE INDEX idx_completions_datetime ON completions(completed_datetime);
CREATE INDEX idx_chores_room ON chores(room);
CREATE INDEX idx_chores_frequency ON chores(frequency);
