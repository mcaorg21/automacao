SELECT login,senha FROM tbl_repositorio_adm
WHERE fk_idRobo IN ? AND login LIKE '%?%'