-- Create database
CREATE DATABASE sports_connect_DB;

-- Use the created database
USE sports_connect_DB;

-- Create Player table
CREATE TABLE Player (
    player_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Create Friend table
CREATE TABLE Friend (
    Friend_id INT PRIMARY KEY,
    Friend_count INT NULL,
    player_id INT NOT NULL,
    FOREIGN KEY (player_id) REFERENCES Player (player_id)
);

-- Create CenterManager table
CREATE TABLE CenterManager (
    manager_id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Create SportsCenter table
CREATE TABLE SportsCenter (
    center_id INT PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    working_hours VARCHAR(255),
    manager_id INT UNIQUE NOT NULL,
    FOREIGN KEY (manager_id) REFERENCES CenterManager (manager_id)
);

-- Create Court table
CREATE TABLE Court (
    court_id INT PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    hourly_rate DECIMAL(5,2),
    court_surface VARCHAR(255) UNIQUE NOT NULL,
    booking_status ENUM('booked', 'free') DEFAULT 'free',
    size VARCHAR(255) UNIQUE NOT NULL,
    football_flag BOOLEAN,
    basketball_flag BOOLEAN,
    volleyball_flag BOOLEAN
);

-- Create Books table
CREATE TABLE Books (
    player_id INT,
    court_id INT,
    price DECIMAL(6,2) NOT NULL,
    start_time DATETIME,
    finish_time DATETIME,
    FOREIGN KEY (player_id) REFERENCES Player(player_id),
    FOREIGN KEY (court_id) REFERENCES Court(court_id)
);

-- Create Reviews table
CREATE TABLE Reviews (
    player_id INT,
    court_id INT,
    comment TEXT,
    star_rating INT,
    PRIMARY KEY (player_id, court_id),
    FOREIGN KEY (player_id) REFERENCES Player(player_id),
    FOREIGN KEY (court_id) REFERENCES Court(court_id)
);

-- Create Team table
CREATE TABLE Team (
    team_id INT PRIMARY KEY,
    team_name VARCHAR(255) NOT NULL,
    sports_played VARCHAR(50) NOT NULL,
    game_id INT
);

-- Create Tournament table
CREATE TABLE Tournament (
    tournament_id INT PRIMARY KEY,
    team_id INT,
    tournament_date DATE,
    tournament_winner VARCHAR(255),
    FOREIGN KEY (team_id) REFERENCES Team(team_id)
);

-- Create Game table
CREATE TABLE Game (
    game_id INT PRIMARY KEY,
    tournament_id INT,
    team_id INT,
    sports_played VARCHAR(255),
    winner_team VARCHAR(255),
    score DECIMAL(5,2),
    FOREIGN KEY (tournament_id) REFERENCES Tournament (tournament_id),
    FOREIGN KEY (team_id) REFERENCES Team (team_id)
);

-- Create PlayerExperience table
CREATE TABLE PlayerExperience (
    player_id INT,
    experience_level INT,
    PRIMARY KEY (player_id, experience_level),
    FOREIGN KEY (player_id) REFERENCES Player (player_id)
);

-- Create Forms table
CREATE TABLE Forms (
    player_id INT,
    team_id INT,
    PRIMARY KEY (player_id, team_id),
    FOREIGN KEY (player_id) REFERENCES Player (player_id),
    FOREIGN KEY (team_id) REFERENCES Team (team_id)
);

-- Create Plays_In_A table
CREATE TABLE Plays_In_A (
    player_id INT,
    game_id INT,
    PRIMARY KEY (player_id, game_id),
    FOREIGN KEY (player_id) REFERENCES Player (player_id),
    FOREIGN KEY (game_id) REFERENCES Game (game_id)
);

-- Create Posts table
CREATE TABLE Posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT,
    sport VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    location VARCHAR(255) NOT NULL,
    description TEXT,
    FOREIGN KEY (player_id) REFERENCES Player(player_id)
);

-- Grant privileges to root user
GRANT ALL PRIVILEGES ON sports_connect_DB.* TO 'root'@'localhost';
SHOW GRANTS;
SHOW GRANTS FOR 'root'@'localhost';

-- Create and grant privileges to 'ahmed zendah' user
CREATE USER 'login'@'localhost' IDENTIFIED BY '1234';
GRANT select,insert ON sports_connect_DB.player TO 'login'@'localhost';
GRANT select,insert ON sports_connect_DB.centermanager TO 'login'@'localhost';
FLUSH PRIVILEGES;


-- Grant privileges to 'player' user
CREATE USER 'player'@'localhost' IDENTIFIED BY 'player1';
GRANT INSERT, UPDATE, SELECT ON sports_connect_DB.player TO 'playercourt'@'localhost';
GRANT INSERT, SELECT, DELETE ON sports_connect_DB.books TO 'player'@'localhost';
GRANT INSERT, SELECT, DELETE ON sports_connect_DB.forms TO 'player'@'localhost';
GRANT INSERT, SELECT, DELETE, UPDATE ON sports_connect_DB.forms TO 'player'@'localhost';
GRANT INSERT, SELECT, DELETE ON sports_connect_DB.posts TO 'player'@'localhost';
GRANT SELECT ON sports_connect_DB.court TO 'player'@'localhost';
GRANT SELECT, INSERT, DELETE ON sports_connect_DB.friend TO 'player'@'localhost';
GRANT SELECT, INSERT, DELETE, UPDATE ON sports_connect_DB.playerexperience TO 'player'@'localhost';
GRANT INSERT, SELECT ON sports_connect_DB.reviews TO 'player'@'localhost';
GRANT INSERT, SELECT, DELETE, UPDATE ON sports_connect_DB.team TO 'player'@'localhost';
GRANT INSERT, SELECT, DELETE, UPDATE ON sports_connect_DB.tournament TO 'player'@'localhost';
GRANT INSERT, SELECT, DELETE, UPDATE ON sports_connect_DB.plays_in_a TO 'player'@'localhost';
GRANT INSERT, SELECT, DELETE, UPDATE ON sports_connect_DB.game TO 'player'@'localhost';

-- Grant privileges to 'manager' user
CREATE USER 'manager'@'localhost' IDENTIFIED BY 'manager1';
GRANT SELECT ON sports_connect_DB.books TO 'manager'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON sports_connect_DB.court TO 'manager'@'localhost';
GRANT SELECT ON sports_connect_DB.reviews TO 'manager'@'localhost';
grant select on sports_connect_db.player to 'manager'@'localhost';
grant select,insert,update,delete on sports_connect_db.centermanager to 'manager'@'localhost';