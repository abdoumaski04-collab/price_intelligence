select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select categorie_normalisee
from `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`cleaned_produits`
where categorie_normalisee is null



      
    ) dbt_internal_test