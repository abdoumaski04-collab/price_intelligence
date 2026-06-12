select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select categorie
from `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`stg_produits`
where categorie is null



      
    ) dbt_internal_test