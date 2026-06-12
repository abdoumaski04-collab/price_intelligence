-- models/aggregations/weekly_stats.sql
-- Statistiques hebdomadaires par source
-- Utilisé par le DAG Airflow weekly_report_pipeline

SELECT
    source,
    DATE_TRUNC(DATE(date_scraping), WEEK)        AS semaine,

    COUNT(*)                                    AS total_produits,
    ROUND(AVG(prix), 2)                         AS prix_moyen_semaine,
    ROUND(MIN(prix), 2)                         AS prix_min_semaine,
    ROUND(MAX(prix), 2)                         AS prix_max_semaine,
    ROUND(STDDEV(prix), 2)                      AS ecart_type_prix,
    ROUND(AVG(remise), 2)                       AS remise_moyenne_semaine,
    COUNTIF(remise IS NOT NULL AND remise > 0)  AS nb_avec_remise,

    -- Percentiles de prix
    ROUND(APPROX_QUANTILES(prix, 4)[OFFSET(1)], 2) AS prix_q1,
    ROUND(APPROX_QUANTILES(prix, 4)[OFFSET(2)], 2) AS prix_median,
    ROUND(APPROX_QUANTILES(prix, 4)[OFFSET(3)], 2) AS prix_q3

FROM {{ ref('cleaned_produits') }}

WHERE prix IS NOT NULL

GROUP BY
    source,
    DATE_TRUNC(DATE(date_scraping), WEEK)

ORDER BY
    semaine DESC,
    source