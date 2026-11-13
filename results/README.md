# Resultados

Nenhum experimento foi executado. Os futuros executores criarão diretórios
`<run_id>/`, ignorados pelo Git, contendo a configuração efetivamente utilizada
em `config.yaml`, os metadados em `metadata.json`, as métricas por amostra em
`raw_metrics.csv` e as falhas em `failures.csv`. A análise poderá derivar
`summary.csv`, `figures/`, `tables/` e exemplos autorizados em `examples/`
a partir desses registros.

Usar identificadores estáveis de execução, experimento, dataset, amostra, método,
condição e repetição. Registrar versões da configuração e do código, sementes
aleatórias, ambiente, hardware quando aplicável e estados explícitos de falha.
Definir o esquema da tabela de métricas junto a cada protocolo; nunca descartar
falhas silenciosamente. Publicar apenas resumos revisados e artefatos cujas
licenças permitam redistribuição.
