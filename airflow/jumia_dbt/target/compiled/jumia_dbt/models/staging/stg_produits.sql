
SELECT
    nom,
    CAST(prix AS FLOAT64)            AS prix,
    CAST(ancien_prix AS FLOAT64)     AS ancien_prix,
    CAST(remise AS FLOAT64)          AS remise,
    url,
    categorie,
    image_url,
    source,
    CAST(date_scraping AS TIMESTAMP) AS date_scraping
FROM `diesel-patrol-491520-j8.jumia_price_intelligence.produits`
WHERE prix IS NOT NULL
    AND prix > 0
    AND nom IS NOT NULL

    AND date_scraping > (SELECT MAX(date_scraping) FROM `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`stg_produits`)
