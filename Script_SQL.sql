#Script da consulta feita na base de dados dbaih no sistema Greenplum em 17/10/2019.


SELECT *
FROM dbaih.tb_espelho_aih
WHERE (dt_internacao LIKE '%2017' or dt_internacao LIKE '%2018' or dt_internacao LIKE '%2019')
	   AND sg_uf = 'AL' 
	   AND complexidade LIKE '3%'
	   AND st_situacao = 'OK'; 
	   
#Consultas auxiliares feitas para medir preliminarmente a integridade dos dados e evitar erros futuros

SELECT sg_uf, COUNT(sg_uf)
FROM dbaih.tb_espelho_aih
GROUP BY 1
ORDER BY 2 DESC;

# Não há nenhum registro na base de dados com 'baixa complexidade'. A ser verificado posteriormente. 
SELECT complexidade, COUNT(complexidade)
FROM dbaih.tb_espelho_aih
GROUP BY 1
ORDER BY 2 DESC;


WITH  sub as (SELECT *
FROM DBAIH.tb_espelho_aih_1_prt_pt_201901
WHERE sg_uf = 'AL' AND complexidade LIKE '3%')

SELECT st_situacao, COUNT(st_situacao)
FROM sub
GROUP BY 1
ORDER BY 2 DESC;





