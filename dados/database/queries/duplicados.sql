use `mcaorg1_uconecte`;

select *, count(*) from robo_log 
where fk_idRobo = 1 
and status = 2 
group by fk_idContrato having count(*) > 1
order by dataConsulta desc;