

SELECT
    nom,
    marque,
    CAST(prix AS FLOAT64) as prix,
    CAST(ancien_prix AS FLOAT64) as ancien_prix,
    CAST(remise AS FLOAT64) as remise,
    CAST(rating AS FLOAT64) as rating,
    url,
    CAST(date_scraping AS TIMESTAMP) as date_scraping
FROM
    `diesel-patrol-491520-j8.jumia_price_intelligence.produits`
WHERE
    prix IS NOT NULL
    AND prix > 0


    AND date_scraping > (SELECT MAX(date_scraping) FROM `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`stg_produits`)
