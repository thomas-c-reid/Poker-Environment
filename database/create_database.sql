CREATE DATABASE poker_database;

-- This might need commented out
\c poker_database;

-- AGENTS table
CREATE TABLE agents(
    id string NOT NULL,
    name string NOT NULL,
)

-- CREATE TABLE player_action(
--     -- fill with stuff
-- )