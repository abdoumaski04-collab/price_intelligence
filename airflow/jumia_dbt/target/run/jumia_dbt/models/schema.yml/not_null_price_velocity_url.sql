select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select url
from `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`price_velocity`
where url is null



      
    ) dbt_internal_test