# RASFF Alert — Config Público

Este repositório contém os **dicionários de filtros** usados pela app RASFF Alert.

Os ficheiros são públicos para permitir atualizações OTA (over-the-air) sem necessitar de uma nova versão da app na loja.

## Ficheiros

| Ficheiro | Descrição |
|---|---|
| `rasff_filters_en.json` | Dicionário de filtros em inglês |
| `rasff_filters_pt.json` | Dicionário de filtros em português |

## Atualização Automática

O workflow `monitor_rasff_filters.yml` verifica semanalmente se a API da UE mudou e atualiza estes ficheiros automaticamente via commit.
