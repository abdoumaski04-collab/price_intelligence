select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select prix_moyen
from `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`agg_prix_categorie`
where prix_moyen is null



      
    ) dbt_internal_test