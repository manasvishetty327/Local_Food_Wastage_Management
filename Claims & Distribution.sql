-- 11. How many food claims have been made for each food item
SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
FROM Food_Listings f
LEFT JOIN Claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Food_Name
ORDER BY Total_Claims DESC;

-- 12. Which provider has had the highest number of successful (Completed) food claims
SELECT p.Name AS Provider_Name, COUNT(c.Claim_ID) AS Completed_Claims
FROM Claims c
JOIN Food_Listings f ON c.Food_ID = f.Food_ID
JOIN Providers p ON f.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Name
ORDER BY Completed_Claims DESC
LIMIT 1;

-- 13. What percentage of food claims are Completed vs Pending vs Canceled
SELECT Status, 
       ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM Claims), 2) AS Percentage
FROM Claims
GROUP BY Status;
