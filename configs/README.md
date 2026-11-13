# Configurações

`datasets.yaml` e `methods.yaml` são exemplos vazios da estrutura inicial, não
configurações de benchmarks executáveis. `schema_version: 1` identifica o formato
atual; `kind` seleciona o mapeamento de cadastros. Apenas cadastros vazios são
aceitos até que seus esquemas sejam definidos na etapa correspondente do projeto.

Usar `fpb-check-config PATH` para verificar um arquivo da estrutura inicial.
Caminhos relativos de arquivos de configuração são resolvidos a partir do
diretório de trabalho atual. Os futuros caminhos de datasets e checkpoints devem
ser resolvidos a partir de uma raiz explícita do repositório ou dos dados, nunca
de um diretório pessoal do desenvolvedor. Downloads implícitos não são permitidos.
