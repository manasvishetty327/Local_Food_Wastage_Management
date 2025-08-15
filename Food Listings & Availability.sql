-- 6. Total quantity of food available from all providers
SELECT SUM(Quantity) AS Total_Food_Quantity
FROM Food_Listings;

-- 7. City with highest number of food listings
SELECT Location AS City, COUNT(*) AS Total_Listings
FROM Food_Listings
GROUP BY Location
ORDER BY Total_Listings DESC
LIMIT 1;

-- 8. Most commonly available food types
SELECT Food_Type, COUNT(*) AS Count
FROM Food_Listings
GROUP BY Food_Type
ORDER BY Count DESC
LIMIT 5;

-- 9. Total quantity of each food type available
SELECT Food_Type, SUM(Quantity) AS Total_Quantity
FROM Food_Listings
GROUP BY Food_Type;

-- 10. List food listings per provider with total quantity
SELECT p.Name AS Provider_Name, SUM(f.Quantity) AS Total_Quantity
FROM Food_Listings f
JOIN Providers p ON f.Provider_ID=p.Provider_ID
GROUP BY p.Name;
