CREATE DATABASE pickflick;
USE pickflick;

-- Tabela de usuários
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de avaliações (sem a tabela de filmes)
CREATE TABLE ratings (
    rating_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    movie_api_id INT, -- ID do filme retornado pela API
    rating DECIMAL(2,1) CHECK (rating >= 0.0 AND rating <= 5.0),
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
