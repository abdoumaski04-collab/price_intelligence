
    
    

with all_values as (

    select
        tendance as value_field,
        count(*) as n_records

    from `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`price_velocity`
    group by tendance

)

select *
from all_values
where value_field not in (
    'Hausse','Baisse','Stable'
)


