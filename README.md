# Face Processing Benchmark

Projeto científico desenvolvido como trabalho final da disciplina de Visão
Computacional do Departamento de Informática da Universidade Federal do Paraná
(UFPR). O projeto compara métodos clássicos e de aprendizado profundo para
centralização facial e remoção de fundo, com execução prevista pelo terminal.

## Experimentos

| Experimento | Avaliação | Dados |
| --- | --- | --- |
| E1 | Centralização sintética com quatro detectores e referência facial aproximada | 1.000 imagens da LFW funneled |
| E2 | Remoção de fundo com quatro métodos nas imagens originais | PPM-100 para validação técnica e P3M-500-NP para avaliação final |
| E3 | Comparação pareada entre imagem original (C0), centralização com preenchimento (C1) e centralização por recorte (C2) | PPM-100 para validação técnica e P3M-500-NP para avaliação final |

Em E3, um único detector escolhido a partir de E1 prepara C1 e C2. A comparação
principal avalia a região original comum às três condições. A geometria das
imagens também é aplicada às referências de segmentação para o cálculo das
métricas. Os parâmetros serão congelados antes da avaliação final.
[Protocolo experimental](docs/PROTOCOLO_EXPERIMENTAL.md) ·
[Métricas](docs/METRICAS_AVALIACAO.md)

## Estado atual

Os oito métodos estão selecionados e os seis YAMLs já registram os datasets, os
métodos e o protocolo de E1, E2 e E3. Os campos `null` acompanhados de `TODO`
registram decisões em aberto. O carregador `fpb-check-config` ainda suporta apenas
cadastros vazios da versão 1. A leitura completa dos YAMLs experimentais da versão 2,
os demais adaptadores, as métricas e os executores estão pendentes. Os quatro detectores faciais
já podem ser executados isoladamente com a lista técnica da LFW.
[Métodos selecionados](docs/METODOS_SELECIONADOS.md) ·
[Especificação dos YAMLs](docs/CONFIGURACAO_EXPERIMENTOS.md)

A cópia local contém manifestos e relatórios de integridade para a LFW
(13.233 imagens), o PPM-100 (100 pares) e o P3M-500-NP (500 pares). LFW e PPM-100
têm listas técnicas de 20 amostras cada. A seleção das 1.000 imagens do E1
é uma etapa distinta. [Datasets selecionados](docs/DATASETS_SELECIONADOS.md)

## Instalação e preparação de dados

Use Python 3.11 ou superior. Na raiz do repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,datasets]'
```

Para instalar também os detectores e o suporte a downloads pelo Google Drive:

```bash
python -m pip install -e '.[all]'
```

Com os dados originais já disponíveis em `datasets/<dataset>/raw/`:

```bash
python scripts/prepare_datasets.py --index
python scripts/validate_datasets.py --dataset all
python scripts/create_test_samples.py
```

Os manifestos, relatórios de integridade e listas técnicas ficam em
`datasets/<dataset>/processed/`. O último comando valida e reutiliza as listas
existentes. Passe `--recreate` para refazê-las com a semente 42. Para obter os
dados e conhecer as opções dos scripts, consulte o
[guia de download e preparação](docs/DOWNLOAD_DATASETS.md).

Os testes atuais cobrem a infraestrutura inicial. Parte deles usa os cadastros
preenchidos como exemplos do esquema antigo e precisa ser ajustada junto com a
atualização do carregador.

## Organização

- `configs/` contém os cadastros e os YAMLs experimentais.
- `docs/` reúne o protocolo, as métricas e a documentação de métodos e dados.
- `scripts/` contém os utilitários de preparação, validação e amostragem de dados, além do verificador de configuração inicial.
- `src/face_processing_benchmark/core/` e `tests/` contêm o carregador inicial e seus testes.
- `datasets/`, `models/` e `results/` são os locais previstos para dados, pesos e saídas experimentais, respectivamente.

A documentação do projeto usa português brasileiro. Código, configurações,
comentários e mensagens dos scripts usam inglês.
[Estrutura atual e planejada](ESTRUTURA_REPOSITORIO.md) · [Etapas do projeto](ETAPAS.md)

## Licenciamento

A licença do código ainda está pendente. Registre separadamente os termos de uso
dos datasets e checkpoints antes de redistribuir imagens, anotações ou pesos.

## Teste isolado do Viola–Jones

Com a lista técnica da LFW preparada:

```bash
python -m pip install -e '.[viola-jones]'
python scripts/test_viola_jones.py
```

Cada execução escreve `per_image.csv`, `summary.json` e os PNGs anotados em
`results/viola_jones/<run_id>/`. A caixa verde indica a maior face e as caixas
laranjas indicam as demais. A taxa reportada mede a presença de detecções nas
20 imagens originais, sem anotação manual de caixas.

## Teste isolado do HOG + SVM

Instale o extra com dlib e OpenCV. Se o dlib precisar ser compilado, a
instalação também exige CMake e um compilador C++.

```bash
python -m pip install -e '.[dev,hog-svm]'
python -m pytest -q tests/test_hog_svm.py
python scripts/test_hog_svm.py
```

O script lê as 20 imagens da lista técnica da LFW. Cada execução gera
`per_image.csv`, `summary.json` e imagens anotadas em
`results/hog_svm/<run_id>/`. Use `--no-visuals` para gerar apenas os relatórios.
O resumo registra a versão do dlib e o número de ampliações configurado em
`configs/methods.yaml`. O valor técnico inicial é uma ampliação, conforme
o [exemplo oficial do dlib](https://dlib.net/face_detector.py.html).

## Teste isolado do YuNet

O YuNet usa o ONNX oficial `face_detection_yunet_2023mar.onnx` do OpenCV Zoo.
Ele deve ficar em `models/checkpoints/`, diretório ignorado pelo Git. Em uma
cópia nova do repositório, obtenha o arquivo com:

```bash
mkdir -p models/checkpoints
curl -fL 'https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx' \
  -o models/checkpoints/face_detection_yunet_2023mar.onnx
```

O adaptador verifica o SHA-256 declarado em `configs/methods.yaml` ao carregar
o modelo. Com o ONNX e a lista técnica da LFW disponíveis:

```bash
python -m pip install -e '.[dev,yunet]'
python -m pytest -q tests/test_yunet.py
python scripts/test_yunet.py
```

As saídas ficam em `results/yunet/<run_id>/` com `per_image.csv`,
`summary.json` e imagens anotadas. Use `--no-visuals` para gerar só os relatórios.

## Teste isolado do SCRFD-500MF

Com o [checkpoint oficial](models/README.md#scrfd-500mf) e a lista técnica da
LFW disponíveis:

```bash
python -m pip install -e '.[dev,scrfd]'
python -m pytest -q tests/test_scrfd.py
python scripts/test_scrfd.py
```

O script roda com ONNX Runtime em CPU e grava `per_image.csv`, `summary.json`
e imagens anotadas em `results/scrfd/<run_id>/`. Use `--no-visuals` para gerar
apenas os relatórios. A configuração técnica inicial segue o exemplo oficial
com entrada de 640 × 640, limiar de confiança 0,5 e NMS 0,4.
