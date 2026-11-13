# Responsabilidades do núcleo

`config.py` valida o formato das configurações iniciais sem carregar métodos,
imagens ou checkpoints. Cadastros preenchidos são rejeitados intencionalmente
até que seus esquemas sejam definidos.

Criar `types.py` e `interfaces.py` ao implementar os contratos comuns de
`FaceDetector`, `ImageAligner` e `PersonSegmenter`. Definir explicitamente
coordenadas, canais RGB, tipos de máscara, transformações, regiões válidas e
estados de sucesso ou falha, conforme a seção 5 da especificação do repositório.
Os métodos devem receber configurações explícitas e preservar as entradas
fornecidas por quem os chama.

Adicionar `registry.py` com identificadores estáveis quando os métodos forem
selecionados; o registro não deve inicializar modelos. Adicionar `geometry.py`
com transformações genéricas testadas ao preparar os dados e a centralização.
Manter a lógica específica de modelos fora deste pacote.
