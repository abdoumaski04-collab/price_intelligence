select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select date_scraping
from `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`stg_produits`
where date_scraping is null



      
    ) dbt_internal_test