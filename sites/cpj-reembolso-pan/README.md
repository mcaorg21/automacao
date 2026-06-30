# CPJ Reembolso - PAN

Automação de registro de reembolso de custas no CPJ para o banco PAN.

## Estrutura

```
cpj-reembolso-pan/
├── main.py                  # Script principal
├── config.json              # Parâmetros de execução
├── requirements.txt         # Dependências Python
├── images/                  # Screenshots de referência para reconhecimento de imagem
├── planilha/                # CSVs/JSONs exportados do CPJ
├── planilha_modelo/pan/     # Planilhas modelo XLS
├── planilha_modelo_excel/   # Planilhas modelo XLSX
├── pdf_merge/               # PDFs mesclados temporários
└── documento_modelo/pan/    # Documentos DOCX/PDF de descritivo
```

## Uso

```bash
# Com argumentos
python main.py <numero_recibo> <data_inicial dd/mm/yyyy> <data_final dd/mm/yyyy>

# Via config.json
python main.py
```
