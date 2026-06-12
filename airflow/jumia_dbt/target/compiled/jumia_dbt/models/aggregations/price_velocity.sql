WITH prix_par_jour AS (
    SELECT
        source,
        nom,
        url,
        prix,
        DATE(date_scraping) AS date_jour,
        LAG(prix) OVER (
            PARTITION BY url
            ORDER BY date_scraping
        ) AS prix_precedent
    FROM `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`cleaned_produits`
),

velocity AS (
    SELECT
        source,
        nom,
        url,
        prix,
        date_jour,
        prix_precedent,
        ROUND(prix - prix_precedent, 2) AS variation_prix,
        CASE
            WHEN prix < prix_precedent THEN 'Baisse'
            WHEN prix > prix_precedent THEN 'Hausse'
            ELSE 'Stable'
        END AS tendance
    FROM prix_par_jour
    WHERE prix_precedent IS NOT NULL
)

SELECT * FROM velocity
ORDER BY date_jour DESC