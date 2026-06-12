select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select date_aggregation
from `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`agg_prix_categorie`
where date_aggregation is null



      
    ) dbt_internal_test