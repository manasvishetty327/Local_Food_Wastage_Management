CREATE DATABASE IF NOT EXISTS food_wastage_db2;
USE food_wastage_db2;

-- =====================================================
-- 2️⃣ Create Providers table
-- Stores all food providers with their details
-- =====================================================
CREATE TABLE Providers (
    Provider_ID INT PRIMARY KEY,        -- Unique ID for each provider
    Name VARCHAR(100),                  -- Provider's name
    Provider_Type VARCHAR(50),          -- Type/category of provider (matches CSV)
    Address VARCHAR(200),               -- Provider's address
    City VARCHAR(50),                   -- City of the provider
    Contact VARCHAR(100)                -- Contact number (up to 100 chars)
);

-- =====================================================
-- 3️⃣ Create Receivers table
-- Stores all receivers who claim food
-- =====================================================
CREATE TABLE Receivers (
    Receiver_ID INT PRIMARY KEY,        -- Unique ID for each receiver
    Name VARCHAR(100),                  -- Receiver's name
    Provider_Type VARCHAR(50),          -- Type/category of receiver (matches CSV)
    City VARCHAR(50),                   -- City of the receiver
    Contact VARCHAR(100)                -- Contact number
);

-- =====================================================
-- 4️⃣ Create Food_Listings table
-- Stores all food items listed by providers
-- =====================================================
CREATE TABLE Food_Listings (
    Food_ID INT PRIMARY KEY AUTO_INCREMENT,  -- Unique ID for each food listing
    Food_Name VARCHAR(100),                  -- Name of the food item
    Quantity INT,                            -- Quantity available
    Expiry_Date DATE,                        -- Expiry date of the food
    Provider_ID INT,                         -- References the provider who listed the food
    Provider_Type VARCHAR(50),               -- Type of the provider (matches CSV)
    Location VARCHAR(50),                    -- Location/city of the food
    Food_Type VARCHAR(50),                   -- Type of food (e.g., vegetarian, non-veg)
    Meal_Type VARCHAR(50),                   -- Meal type (Breakfast, Lunch, Dinner)
    FOREIGN KEY (Provider_ID) REFERENCES Providers(Provider_ID)
);

-- =====================================================
-- 5️⃣ Create Claims table
-- Tracks which receiver claimed which food and the status
-- =====================================================
CREATE TABLE Claims (
    Claim_ID INT PRIMARY KEY AUTO_INCREMENT, -- Unique ID for each claim
    Food_ID INT,                             -- References the food listing
    Receiver_ID INT,                         -- References the receiver claiming food
    Status VARCHAR(50),                       -- Status of the claim (e.g., Pending, Completed)
    Timestamp DATETIME,                       -- Time of the claim
    FOREIGN KEY (Food_ID) REFERENCES Food_Listings(Food_ID),
    FOREIGN KEY (Receiver_ID) REFERENCES Receivers(Receiver_ID)
);
