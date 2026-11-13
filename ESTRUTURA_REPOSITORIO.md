# Estrutura do repositório — Face Processing Benchmark

> **Finalidade:** especificar a organização de pastas, as responsabilidades dos módulos e as regras de desenvolvimento para que o Codex possa criar e expandir o repositório `face-processing-benchmark` de forma consistente.
>
> **Escopo:** projeto científico independente para comparar detecção facial, centralização/recorte, segmentação de pessoas e o efeito do pré-processamento sobre a segmentação. Não deve importar código ou depender de uma aplicação externa.
>
> **Idioma:** nomes de arquivos, pastas, funções, classes, variáveis, docstrings, comentários, mensagens de log e configurações em **inglês**. Documentação acadêmica pode ser redigida em português, conforme a necessidade do trabalho.

## 1. Princípios de organização

1. **Separação de responsabilidades:** algoritmos processam imagens; experimentos executam protocolos; métricas avaliam resultados; análise gera estatísticas e figuras; documentos apresentam a pesquisa.
2. **Métodos substituíveis:** incluir um detector ou segmentador novo não deve exigir reescrever os scripts experimentais.
3. **Execução independente:** cada experimento deve ter seu próprio ponto de entrada (CLI), além de existir uma execução conjunta opcional.
4. **Rastreabilidade:** cada resultado deve identificar dataset, amostra, método, configuração, versão e execução.
5. **Reprodutibilidade:** registrar sementes aleatórias, versões de bibliotecas/modelos, parâmetros, ambiente e informações do hardware quando aplicável.
6. **Dados imutáveis:** preservar datasets originais e anotações de referência; derivações vão para diretórios separados.
7. **Crescimento incremental:** criar inicialmente apenas o esqueleto e os arquivos necessários; não implementar todos os candidatos ou gerar arquivos vazios indiscriminadamente.
8. **Sem dependência de interface gráfica:** a execução principal deve funcionar pelo terminal, inclusive em lote.

## 2. Árvore de diretórios proposta

O desenho abaixo é a **estrutura-alvo**, não uma ordem para implementar tudo imediatamente. Arquivos marcados como `example` representam padrões de nomes; só devem ser criados após a seleção dos métodos e a necessidade concreta.

```text
face-processing-benchmark/
├── README.md
├── ETAPAS.md
├── ESTRUTURA_REPOSITORIO.md
├── LICENSE
├── .gitignore
├── pyproject.toml
├── requirements-lock.txt                 # Optional; generated after dependency resolution
│
├── configs/
│   ├── datasets.yaml                     # Dataset registration and paths
│   ├── methods.yaml                      # Methods, checkpoints and parameters
│   ├── experiments/
│   │   ├── face_detection.yaml
│   │   ├── face_alignment.yaml
│   │   ├── segmentation.yaml
│   │   ├── preprocessing_impact.yaml
│   │   ├── performance.yaml
│   │   └── pipeline.yaml
│   └── presets/                          # Optional named configurations
│
├── src/
│   └── face_processing_benchmark/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── types.py                   # Common data contracts
│       │   ├── interfaces.py              # Detector, cropper, segmenter interfaces
│       │   ├── registry.py                # Method registration / discovery
│       │   ├── config.py                  # Config loading and validation
│       │   └── geometry.py                # Coordinate transforms and crop geometry
│       │
│       ├── methods/
│       │   ├── __init__.py
│       │   ├── detection/
│       │   │   ├── __init__.py
│       │   │   ├── classical/
│       │   │   │   └── haar_cascade.py     # Example
│       │   │   └── deep_learning/
│       │   │       └── yunet.py           # Example
│       │   ├── alignment/
│       │   │   ├── __init__.py
│       │   │   ├── translate.py           # Example: center with translation
│       │   │   └── crop.py                # Example: center by cropping
│       │   └── segmentation/
│       │       ├── __init__.py
│       │       ├── classical/
│       │       │   └── grabcut.py         # Example
│       │       └── deep_learning/
│       │           └── modnet.py          # Example
│       │
│       ├── data/
│       │   ├── __init__.py
│       │   ├── loaders.py                 # Read images, masks and annotations
│       │   ├── manifests.py               # Sample IDs and metadata
│       │   ├── validation.py              # Input/reference validation
│       │   └── transforms.py              # Apply identical transforms to GT
│       │
│       ├── evaluation/
│       │   ├── __init__.py
│       │   ├── detection_metrics.py
│       │   ├── alignment_metrics.py
│       │   ├── segmentation_metrics.py
│       │   ├── performance_metrics.py
│       │   └── aggregation.py             # Aggregate raw per-image metrics
│       │
│       ├── experiments/
│       │   ├── __init__.py
│       │   ├── face_detection.py
│       │   ├── face_alignment.py
│       │   ├── segmentation.py
│       │   ├── preprocessing_impact.py
│       │   ├── performance.py
│       │   └── pipeline.py
│       │
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── statistics.py              # CIs, paired comparisons etc.
│       │   ├── plots.py                   # Reproducible plots
│       │   ├── tables.py                  # Summary tables
│       │   └── examples.py                # Failure / success case selection
│       │
│       └── utils/
│           ├── __init__.py
│           ├── image_io.py
│           ├── logging_utils.py
│           ├── profiling.py
│           └── reproducibility.py
│
├── scripts/
│   ├── prepare_dataset.py
│   ├── validate_dataset.py
│   ├── run_face_detection.py
│   ├── run_face_alignment.py
│   ├── run_segmentation.py
│   ├── run_preprocessing_impact.py
│   ├── run_performance.py
│   ├── run_pipeline.py
│   ├── run_all.py
│   └── generate_report_assets.py
│
├── datasets/
│   ├── README.md
│   ├── raw/                             # Downloaded originals (ignored by Git)
│   ├── annotations/                     # Source ground truth (ignored by Git)
│   ├── processed/                       # Derived images/masks (ignored by Git)
│   ├── manifests/                       # Versioned metadata where permitted
│   └── samples/                         # Small redistributable test fixtures only
│
├── models/
│   ├── README.md                         # Weights, sources, licenses, checksums
│   └── checkpoints/                     # Downloaded weights (ignored by Git)
│
├── results/
│   ├── README.md
│   └── <run_id>/                         # Generated by the runner (ignored by Git)
│       ├── metadata.json
│       ├── config.yaml
│       ├── raw_metrics.csv
│       ├── summary.csv
│       ├── failures.csv
│       ├── figures/
│       ├── tables/
│       └── examples/
│
├── tests/
│   ├── conftest.py
│   ├── test_geometry.py
│   ├── test_transforms.py
│   ├── test_detection_metrics.py
│   ├── test_alignment_metrics.py
│   ├── test_segmentation_metrics.py
│   ├── test_config.py
│   └── test_cli_smoke.py
│
├── docs/
│   ├── methodology.md                   # Experimental protocol
│   ├── datasets.md                      # Dataset provenance and conditions
│   ├── methods.md                       # Selected methods and citations
│   ├── metrics.md                       # Formal metric definitions
│   ├── reproducibility.md               # Exact replay instructions
│   └── decisions/                       # Short architectural/research decisions
│
├── report/
│   ├── main.tex
│   ├── sections/
│   ├── figures/                         # Selected/copied figures for LaTeX
│   ├── tables/                          # Selected/copied tables for LaTeX
│   └── references.bib
│
└── presentation/
    ├── README.md
    └── assets/                            # Selected figures/examples for slides
```

## 3. Responsabilidade de cada pasta

| Pasta | Responsabilidade | O que não deve conter |
|---|---|---|
| `configs/` | Parametrizar datasets, métodos, experimentos e caminhos | Lógica de processamento ou resultados |
| `src/.../core/` | Contratos, tipos, registro de métodos e operações geométricas genéricas | Implementações específicas de modelos |
| `src/.../methods/` | Implementar ou adaptar cada algoritmo de detecção, centralização e segmentação | Cálculo de estatísticas globais e criação de gráficos |
| `src/.../data/` | Ler, organizar, validar e transformar dados e ground truth | Treinamento/inferência de modelos |
| `src/.../evaluation/` | Calcular métricas numéricas por amostra e agregações definidas | Gerar figuras e conclusões científicas |
| `src/.../experiments/` | Orquestrar execuções sob um protocolo experimental | Implementar internamente os algoritmos comparados |
| `src/.../analysis/` | Produzir gráficos, tabelas, estatísticas e casos ilustrativos a partir dos resultados | Executar novamente a inferência |
| `src/.../utils/` | Utilitários pequenos e compartilhados | Lógica central que deveria pertencer a outros módulos |
| `scripts/` | Expor comandos de terminal curtos que chamam os módulos de `src/` | Grandes implementações duplicadas |
| `datasets/` | Armazenar originais, anotações, derivados e manifests | Resultados de avaliação ou checkpoints de modelos |
| `models/` | Registrar e armazenar pesos externos de modelos | Datasets e saídas de experimentos |
| `results/` | Conter tudo que uma execução gerar, identificado por `run_id` | Dados de origem ou códigos-fonte |
| `tests/` | Testes unitários, de integração e smoke tests, usando dados pequenos | Execuções completas dos benchmarks |
| `docs/` | Metodologia, decisões, protocolos e documentação de reprodução | Artefatos finais de relatório e apresentação |
| `report/` | Fontes e materiais selecionados do relatório acadêmico | Resultados brutos gigantes e modelos |
| `presentation/` | Recursos da apresentação acadêmica | Código experimental |

## 4. Responsabilidades dos arquivos principais

### Raiz

- **`README.md`** — apresentação curta do objetivo, instalação, comandos básicos, organização e links para documentos detalhados.
- **`ETAPAS.md`** — checklist de planejamento e acompanhamento do projeto.
- **`ESTRUTURA_REPOSITORIO.md`** — este contrato de organização para humanos e Codex.
- **`pyproject.toml`** — metadados do pacote Python, versão mínima, dependências básicas/extra opcionais, ferramentas de lint/teste e comandos instaláveis quando apropriado.
- **`requirements-lock.txt`** — opcional; dependências resolvidas e fixadas para execução reprodutível em ambiente documentado. Não substituir metadados de dependências do `pyproject.toml`.
- **`.gitignore`** — excluir ambiente virtual, caches, datasets restritos, checkpoints pesados e resultados volumosos; manter arquivos de documentação e pequenas amostras licenciadas.
- **`LICENSE`** — licença do código próprio; não implica que datasets ou pesos externos tenham a mesma licença.

### Contratos e métodos (`src/.../core/`, `src/.../methods/`)

- **`core/types.py`** — formatos padronizados para caixas faciais, landmarks opcionais, máscaras, transformações e resultados com estado de sucesso/falha. Definir convenção explícita de coordenadas, canais e unidades.
- **`core/interfaces.py`** — interfaces abstratas de `FaceDetector`, `ImageAligner` e `PersonSegmenter`. Detector retorna caixas/landmarks/scores; alinhador retorna imagem e transformação; segmentador retorna máscara e metadados.
- **`core/registry.py`** — associar identificadores estáveis (`yunet`, `grabcut`, etc.) às implementações; não misturar registro com inicialização pesada.
- **`core/config.py`** — ler YAML e validar campos obrigatórios, tipos e caminhos, com erros claros.
- **`core/geometry.py`** — calcular regiões de interesse, transformações e conversões de coordenadas. Não aplicar heurísticas de um modelo específico.
- **`methods/detection/...`** — um arquivo por detector, encapsulando carregamento, pré-processamento, inferência e conversão de saída para a interface comum.
- **`methods/alignment/...`** — um arquivo por estratégia de centralização/recorte; retornar também a transformação executada e informações sobre pixels válidos e eventuais preenchimentos.
- **`methods/segmentation/...`** — um arquivo por segmentador; encapsular sua inicialização, inferência e saída em uma convenção comum. Preservar opcionalmente máscara suave/alfa antes de binarizar.

**Regra:** exemplos como `yunet.py` ou `modnet.py` são candidatos, não uma decisão de pesquisa. A lista definitiva será definida na Etapa 1.

### Datasets e referências (`src/.../data/`, `datasets/`)

- **`data/loaders.py`** — carregar imagens, máscaras e rótulos sem assumir um único dataset.
- **`data/manifests.py`** — listar amostras por identificador estável, caminhos, split e metadados necessários para estratificação.
- **`data/validation.py`** — verificar presença de arquivos, leitura, dimensões, formato das máscaras e correspondência entre imagem e referência.
- **`data/transforms.py`** — aplicar a mesma transformação espacial à imagem e ao ground truth, com interpolação apropriada: nearest-neighbor para máscaras binárias e interpolação documentada para máscaras alfa.
- **`datasets/README.md`** — registrar fontes, licença, download, organização esperada e instruções de preparação; não incluir URLs fictícias.
- **`datasets/raw/`** — somente imagens de origem, sem modificações.
- **`datasets/annotations/`** — referências originais, preservadas.
- **`datasets/processed/`** — derivados regeneráveis, com configuração e procedência rastreáveis.
- **`datasets/manifests/`** — índices de imagens, splits e versões. Versionar apenas metadados que possam ser publicados.
- **`datasets/samples/`** — mínimo conjunto de testes, apenas quando a licença permitir redistribuição.

### Avaliação (`src/.../evaluation/`)

- **`detection_metrics.py`** — detecção, correspondência com anotações, recall/precisão e/ou erros de localização conforme o protocolo.
- **`alignment_metrics.py`** — distância do rosto ao alvo, erro normalizado e validade/preservação do recorte; distinguir erro de detecção de erro do algoritmo de alinhamento.
- **`segmentation_metrics.py`** — IoU, Dice, Boundary F1 e outras métricas previamente definidas; documentar limiares, tolerância de borda e casos de máscaras vazias.
- **`performance_metrics.py`** — estruturação dos registros de tempo, memória e metadados do ambiente; evitar contaminar o tempo com download de pesos ou criação de gráficos.
- **`aggregation.py`** — agregar medições por método/dataset/condição, mantendo o resultado por amostra disponível.

### Experimentos (`src/.../experiments/`)

Cada arquivo representa um **protocolo diferente**:

- **`face_detection.py`** — comparar detectores em entradas e anotações comuns.
- **`face_alignment.py`** — comparar centralização, recorte e preservação da área/qualidade geométrica.
- **`segmentation.py`** — comparar segmentadores com imagens e ground truth alinhados.
- **`preprocessing_impact.py`** — comparar segmentação em imagens originais, centralizadas sem recorte e centralizadas com recorte; registrar transformações, área preservada e região de avaliação.
- **`performance.py`** — medir custo computacional com aquecimento, repetições e separação entre carregamento/inferência, se previsto no protocolo.
- **`pipeline.py`** — avaliar combinações selecionadas de detecção, centralização e segmentação, registrando falhas propagadas.

**Regra crítica:** o experimento de impacto do pré-processamento deve transformar a máscara de referência com a **mesma geometria** aplicada à imagem. Medir em regiões válidas comparáveis e registrar a área removida pelo recorte, para que a melhora aparente de uma métrica não seja confundida com exclusão de regiões difíceis.

### Análise (`src/.../analysis/`)

- **`statistics.py`** — médias, medianas, dispersão, intervalos de confiança e comparações pareadas apropriadas.
- **`plots.py`** — construir gráficos a partir de `raw_metrics.csv`/`summary.csv`, sem executar modelos.
- **`tables.py`** — exportar tabelas resumidas em CSV e, opcionalmente, LaTeX/Markdown.
- **`examples.py`** — selecionar casos de sucesso, falha ou divergência com critério explícito e identificador de origem.

### Ferramentas e comandos (`src/.../utils/`, `scripts/`)

- **`image_io.py`** — leitura/escrita de formatos de imagem e normalização de canais.
- **`logging_utils.py`** — logs padronizados por execução, método e amostra.
- **`profiling.py`** — cronômetros, medições de memória e contextos de benchmark.
- **`reproducibility.py`** — sementes, versões instaladas, versão do código e configuração do ambiente.
- **`scripts/prepare_dataset.py`** — preparar um dataset segundo documentação/licença e argumentos explícitos.
- **`scripts/validate_dataset.py`** — executar validação de imagens e referências sem inferência.
- **`scripts/run_*.py`** — CLIs pequenas, independentes e consistentes; cada uma invoca um protocolo em `src/.../experiments/`.
- **`scripts/run_all.py`** — orquestração opcional dos protocolos configurados. Não duplicar sua implementação.
- **`scripts/generate_report_assets.py`** — usar resultados já existentes para gerar estatísticas, figuras e tabelas; jamais recalcular predições.

### Resultados (`results/`)

- **`results/<run_id>/metadata.json`** — identificador da execução, timestamps, comando, versão Git, ambiente e informações de hardware.
- **`results/<run_id>/config.yaml`** — cópia exata da configuração efetivamente usada.
- **`results/<run_id>/raw_metrics.csv`** — uma linha por amostra, método e condição (e repetição quando aplicável).
- **`results/<run_id>/summary.csv`** — resumo agregado gerado a partir das métricas brutas.
- **`results/<run_id>/failures.csv`** — erros, detecções ausentes, arquivos inválidos e motivos; uma falha não deve desaparecer silenciosamente.
- **`results/<run_id>/figures/`** — gráficos derivados da execução.
- **`results/<run_id>/tables/`** — tabelas agregadas.
- **`results/<run_id>/examples/`** — amostras visuais com procedência e autorização de distribuição verificadas.

### Documentos acadêmicos

- **`docs/methodology.md`** — protocolo antes da execução: seleção de dados, condições, repetições, hardware, métricas e regras de exclusão.
- **`docs/datasets.md`** — procedência, características, licenças, splits e limitações de cada base.
- **`docs/methods.md`** — implementações avaliadas, versões dos pesos, artigos, links e parâmetros.
- **`docs/metrics.md`** — fórmulas, convenções, normalizações, limites e interpretação.
- **`docs/reproducibility.md`** — instruções exatas para executar e reproduzir resultados.
- **`docs/decisions/`** — registrar decisões importantes e suas justificativas, com data.
- **`report/`** — arquivos LaTeX, bibliografia e figuras/tabelas selecionadas; pode referenciar resultados gerados, mas não conter cópias indiscriminadas do dataset.
- **`presentation/`** — fontes/recursos de slides, exemplos e figuras selecionadas para apresentação.

## 5. Contratos mínimos entre módulos

A implementação pode escolher `dataclasses`, `Protocol` ou classes abstratas, desde que respeite as convenções abaixo.

| Operação | Entrada mínima | Saída mínima |
|---|---|---|
| Detector facial | Imagem + parâmetros | Lista de caixas faciais e confiança; landmarks opcionais; diagnóstico |
| Centralizador/recortador | Imagem + rosto/landmarks + parâmetros | Imagem transformada + transformação geométrica + região válida |
| Segmentador | Imagem + parâmetros | Máscara 2D no tamanho da imagem + tipo (binária/probabilidade/alfa) + diagnóstico |
| Carregador de dados | Manifest + identificador de amostra | Imagem + ground truth + metadados |
| Avaliador | Predição + referência + região válida + parâmetros | Métricas por imagem + status |
| Executor experimental | Configuração resolvida + seleção de amostras | Resultados brutos + falhas + metadados da execução |
| Gerador de análises | Resultados de uma ou mais execuções | Estatísticas, tabelas, figuras e lista dos resultados analisados |

**Convenções obrigatórias:**

- Coordenadas e unidades explícitas (por exemplo, caixas `xywh` em pixels); sem misturar formatos silenciosamente.
- Definir se imagens estão em RGB ou BGR nas fronteiras dos módulos.
- Máscaras 2D e valores claramente documentados: binário (`0/1` ou `0/255`) ou probabilidades/alfa (`0..1`). Não assumir que todo alfa é uma máscara binária.
- Definir comportamento para múltiplos rostos, nenhuma face, máscaras vazias, tamanhos diferentes e imagens corrompidas.
- Não alterar a imagem ou a máscara original recebida sem contrato explícito.
- Identificadores estáveis para métodos, datasets, imagens, condições e execuções.
- Todos os métodos devem receber configurações explícitas e retornar erros/estados interpretáveis.

## 6. Fluxo de execução e artefatos

```text
configs/ + datasets/ + models/
               |
               v
      scripts/run_*.py
               |
               v
  src/.../experiments/*.py
          /          \
         v            v
  methods/        evaluation/
          \          /
           v        v
     results/<run_id>/
       raw_metrics.csv
       failures.csv
       metadata.json
               |
               v
   scripts/generate_report_assets.py
               |
               v
      analysis/  ->  summary.csv + figures/ + tables/
               |
               v
       report/ + presentation/
```

### Formato mínimo de registro experimental

Preferir arquivos longos (*tidy data*) em CSV/Parquet, mantendo uma linha por observação. Recomenda-se registrar, quando aplicável:

- `run_id`, `experiment`, `dataset_id`, `sample_id`, `method_id`, `condition_id`, `repeat_id`;
- `status`, `error_type`, `error_message`;
- `metric_name` e `metric_value` **ou** colunas numéricas de métrica claramente definidas (escolher uma convenção e documentá-la);
- tempos de carregamento/inferência/total, RAM, formato e resolução;
- `config_hash`, `model_version` e referência da versão de código.

**Não obrigar todos os experimentos a terem exatamente as mesmas métricas:** as métricas de localização facial e segmentação são diferentes. Os identificadores e a rastreabilidade, porém, devem ser compatíveis.

## 7. Regras para datasets, modelos e Git

1. Não versionar datasets completos, imagens sem permissão, checkpoints pesados ou arquivos temporários.
2. Preservar anotações originais; nunca sobrescrever ground truth com versões recortadas.
3. Se um dataset exigir download manual, fornecer instruções e validar a presença dos arquivos.
4. Registrar, para cada checkpoint, origem, versão/commit, checksum quando possível e condições de licença.
5. Não baixar automaticamente pesos/datasets sem o comportamento estar documentado e explicitamente solicitado pelo usuário na execução.
6. Colocar grandes artefatos em caminhos configuráveis, sem depender de diretórios absolutos do desenvolvedor.
7. Versionar código, configs de exemplo, manifests publicáveis e testes pequenos; resultados resumidos podem ser publicados seletivamente quando a licença permitir.
8. Manter caminhos locais, tokens, arquivos pessoais e caches fora do Git.

### `.gitignore` mínimo

```gitignore
.venv/
__pycache__/
.pytest_cache/
.ruff_cache/
*.py[cod]
*.egg-info/
build/
dist/
.env
.env.*
!.env.example

datasets/raw/
datasets/annotations/
datasets/processed/
models/checkpoints/
results/*/
!results/README.md
```

> Ajustar as exclusões se houver pequenos fixtures de teste ou resultados aprovados para publicação. Não usar Git LFS automaticamente sem necessidade e sem decisão explícita.

## 8. Testes e critérios de aceite

Antes de executar um benchmark em escala, garantir:

- **Geometria:** transformação conhecida aplicada à imagem e à referência produz coordenadas e recortes consistentes.
- **Máscaras:** IoU/Dice/Boundary F1 passam por casos sintéticos (iguais, disjuntas, vazias, contornos deslocados), incluindo convenção para denominador zero.
- **Formatos:** leitura e saída compatíveis para RGB/BGR, PNG/JPG e máscaras binárias/alfa quando suportadas.
- **Falhas:** detector sem rosto e imagem inválida produzem status registrado; o pipeline não trata falhas como sucessos.
- **Reprodutibilidade:** a mesma configuração e semente geram a mesma seleção/transformação estocástica, quando determinismo for possível.
- **CLI:** ao menos um teste curto verifica que cada script aceita configuração e gera arquivos com o esquema esperado.
- **Isolamento:** o módulo `analysis/` consegue gerar gráficos e tabelas a partir de resultados simulados, sem carregar modelos.

## 9. Orientações explícitas para o Codex

Ao usar este documento como especificação de scaffolding:

1. **Crie a estrutura base do projeto**, respeitando os nomes e as responsabilidades descritas.
2. **Crie primeiro** `pyproject.toml`, `.gitignore`, `README.md`, pastas de código e testes, configurações iniciais e arquivos `README.md` nas pastas de dados/modelos/resultados.
3. **Não implemente todos os métodos candidatos de uma só vez.** Crie classes e módulos específicos apenas à medida que os métodos forem selecionados.
4. **Não invente datasets, checkpoints, resultados ou referências**. Onde faltar informação, usar configurações de exemplo claramente identificadas e instruções de preenchimento, sem simular resultados científicos.
5. **Mantenha scripts de `scripts/` enxutos**, com lógica reutilizável dentro de `src/face_processing_benchmark/`.
6. **Evite dependências pesadas obrigatórias:** instalar bibliotecas de modelos como extras opcionais quando fizer sentido.
7. **Use caminhos relativos à raiz ou configuráveis**, sem caminhos pessoais fixos.
8. **Não altere os arquivos `ETAPAS.md` e `ESTRUTURA_REPOSITORIO.md` automaticamente**, salvo quando a mudança for solicitada.
9. **Não crie gráficos, resultados fictícios ou arquivos LaTeX extensos** na etapa inicial. As pastas `report/` e `presentation/` podem começar com README ou `.gitkeep` e ser preenchidas posteriormente.
10. **Valide o scaffold** com importação do pacote, instalação em modo editável (se disponível) e testes simples, relatando o que está pronto e o que depende das próximas etapas.

## 10. Ordem sugerida para materializar a estrutura

| Momento | Criar/ativar |
|---|---|
| **Inicialização** | Raiz, `pyproject.toml`, `configs/`, `src/.../core/`, `scripts/`, `tests/` e READMEs de dados/modelos/resultados |
| **Seleção de métodos** | `docs/methods.md`, entradas de configuração e implementações individuais escolhidas |
| **Preparação de dados** | `data/`, manifests, validadores e testes de transformações |
| **Implementação dos benchmarks** | `evaluation/`, `experiments/`, CLIs e testes de métricas |
| **Execução** | diretórios reais `results/<run_id>/`, dados e logs por execução |
| **Análise e comunicação** | `analysis/`, assets de relatório, `report/` e `presentation/` |

---

**Critério geral de sucesso:** uma pessoa deve conseguir identificar onde adicionar um método, configurar um experimento, executá-lo isoladamente, reproduzir seu resultado e gerar os gráficos sem precisar modificar algoritmos não relacionados.
