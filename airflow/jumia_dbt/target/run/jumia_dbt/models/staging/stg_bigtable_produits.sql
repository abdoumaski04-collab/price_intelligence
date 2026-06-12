

  create or replace view `diesel-patrol-491520-j8`.`price_intelligence_bigtable`.`stg_bigtable_produits`
  OPTIONS()
  as 

with source_data as (
    select * from `diesel-patrol-491520-j8.price_intelligence_bigtable.produits_external`
),

flattened_data as (
    select
        safe_convert_bytes_to_string(rowkey) as full_rowkey,
        (select p.value from unnest(price_cf.prix.cell) p order by p.timestamp desc limit 1) as prix,
        (select p.value from unnest(price_cf.nom.cell) p order by p.timestamp desc limit 1) as nom,
        (select p.value from unnest(price_cf.source.cell) p order by p.timestamp desc limit 1) as source,
        (select p.value from unnest(price_cf.categorie.cell) p order by p.timestamp desc limit 1) as categorie,
        (select p.value from unnest(price_cf.url.cell) p order by p.timestamp desc limit 1) as url,
        (select p.value from unnest(price_cf.date_scraping.cell) p order by p.timestamp desc limit 1) as date_scraping
    from source_data
)

select
    full_rowkey,
    split(full_rowkey, '#')[OFFSET(0)] as plateforme_source,
    cast(prix as numeric) as prix_actuel,
    nom,
    url,
    source,
    categorie,
    date_scraping as date_extraction
from flattened_data;

