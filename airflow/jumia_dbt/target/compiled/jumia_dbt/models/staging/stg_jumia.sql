SELECT
    'jumia'                             AS source,
    nom,
    CAST(prix AS FLOAT64)               AS prix,
    CAST(ancien_prix AS FLOAT64)        AS ancien_prix,
    CAST(remise AS FLOAT64)             AS remise,
    url,
    categorie,
    image_url,
    CAST(date_scraping AS TIMESTAMP)    AS date_scraping
FROM `diesel-patrol-491520-j8.jumia_price_intelligence.produits`
WHERE source = 'jumia'
    AND prix IS NOT NULL AND prix > 0 AND nom IS NOT NULL