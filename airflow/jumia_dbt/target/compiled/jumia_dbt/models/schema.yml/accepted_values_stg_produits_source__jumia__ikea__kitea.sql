
    
    

with all_values as (

    select
        source as value_field,
        count(*) as n_records

    from `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`stg_produits`
    group by source

)

select *
from all_values
where value_field not in (
    'jumia','ikea','kitea'
)


