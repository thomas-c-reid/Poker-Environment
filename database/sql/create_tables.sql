
-- AGENTS table
CREATE TYPE action_enum AS ENUM (
    'CHECK',
    'FOLD',
    'BET', 
    'CALL', 
    'RAISE', 
    'BIG_BLIND', 
    'SMALL_BLIND'
);

CREATE TYPE hand_value AS ENUM (
    'HIGH_CARD',
    'ONE_PAIR',
    'TWO_PAIR',
    'THREE_OF_A_KIND',
    'STRAIGHT',
    'FLUSH',
    'FULL_HOUSE',
    'FOUR_OF_A_KIND',
    'STRAIGHT_FLUSH',
    'ROYAL_FLUSH'
);

CREATE TABLE tbl_agents(
    id VARCHAR(8) PRIMARY KEY, -- This should be the primary Key for the table
    name VARCHAR(255) NOT NULL,
    initial_bankroll INT NOT NULL,
    total_bet INT DEFAULT 0,
    total_won INT DEFAULT 0,
    in_play BOOL DEFAULT TRUE
);


CREATE TABLE tbl_rounds (
    id SERIAL PRIMARY KEY,
    table_cards TEXT[], -- Array of text values
    round_duration INTERVAL
);

CREATE TABLE tbl_actions(
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(8) NOT NULL REFERENCES tbl_agents(id), -- Needs to be foreign key for above table
    action_type action_enum NOT NULL, -- There is an enum class i have and I want it to be a string with the options (CALL, RAISE, FOLD, CHECK) use appropriate amount of space
    round INT NOT NULL REFERENCES tbl_rounds(id),
    amount FLOAT NOT NULL DEFAULT 0.0, 
    all_in_flag BOOL DEFAULT FALSE
);

CREATE TABLE tbl_results(
    id SERIAL PRIMARY KEY,
    round INT REFERENCES tbl_rounds(id),
    player_id VARCHAR(8) NOT NULL REFERENCES tbl_agents(id),
    amount_won FLOAT NOT NULL DEFAULT 0.0,
    amount_bet FLOAT NOT NULL DEFAULT 0.0,
    reward INT NOT NULL,
    final_hand_value hand_value NOT NULL
)
