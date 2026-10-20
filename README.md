# Segmentação de pluma de fumaça com SAM — versão aprimorada

Continuação do notebook inicial da atividade. Mesma stack (**Ultralytics**) e mesma imagem
(`MyDrive/pluma.jpg`); o que muda é **como o SAM é acionado** e **como o resultado é avaliado**.

> Substitua `SEU_USUARIO/SEU_REPO` depois de subir o repositório.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SEU_USUARIO/SEU_REPO/blob/main/Segmentacao_Pluma_SAM.ipynb)

## O que estava quebrado no notebook inicial

| Célula | O que acontecia | Causa |
|---|---|---|
| 13 | `FileNotFoundError: 'sam_b.pt'` | `SAM3SemanticPredictor` espera pesos do SAM 3 (download deu 404); `sam_b.pt` não faz *prompt* de texto |
| 14 | `(no detections)` → nenhuma máscara gerada | o detector `YOLOv8m-smoke-detection` não encontrou a pluma |
| 12 | "4 cars, 1 truck" | `yolo26n` é COCO — não existe classe "fumaça" |
| 7 | `copyfile("pluma.jpg", "pluma.png")` | só renomeia: o arquivo continua JPEG |

**Correção:** *prompts* geométricos (caixa e pontos) em vez de detector automático ou *prompt* de
texto, com `SAM2Predictor` e `set_image()` chamado uma única vez.

## ⚠️ Antes de publicar

O notebook inicial tem uma **chave da API do CDS/Copernicus escrita no código** (célula 4). Chave em
repositório público é chave vazada: **revogue essa e gere outra** no painel do CDS, e passe a lê-la de
variável de ambiente (`os.environ["CDSAPI_KEY"]`). Este notebook não contém a chave nem a parte de
ERA5/netCDF — ela é outra frente do projeto; aqui é só a segmentação da pluma.

## As três configurações de *prompt*

| | *Prompt* | Hipótese testada |
|---|---|---|
| A | só a caixa | o retângulo basta? Ele contém muito céu junto. |
| B | só pontos positivos | sem limite espacial, até onde a região espalha por semelhança? |
| C | caixa + positivos + negativos | dizer o que **não** é pluma resolve a ambiguidade? |

## Etapas

| Etapa | Conteúdo |
|---|---|
| 1 | instalação, imagem, **palpite de caixa/pontos calculado na própria imagem** e grade de coordenadas |
| 2 | os três *prompts* e a predição (`set_image` uma vez, três decodificações) |
| 3 | original + *prompts* / máscara binária / sobreposição, lado a lado, para cada configuração |
| 4.1 | métricas sem rótulo: área, componentes, compacidade, invasão de céu/solo, IoU entre configurações e separabilidade dentro×fora |
| 4.2 | efeito do contraste: mesma cena e mesmo *prompt*, contraste reduzido à metade |
| 5 | conclusões e o que faria a seguir |

## Como rodar

`Ambiente de execução → Executar tudo`. GPU ajuda mas não é obrigatória (usa `sam2_t.pt` em CPU e
`sam2_b.pt` em GPU).

**Ajuste obrigatório:** confira na Etapa 1 se o palpite caiu na pluma. Se não caiu, corrija `PROMPTS`
na Etapa 2 — as coordenadas são frações de 0 a 1, lidas direto da grade.

## Limitação declarada

Sem máscara de referência traçada à mão não há IoU contra a verdade; por isso a avaliação usa
medidas que não dependem de rótulo (invasão de céu/solo, concordância entre *prompts*, separabilidade
fotométrica dentro×fora da máscara). Traçar uma referência é o primeiro item do "o que faria a
seguir".
