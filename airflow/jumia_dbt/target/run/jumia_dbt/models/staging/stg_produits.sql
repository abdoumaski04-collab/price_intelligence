-- back compat for old kwarg name
  
  
        
            
            
        
    

    

    merge into `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`stg_produits` as DBT_INTERNAL_DEST
        using (
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

        ) as DBT_INTERNAL_SOURCE
        on (
                DBT_INTERNAL_SOURCE.url = DBT_INTERNAL_DEST.url
            )

    
    when matched then update set
        `nom` = DBT_INTERNAL_SOURCE.`nom`,`prix` = DBT_INTERNAL_SOURCE.`prix`,`ancien_prix` = DBT_INTERNAL_SOURCE.`ancien_prix`,`remise` = DBT_INTERNAL_SOURCE.`remise`,`url` = DBT_INTERNAL_SOURCE.`url`,`categorie` = DBT_INTERNAL_SOURCE.`categorie`,`image_url` = DBT_INTERNAL_SOURCE.`image_url`,`source` = DBT_INTERNAL_SOURCE.`source`,`date_scraping` = DBT_INTERNAL_SOURCE.`date_scraping`
    

    when not matched then insert
        (`nom`, `prix`, `ancien_prix`, `remise`, `url`, `categorie`, `image_url`, `source`, `date_scraping`)
    values
        (`nom`, `prix`, `ancien_prix`, `remise`, `url`, `categorie`, `image_url`, `source`, `date_scraping`)


    