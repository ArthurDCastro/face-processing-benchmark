# Datasets

Nenhum dataset foi selecionado ou baixado. Antes de adicionar uma base, registrar
seu identificador estável, origem, versão, licença, requisitos de acesso, política
de divisão dos dados, organização esperada e instruções explícitas de preparação.
Não inventar fontes nem baixar dados implicitamente.

Criar os seguintes diretórios apenas quando necessário:

- `raw/`: imagens originais imutáveis; ignorado pelo Git.
- `annotations/`: referências originais imutáveis; ignorado pelo Git.
- `processed/`: dados derivados regeneráveis, com procedência; ignorado pelo Git.
- `manifests/`: identificadores estáveis de amostras, caminhos, divisões e metadados públicos permitidos.
- `samples/`: pequenas amostras de teste, apenas quando a redistribuição for autorizada.

Preservar as máscaras de referência originais. O pré-processamento espacial deve
aplicar a mesma geometria às imagens e às referências, com interpolação das
máscaras e regiões válidas documentadas. Datasets completos e metadados restritos
devem permanecer fora do controle de versão.
