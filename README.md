# Segmentação de pluma de fumaça com SAM — versão aprimorada

Continuação do notebook inicial da atividade: mesma stack (**Ultralytics**), *prompts* e avaliação
reescritos. A imagem do notebook inicial (`MyDrive/pluma.jpg`) não está mais disponível, então a
análise usa uma imagem pública equivalente, com *prompts* e máscara de referência já calibrados.


[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fnsantos1/segmentacao-pluma-sam/blob/main/Segmentacao_Pluma_SAM.ipynb)

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
ERA5/netCDF — aquilo é outra frente do projeto; aqui é só a segmentação da pluma.

## A imagem

*Smoke plume from SoCal wildfire, outubro/2007* (Wikimedia Commons, domínio público). Reúne **os três
distratores citados no enunciado ao mesmo tempo** — céu azul, casas/telhados e uma faixa de *haze*
esbranquiçada quase indistinguível da base da pluma — e ainda uma placa de trânsito que **oclui**
parte da pluma.

Para usar outra imagem: `CFG["IMAGEM"] = "upload"` (ou caminho/URL). Aí os *prompts* calibrados não
valem mais, e a Etapa 1 calcula um palpite automático e mostra a imagem com grade de coordenadas para
você ajustar `PROMPTS` na Etapa 2.

## As três configurações de *prompt*

| | *Prompt* | Hipótese testada |
|---|---|---|
| A | só a caixa | o retângulo basta? Ele contém muito céu junto. |
| B | só pontos positivos | sem limite espacial, até onde a região espalha por semelhança? |
| C | caixa + 5 positivos + 8 negativos | dizer o que **não** é pluma resolve a ambiguidade? |

## Etapas

| Etapa | Conteúdo |
|---|---|
| 1 | instalação, imagem, *prompts* calibrados (ou palpite automático) e grade de coordenadas |
| 2 | os três *prompts* e a predição (`set_image` uma vez, três decodificações) |
| 3 | original + *prompts* / máscara binária / sobreposição, lado a lado, por configuração |
| 4.1 | métricas: IoU, Dice, precisão, recall, área, componentes, compacidade, invasão de céu/*haze*/edificação, IoU entre configurações, separabilidade dentro×fora, e mapa de erro |
| 4.2 | efeito do contraste: mesma cena e mesmo *prompt*, contraste reduzido à metade |
| 5 | conclusões e o que faria a seguir |

## Como rodar

`Ambiente de execução → Executar tudo`. GPU ajuda mas não é obrigatória (usa `sam2_t.pt` em CPU e
`sam2_b.pt` em GPU).

## Limitação declarada

A máscara de referência é um polígono traçado **à mão** e **aproximado** — na base da pluma não
existe fronteira objetiva entre fumaça e *haze*. Os valores de IoU/Dice servem para comparar as
configurações **entre si**, não como medida absoluta; essa incerteza do próprio rótulo é parte da
resposta à pergunta "por que é difícil". Além disso, os resultados vêm de **uma** imagem: uma
avaliação robusta exigiria N imagens com média ± desvio.
