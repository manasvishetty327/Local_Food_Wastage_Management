-- 1. Count of food providers in each city
SELECT City, COUNT(*) AS Total_Providers
FROM Providers
GROUP BY City;

-- 2. Count of receivers in each city
SELECT City, COUNT(*) AS Total_Receivers
FROM Receivers
GROUP BY City;

-- 3. Type of provider contributing the most food (based on number of listings)
SELECT Provider_Type, COUNT(*) AS Total_Food_Listings
FROM Food_Listings
GROUP BY Provider_Type
ORDER BY Total_Food_Listings DESC
LIMIT 1;

-- 4. Contact info of providers in a specific city (e.g., Bangalore)
SELECT Name, Contact
FROM Providers
WHERE City='Bangalore';

-- 5. Receivers who have claimed the most food (by number of claims)
SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims
FROM Receivers r
JOIN Claims c ON r.Receiver_ID=c.Receiver_ID
GROUP BY r.Name
ORDER BY Total_Claims DESC
LIMIT 5;
