-- back compat for old kwarg name
  
  
        
            
            
        
    

    

    merge into `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`stg_produits` as DBT_INTERNAL_DEST
        using (

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

        ) as DBT_INTERNAL_SOURCE
        on (
                DBT_INTERNAL_SOURCE.url = DBT_INTERNAL_DEST.url
            )

    
    when matched then update set
        `nom` = DBT_INTERNAL_SOURCE.`nom`,`marque` = DBT_INTERNAL_SOURCE.`marque`,`prix` = DBT_INTERNAL_SOURCE.`prix`,`ancien_prix` = DBT_INTERNAL_SOURCE.`ancien_prix`,`remise` = DBT_INTERNAL_SOURCE.`remise`,`rating` = DBT_INTERNAL_SOURCE.`rating`,`url` = DBT_INTERNAL_SOURCE.`url`,`date_scraping` = DBT_INTERNAL_SOURCE.`date_scraping`
    

    when not matched then insert
        (`nom`, `marque`, `prix`, `ancien_prix`, `remise`, `rating`, `url`, `date_scraping`)
    values
        (`nom`, `marque`, `prix`, `ancien_prix`, `remise`, `rating`, `url`, `date_scraping`)


    