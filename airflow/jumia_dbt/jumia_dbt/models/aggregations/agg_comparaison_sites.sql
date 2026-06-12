-- models/aggregations/agg_comparaison_sites.sql
-- Comparaison des prix entre Jumia, IKEA et Kitea par marque
-- Permet de voir quel site est le moins cher pour chaque marque

WITH stats_par_source AS (
    SELECT
        source,
        marque,
        DATE(date_scraping)         AS date_scraping,
        ROUND(AVG(prix), 2)         AS prix_moyen,
        COUNT(*)                    AS nb_produits,
        ROUND(AVG(remise), 2)       AS remise_moyenne
    FROM {{ ref('cleaned_produits') }}
    GROUP BY source, marque, DATE(date_scraping)
),

-- Pivot : une ligne par marque/date avec les 3 sources côte à côte
pivot AS (
    SELECT
        marque,
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
    GROUP BY marque, date_scraping
)

SELECT
    marque,
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

    -- Site le moins cher pour cette marque
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
ORDER BY date_scraping DESC, marque