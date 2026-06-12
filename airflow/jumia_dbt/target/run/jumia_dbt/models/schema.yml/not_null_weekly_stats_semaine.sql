select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select semaine
from `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`weekly_stats`
where semaine is null



      
    ) dbt_internal_test