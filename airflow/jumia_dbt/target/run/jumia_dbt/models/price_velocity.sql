

  create or replace view `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`price_velocity`
  OPTIONS()
  as WITH prix_par_jour AS (
    SELECT
        nom,
        marque,
        prix,
        DATE(date_scraping) as date_jour,
        LAG(prix) OVER (
            PARTITION BY url 
            ORDER BY date_scraping
        ) as prix_precedent
    FROM `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`stg_produits`
),

velocity AS (
    SELECT
        nom,
        marque,
        prix,
        date_jour,
        prix_precedent,
        ROUND(prix - prix_precedent, 2) as variation_prix,
        CASE
            WHEN prix < prix_precedent THEN 'Baisse'
            WHEN prix > prix_precedent THEN 'Hausse'
            ELSE 'Stable'
        END as tendance
    FROM prix_par_jour
    WHERE prix_precedent IS NOT NULL
)

SELECT * FROM velocity
ORDER BY date_jour DESC;

