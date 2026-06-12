select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select tranche_prix
from `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`cleaned_produits`
where tranche_prix is null



      
    ) dbt_internal_test