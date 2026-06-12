-- models/cleaned/cleaned_produits.sql
-- Union des 3 sources (Jumia + IKEA + Kitea)
-- Ajout des colonnes calculées : prix_euro, type_remise, economie_mad

WITH jumia AS (
    SELECT * FROM {{ ref('stg_jumia') }}
),
ikea AS (
    SELECT * FROM {{ ref('stg_ikea') }}
),
kitea AS (
    SELECT * FROM {{ ref('stg_kitea') }}
),

-- Union des 3 sources
all_sources AS (
    SELECT * FROM jumia
    UNION ALL
    SELECT * FROM ikea
    UNION ALL
    SELECT * FROM kitea
)

SELECT
    source,
    nom,
    marque,
    prix,
    ancien_prix,
    remise,
    rating,
    url,
    date_scraping,

    -- Conversion MAD → EUR (taux fixe 0.093)
    ROUND(prix * 0.093, 2)                          AS prix_euro,

    -- Catégorie de remise
    CASE
        WHEN remise >= 50 THEN 'Forte remise'
        WHEN remise >= 20 THEN 'Remise moyenne'
        WHEN remise >  0  THEN 'Petite remise'
        ELSE                   'Sans remise'
    END                                             AS type_remise,

    -- Économie réalisée en MAD
    CASE
        WHEN ancien_prix IS NOT NULL AND ancien_prix > prix
        THEN ROUND(ancien_prix - prix, 2)
        ELSE 0.0
    END                                             AS economie_mad,

    -- Bon plan : remise >= 20% ET rating >= 4
    CASE
        WHEN remise >= 20 AND rating >= 4 THEN TRUE
        ELSE FALSE
    END                                             AS est_bon_plan

FROM all_sources