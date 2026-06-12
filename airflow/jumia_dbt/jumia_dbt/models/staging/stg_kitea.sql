-- models/staging/stg_kitea.sql
-- Lecture des données brutes Kitea depuis BigQuery
-- Casting des types + filtre qualité de base

SELECT
    'kitea'                             AS source,
    nom,
    marque,
    CAST(prix AS FLOAT64)               AS prix,
    CAST(ancien_prix AS FLOAT64)        AS ancien_prix,
    CAST(remise AS FLOAT64)             AS remise,
    CAST(rating AS FLOAT64)             AS rating,
    url,
    CAST(date_scraping AS TIMESTAMP)    AS date_scraping
FROM
    `diesel-patrol-491520-j8.jumia_price_intelligence.produits_kitea`
WHERE
    prix IS NOT NULL
    AND prix > 0
    AND nom IS NOT NULL