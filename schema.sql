-- schema.sql
CREATE DATABASE IF NOT EXISTS railway_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE railway_db;

-- Users (passengers + admins)
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(150),
  phone VARCHAR(20),
  is_admin BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trains
CREATE TABLE trains (
  id INT AUTO_INCREMENT PRIMARY KEY,
  train_no VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(150) NOT NULL,
  source VARCHAR(100) NOT NULL,
  destination VARCHAR(100) NOT NULL,
  route TEXT, -- JSON or comma-separated stops with times
  total_seats INT NOT NULL DEFAULT 0,
  classes_json JSON DEFAULT NULL, -- e.g. {"SL":100,"3A":20,"2A":10}
  fare_json JSON DEFAULT NULL, -- e.g. {"SL":150,"3A":750}
  schedule_json JSON DEFAULT NULL, -- dates/times or weekly timings
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bookings
CREATE TABLE bookings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  pnr VARCHAR(30) UNIQUE NOT NULL,
  user_id INT NOT NULL,
  train_id INT NOT NULL,
  travel_date DATE NOT NULL,
  class VARCHAR(10) NOT NULL,
  seat_count INT NOT NULL,
  fare_per_seat DECIMAL(10,2) NOT NULL,
  total_fare DECIMAL(10,2) NOT NULL,
  status ENUM('CONFIRMED','CANCELLED','RAC','WL') DEFAULT 'CONFIRMED',
  payment_status ENUM('PAID','REFUNDED','PENDING') DEFAULT 'PENDING',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (train_id) REFERENCES trains(id) ON DELETE CASCADE
);

-- Seat availability per train per date per class
CREATE TABLE seat_availability (
  id INT AUTO_INCREMENT PRIMARY KEY,
  train_id INT NOT NULL,
  travel_date DATE NOT NULL,
  class VARCHAR(10) NOT NULL,
  seats_left INT NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY train_date_class (train_id, travel_date, class),
  FOREIGN KEY (train_id) REFERENCES trains(id) ON DELETE CASCADE
);

-- Payments
CREATE TABLE payments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  booking_id INT NOT NULL,
  provider VARCHAR(50),
  provider_payment_id VARCHAR(100),
  amount DECIMAL(10,2) NOT NULL,
  currency VARCHAR(10) DEFAULT 'INR',
  status ENUM('SUCCESS','FAILED','REFUNDED','PENDING') DEFAULT 'PENDING',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

-- Admin logs / reports (optional)
CREATE TABLE daily_reports (
  id INT AUTO_INCREMENT PRIMARY KEY,
  report_date DATE NOT NULL,
  total_bookings INT DEFAULT 0,
  total_revenue DECIMAL(12,2) DEFAULT 0.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);