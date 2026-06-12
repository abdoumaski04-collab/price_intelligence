-- models/aggregations/agg_prix_categorie.sql
-- Matérialisé en TABLE dans BigQuery → utilisé pour le dashboard

SELECT
    source,
    DATE(date_scraping)             AS date_scraping,

    COUNT(*)                        AS nombre_produits,
    ROUND(AVG(prix), 2)             AS prix_moyen,
    MIN(prix)                       AS prix_min,
    MAX(prix)                       AS prix_max,
    ROUND(STDDEV(prix), 2)          AS volatilite_prix,
    ROUND(AVG(remise), 2)           AS remise_moyenne,
    COUNTIF(est_bon_plan = TRUE)    AS nb_bons_plans

FROM `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`cleaned_produits`

GROUP BY
    source,
    DATE(date_scraping)

ORDER BY
    date_scraping DESC,
    prix_moyen DESC