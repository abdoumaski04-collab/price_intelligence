SELECT
    nom,
    marque,
    prix,
    ancien_prix,
    remise,
    rating,
    url,
    date_scraping,
    CASE
        WHEN remise >= 50 THEN 'Forte remise'
        WHEN remise >= 20 THEN 'Remise moyenne'
        WHEN remise > 0 THEN 'Petite remise'
        ELSE 'Sans remise'
    END as type_remise
FROM
    `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`stg_produits`