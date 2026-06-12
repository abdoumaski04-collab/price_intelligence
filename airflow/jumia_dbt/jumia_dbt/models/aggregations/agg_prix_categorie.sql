-- models/aggregations/agg_prix_categorie.sql
-- Prix moyen / min / max par source et par marque, par jour
-- Matérialisé en TABLE dans BigQuery → utilisé pour le dashboard

SELECT
    source,
    marque,
    DATE(date_scraping)             AS date_scraping,

    COUNT(*)                        AS nombre_produits,
    ROUND(AVG(prix), 2)             AS prix_moyen,
    MIN(prix)                       AS prix_min,
    MAX(prix)                       AS prix_max,
    ROUND(STDDEV(prix), 2)          AS volatilite_prix,
    ROUND(AVG(remise), 2)           AS remise_moyenne,
    ROUND(AVG(rating), 2)           AS rating_moyen,
    COUNTIF(est_bon_plan = TRUE)    AS nb_bons_plans

FROM {{ ref('cleaned_produits') }}

GROUP BY
    source,
    marque,
    DATE(date_scraping)

ORDER BY
    date_scraping DESC,
    prix_moyen DESC