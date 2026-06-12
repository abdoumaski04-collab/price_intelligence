-- models/aggregations/agg_comparaison_sites.sql

WITH stats_par_source AS (
    SELECT
        source,
        DATE(date_scraping)         AS date_scraping,
        ROUND(AVG(prix), 2)         AS prix_moyen,
        COUNT(*)                    AS nb_produits,
        ROUND(AVG(remise), 2)       AS remise_moyenne
    FROM `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`cleaned_produits`
    GROUP BY source, DATE(date_scraping)
),

pivot AS (
    SELECT
        date_scraping,
        MAX(CASE WHEN source = 'jumia' THEN prix_moyen END)     AS jumia_prix_moyen,
        MAX(CASE WHEN source = 'ikea'  THEN prix_moyen END)     AS ikea_prix_moyen,
        MAX(CASE WHEN source = 'kitea' THEN prix_moyen END)     AS kitea_prix_moyen,
        MAX(CASE WHEN source = 'jumia' THEN nb_produits END)    AS jumia_nb_produits,
        MAX(CASE WHEN source = 'ikea'  THEN nb_produits END)    AS ikea_nb_produits,
        MAX(CASE WHEN source = 'kitea' THEN nb_produits END)    AS kitea_nb_produits,
        MAX(CASE WHEN source = 'jumia' THEN remise_moyenne END) AS jumia_remise_moy,
        MAX(CASE WHEN source = 'ikea'  THEN remise_moyenne END) AS ikea_remise_moy,
        MAX(CASE WHEN source = 'kitea' THEN remise_moyenne END) AS kitea_remise_moy
    FROM stats_par_source
    GROUP BY date_scraping
)

SELECT
    date_scraping,
    jumia_prix_moyen,
    ikea_prix_moyen,
    kitea_prix_moyen,
    jumia_nb_produits,
    ikea_nb_produits,
    kitea_nb_produits,
    jumia_remise_moy,
    ikea_remise_moy,
    kitea_remise_moy,
    CASE
        WHEN jumia_prix_moyen IS NULL AND ikea_prix_moyen IS NULL THEN 'kitea'
        WHEN jumia_prix_moyen IS NULL AND kitea_prix_moyen IS NULL THEN 'ikea'
        WHEN ikea_prix_moyen  IS NULL AND kitea_prix_moyen IS NULL THEN 'jumia'
        WHEN jumia_prix_moyen <= IFNULL(ikea_prix_moyen, 9999999)
         AND jumia_prix_moyen <= IFNULL(kitea_prix_moyen, 9999999) THEN 'jumia'
        WHEN ikea_prix_moyen  <= IFNULL(jumia_prix_moyen, 9999999)
         AND ikea_prix_moyen  <= IFNULL(kitea_prix_moyen, 9999999) THEN 'ikea'
        ELSE 'kitea'
    END AS site_moins_cher
FROM pivot