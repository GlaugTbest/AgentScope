# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Pessoas desenvolvendo ou avaliando agentes de IA localmente, que precisam confirmar rapidamente o que cada agente executou e onde falhou.

## Product Purpose

AgentScope torna traces, spans, custos e falhas de agentes visíveis em um ambiente local testável. O sucesso é alguém criar um agente, executar uma demonstração e inspecionar seus dados persistidos sem serviços externos.

## Positioning

Uma bancada local de observabilidade que combina criação de agente e trace real em um único fluxo de teste.

## Operating Context

Uso local em navegador, com FastAPI, SQLite e dashboard Next.js rodando em loopback.

## Capabilities and Constraints

Agentes são identificados por nome e descrição localmente. A demonstração é determinística e não usa API paga. O produto permanece monousuário, sem login e sem serviço externo.

## Evidence on Hand

Há um SDK Python, endpoints de ingestão/consulta e um demo-agent local. Os dados de demonstração são explicitamente sintéticos.

## Product Principles

- Dados reais antes de decoração.
- O próximo passo de teste deve estar sempre visível.
- Falhas precisam orientar a investigação.
- O ambiente local não exige infraestrutura extra.
