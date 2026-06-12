
    
    

with all_values as (

    select
        niveau_remise as value_field,
        count(*) as n_records

    from `diesel-patrol-491520-j8`.`jumia_price_intelligence`.`cleaned_produits`
    group by niveau_remise

)

select *
from all_values
where value_field not in (
    'sans remise','remise faible (<10%)','remise modérée (10–24%)','remise forte (25–49%)','remise exceptionnelle (≥50%)'
)


