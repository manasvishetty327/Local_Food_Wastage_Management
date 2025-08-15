-- 14. What is the average quantity of food claimed per receiver
SELECT r.Name AS Receiver_Name, 
       ROUND(AVG(f.Quantity), 2) AS Avg_Quantity_Claimed
FROM Claims c
JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
JOIN Food_Listings f ON c.Food_ID = f.Food_ID
GROUP BY r.Name
ORDER BY Avg_Quantity_Claimed DESC;

-- 15. Which meal type (Breakfast, Lunch, Dinner, Snacks) is claimed the most
SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
FROM Claims c
JOIN Food_Listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Meal_Type
ORDER BY Total_Claims DESC;

-- 16. What is the total quantity of food donated by each provider
SELECT p.Name AS Provider_Name, SUM(f.Quantity) AS Total_Donated
FROM Food_Listings f
JOIN Providers p ON f.Provider_ID = p.Provider_ID
GROUP BY p.Name
ORDER BY Total_Donated DESC;

-- 17. List the top 5 receivers who have claimed the most total food quantity
SELECT r.Name AS Receiver_Name, SUM(f.Quantity) AS Total_Claimed
FROM Claims c
JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
JOIN Food_Listings f ON c.Food_ID = f.Food_ID
GROUP BY r.Name
ORDER BY Total_Claimed DESC
LIMIT 5;

-- 18. Show the food types that are least claimed (to identify less popular items)
SELECT f.Food_Type, COUNT(c.Claim_ID) AS Claims_Count
FROM Food_Listings f
LEFT JOIN Claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Food_Type
ORDER BY Claims_Count ASC;

