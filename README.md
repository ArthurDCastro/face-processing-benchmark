# Face Processing Benchmark

Projeto científico desenvolvido como trabalho final da disciplina de Visão
Computacional do Departamento de Informática da Universidade Federal do Paraná
(UFPR).

O objetivo é comparar detecção facial, centralização e recorte de imagens,
segmentação de pessoas e o efeito do pré-processamento na segmentação. O projeto
é independente de aplicações externas e terá execução pelo terminal, sem depender
de interface gráfica.

## Escopo atual

Esta é a estrutura inicial descrita nas seções 9 e 10 da
[especificação do repositório](ESTRUTURA_REPOSITORIO.md). Ainda não há métodos,
carregadores de dados, métricas, experimentos, downloads de modelos ou resultados
científicos implementados. Os cadastros de datasets e métodos estão
intencionalmente vazios.

A documentação está em português brasileiro. Nomes de arquivos e pastas,
código, comentários, docstrings, mensagens de log e configurações permanecem em
inglês. Os documentos de planejamento existentes conservam seus nomes originais.

## Instalação e validação

É necessário Python 3.11 ou superior. Na raiz do repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -c "import face_processing_benchmark"
fpb-check-config configs/datasets.yaml
python scripts/check_config.py configs/methods.yaml
python -m pytest
python -m ruff check .
```

A validação de configurações verifica apenas o esquema da estrutura inicial;
não valida imagens, arquivos de modelos ou protocolos experimentais. O comando
também pode ser executado como
`python -m face_processing_benchmark.core.config CONFIG`. Ele apenas lê o arquivo
informado e não gera resultados. Bibliotecas de modelos serão adicionadas como
dependências opcionais após a seleção dos métodos.

## Organização e próximas etapas

- `configs/`: exemplos de cadastros e espaço para futuras configurações experimentais.
- `src/face_processing_benchmark/core/`: infraestrutura compartilhada e futuros contratos.
- `scripts/`: pontos de entrada enxutos que chamam o código reutilizável do pacote.
- `tests/`: testes pequenos de infraestrutura, sem datasets ou modelos.
- `datasets/`, `models/`, `results/`: orientações de armazenamento e procedência.

Seguir [ETAPAS.md](ETAPAS.md) e a seção 10 da especificação de forma incremental:
selecionar os métodos antes de adicionar implementações individuais em `methods/`;
criar `data/` durante a preparação dos dados; adicionar `evaluation/`,
`experiments/` e seus comandos independentes durante a implementação dos
benchmarks. Criar `analysis/`, `report/` e `presentation/` quando houver necessidade
de analisar resultados e produzir os materiais de comunicação do trabalho.

Os futuros contratos devem explicitar imagens RGB, unidades de coordenadas,
semântica das máscaras, transformações geométricas, regiões válidas, preservação
das entradas e estados de falha interpretáveis. O pré-processamento deve
transformar as máscaras de referência com a mesma geometria das imagens e
registrar as áreas removidas. Consultar a seção 5 da especificação antes de
implementar esses contratos.

Os caminhos devem ser relativos ao repositório ou configuráveis. Dados e
anotações originais permanecem imutáveis; dados derivados e saídas de cada execução
têm locais separados. Nenhuma aplicação externa é necessária e nenhum dado ou
peso de modelo é baixado automaticamente.

## Licenciamento

A licença do código ainda não foi escolhida; nenhuma concessão de licença está
implícita. As licenças de datasets e checkpoints devem ser registradas
separadamente antes do uso ou da redistribuição.
