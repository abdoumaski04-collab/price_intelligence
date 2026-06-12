select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select source
from `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`weekly_stats`
where source is null



      
    ) dbt_internal_test