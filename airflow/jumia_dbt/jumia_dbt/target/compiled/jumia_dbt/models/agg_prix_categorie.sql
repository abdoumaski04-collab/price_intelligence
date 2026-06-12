SELECT
    marque,
    COUNT(*) as nombre_produits,
    ROUND(AVG(prix), 2) as prix_moyen,
    MIN(prix) as prix_min,
    MAX(prix) as prix_max,
    ROUND(AVG(remise), 2) as remise_moyenne,
    ROUND(AVG(rating), 2) as rating_moyen,
    DATE(date_scraping) as date_scraping
FROM
    `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`cleaned_produits`
GROUP BY
    marque,
    DATE(date_scraping)
ORDER BY
    prix_moyen DESC