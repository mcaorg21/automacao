### Instruções banco de dados

[Documentação](https://tinydb.readthedocs.io/en/latest/index.html)

### Principais funcionalidades

- Inicialização do Banco:

```
db = TinyDB('caminho_completo_do_db.json')
```

- Inserção:

```
db.insert({
    'sigla': 'MG',
    'idOrgaoUconecte': '63',
    'idPerfilUconecte': '1',
    'tabelas': ['1', '2'],
    'idOrgaoOle': "008525"
})
```

- Busca:

```
// Múltiplos resultados
db.search(Query().idPerfilUconecte == '1') 

// Apenas um Resultado
db.get(Query().idPerfilUconecte == '1')['idOrgaoOle'] // Encontra "008525"
```