# Download e organização dos datasets

Este documento descreve como obter e organizar os datasets utilizados no **face-processing-benchmark**. Os arquivos originais devem ser preservados, sem alterações; as cópias ou informações derivadas ficam em `processed/`.

## Datasets utilizados

| Dataset | Utilização | Quantidade prevista | Fonte |
|---|---|---:|---|
| **LFW (funneled)** | Avaliação de detecção/centralização com deslocamentos sintéticos | Seleção reproduzível de 1.000 imagens | [scikit-learn — LFW](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_lfw_people.html) |
| **PPM-100** | Desenvolvimento e testes dos métodos de remoção de fundo | 100 pares imagem/máscara | [PPM — repositório oficial](https://github.com/ZHKKKe/PPM) |
| **P3M-500-NP** | Experimentos finais de remoção de fundo e influência do enquadramento | 500 pares imagem/máscara | [P3M-Net — repositório oficial](https://github.com/ViTAE-Transformer/P3M-Net) |

**Atenção:** a LFW padrão não oferece caixas faciais de referência precisas. Nos testes de centralização com transformações sintéticas, a posição conhecida da foto inserida serve como referência aproximada, não como anotação manual da face.

## Estrutura de diretórios

Execute os comandos a partir da raiz do repositório.

```text
datasets/
├── lfw/
│   ├── raw/
│   │   ├── lfw-funneled.tgz
│   │   └── lfw_funneled/
│   └── processed/
│       └── manifest.csv
├── ppm100/
│   ├── raw/
│   └── processed/
│       └── manifest.csv
└── p3m500np/
    ├── raw/
    └── processed/
        └── manifest.csv
```

- **`raw/`**: arquivos baixados e extraídos, mantendo os nomes e a estrutura originais.
- **`processed/`**: índices (`manifest.csv`) e futuros artefatos derivados; não substituir os originais.
- **`manifest.csv`**: índice gerado pelo script com `id`, `image` e `matte`; os caminhos são relativos a `datasets/`.

## Preparar as pastas

O utilitário do projeto fica em `scripts/prepare_datasets.py`.

```bash
python scripts/prepare_datasets.py
```

Esse comando cria os diretórios, mas não baixa nenhum dataset.

## LFW (funneled)

O script baixa a distribuição **LFW funneled** utilizada pelo scikit-learn, verifica o SHA-256 do arquivo e extrai as imagens.

```bash
python scripts/prepare_datasets.py --download-lfw
```

Os arquivos ficam em `datasets/lfw/raw/lfw_funneled/`. O download contém o conjunto disponível; a seleção das 1.000 imagens usadas nos experimentos será realizada posteriormente com uma semente fixa, e não durante a aquisição.

## Download automático pelo Google Drive

O script utiliza [gdown](https://github.com/wkentaro/gdown) para baixar arquivos públicos do Google Drive. Não é necessário configurar credenciais da API Google Drive, desde que o link esteja acessível publicamente.

Instale a dependência no ambiente virtual:

```bash
python -m pip install -e '.[dataset-downloads]'
```

### PPM-100

```bash
python scripts/prepare_datasets.py --download-ppm100
```

Fonte oficial: [PPM-100 no Google Drive](https://drive.google.com/file/d/1JUx-EPoV9QAhQgmW0AyOen-xKQUzZia-/view?usp=sharing).

O programa baixa o pacote para `datasets/ppm100/raw/`, confere se é um arquivo ZIP ou TAR reconhecido e extrai o conteúdo. Se o Google Drive limitar o download, consulte a [página dos autores](https://github.com/ZHKKKe/PPM).

### P3M-500-NP

**Atenção:** o link oficial é para o pacote **P3M-10k completo**, não somente para as 500 imagens NP. Portanto, esse download pode ser bem maior. O script evita extrair as demais partes, mas ainda precisa baixar o pacote inteiro.

```bash
python scripts/prepare_datasets.py --download-p3m500np --allow-full-p3m-archive
```

Fonte oficial: [P3M-10k no Google Drive](https://drive.google.com/file/d/1odzHp2zbQApLm90HH_Cvr5b5OwJVhEQG/view?usp=sharing); [repositório dos autores](https://github.com/ViTAE-Transformer/P3M-Net).

O script procura a pasta `P3M-500-NP` dentro do arquivo e extrai apenas seus arquivos para `datasets/p3m500np/raw/`. Se o formato ou a organização do pacote forem diferentes, será necessário adaptar o extrator; ele não baixa automaticamente uma alternativa não oficial.

Antes de obter o P3M, leia o [acordo de distribuição do dataset](https://jizhizili.github.io/files/p3m_dataset_agreement/P3M-10k_Dataset_Release_Agreement.pdf).

### Baixar tudo

```bash
python scripts/prepare_datasets.py --download-all --allow-full-p3m-archive
python scripts/prepare_datasets.py --index
```

O download pode falhar por limites de acesso ou tráfego do Google Drive. Nesse caso, os links oficiais acima podem ser usados manualmente. Os arquivos originais não devem ser colocados no Git.

## Gerar índices dos arquivos

Depois de colocar os arquivos nas respectivas pastas `raw/`, execute:

```bash
python scripts/prepare_datasets.py --index
```

O comando tenta associar imagens às respectivas máscaras pelo nome-base do arquivo e gera:

```text
datasets/lfw/processed/manifest.csv
datasets/ppm100/processed/manifest.csv
datasets/p3m500np/processed/manifest.csv
```

Se houver arquivos sem par ou nomes ambíguos, o script registra o problema em `processed/pairing_issues.txt`. Caso a estrutura recebida use convenções diferentes das reconhecidas pelo script, será necessário adaptar o indexador; **não renomeie os arquivos originais apenas para forçar uma correspondência**.

Os índices são utilizados pelo validador descrito na próxima seção, que verifica a integridade dos arquivos, as dimensões e os valores das máscaras alfa.

## Validar a integridade dos datasets

Depois do download e da indexação, execute `scripts/validate_datasets.py` para conferir os arquivos e os pares imagem–máscara. Instale o extra `datasets`, que inclui Pillow e usa o NumPy declarado no projeto:

```bash
python -m pip install -e '.[datasets]'
python scripts/prepare_datasets.py --index
```

### Executar a validação

Colocar `validate_datasets.py` na pasta `scripts/`:

```bash
# Validar os três datasets
python scripts/validate_datasets.py --dataset all

# Validar apenas um dataset, mesmo durante o download dos outros
python scripts/validate_datasets.py --dataset ppm100
python scripts/validate_datasets.py --dataset lfw
python scripts/validate_datasets.py --dataset p3m500np

# Usar outra localização para os dados
python scripts/validate_datasets.py --root /caminho/datasets --dataset all
```

Um dataset ainda não baixado, ou sem `manifest.csv`, será identificado como `FAILED`. O código de saída é `0` quando todos os datasets selecionados passam e `1` quando algum falha.

### O que é verificado

- A quantidade mínima de imagens: **LFW ≥ 1.000**, **PPM-100 = 100 pares**, **P3M-500-NP = 500 pares**.
- Existência, abertura e integridade básica dos arquivos listados no manifesto.
- Unicidade de identificadores e caminhos de imagem/máscara.
- Presença de uma máscara para cada imagem nos datasets de matting.
- Igualdade de largura e altura entre cada imagem e sua máscara.
- Formato de máscara, valores não finitos e máscaras constantes.
- Problemas de pareamento registrados pelo indexador.

Máscaras constantes e modos não usuais são sinalizados como **avisos**, pois podem ser dados válidos dependendo do conjunto. Avisos não fazem a validação falhar automaticamente. O script não utiliza máscaras verdadeiras para ajustar nenhum método.

**Limitação:** o validador depende dos arquivos incluídos no manifesto. Se o indexador não encontrar determinadas imagens, elas não serão inspecionadas; confira também os avisos de pareamento e a quantidade esperada. Para LFW, não há verificação de caixas faciais verdadeiras. A validação não garante a qualidade semântica das anotações.

### Relatórios gerados

```text
datasets/
├── lfw/processed/validation/
│   ├── summary.json
│   └── files.csv
├── ppm100/processed/validation/
│   ├── summary.json
│   └── files.csv
└── p3m500np/processed/validation/
    ├── summary.json
    └── files.csv
```

`summary.json` apresenta a situação geral, quantidades e tipos de problemas; `files.csv` registra o resultado individual de cada imagem. Os relatórios podem ser regenerados a qualquer momento. Os arquivos `raw/` permanecem intactos.


## Criar amostras para testes técnicos

Com os manifestos existentes, execute a partir da raiz do repositório:

```bash
python scripts/create_test_samples.py
```

O script seleciona 20 amostras válidas da LFW e 20 do PPM-100 com semente 42.
Cada lista é gravada em `datasets/{dataset}/processed/test_samples.csv` com as
colunas `id,image,matte` e caminhos relativos a `datasets/`. A lista do PPM-100
mantém cada imagem associada à sua máscara. Os arquivos originais são apenas lidos
e o P3M-500-NP fica reservado para a avaliação final.

As listas existentes são reutilizadas após conferência com o manifesto e
verificação dos arquivos. Use `--recreate` para refazer a seleção. Com os mesmos
registros válidos, a seleção é reproduzível mesmo se a ordem do manifesto mudar.
Use `--dataset lfw` ou `--dataset ppm100` para processar apenas uma base, e
`--root` se os datasets estiverem em outro diretório. O script usa as mesmas
dependências do validador, Pillow e NumPy.

## Cuidados com os dados

- Não modificar imagens e máscaras dentro de `raw/`.
- Não misturar os subconjuntos `P3M-500-NP` e `P3M-500-P`.
- Não utilizar o P3M-500-NP para ajustar parâmetros após começar a avaliação final; reservar o PPM-100 para desenvolvimento e testes.
- Registrar a fonte, a versão e as condições de uso dos arquivos obtidos.
- Adicionar `datasets/` ao `.gitignore`, evitando publicar imagens e máscaras sem autorização.
- Verificar as licenças e os termos de cada dataset antes de redistribuí-lo.

## Referências oficiais

- [LFW — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_lfw_people.html)
- [PPM-100 — ZHKKKe/PPM](https://github.com/ZHKKKe/PPM)
- [P3M-500-NP — ViTAE-Transformer/P3M-Net](https://github.com/ViTAE-Transformer/P3M-Net)
