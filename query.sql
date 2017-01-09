.headers on
.mode csv
.output conf_time_vs_fee_rate.csv
select (julianday(first_confirmed) - julianday(first_seen)) * 86400 as conf_time,
       fee/size as fee_rate,
       transaction_id,
       first_seen,
       first_confirmed,
       fee,
       size
  from transactions 
  where first_confirmed is not null and 
        fee > -1
  order by first_confirmed;
