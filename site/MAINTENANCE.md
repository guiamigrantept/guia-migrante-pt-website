# Guia Migrante PT — manutenção editorial V12

Última revisão integral: 2026-08-20

## Regra de revisão
- Conteúdo legal/migratório, contactos, taxas e janelas de renovação: rever a cada 30 dias.
- Conteúdo prático geral: rever a cada 90 dias.
- Privacidade, termos e acessibilidade: rever a cada 180 dias ou quando houver alteração funcional.
- Se uma fonte oficial mudar antes da data prevista, atualizar imediatamente a página afetada.

## Processo
1. Abrir `estado-informacao.html`.
2. Priorizar páginas cuja data de revisão está próxima ou ultrapassada.
3. Confirmar sempre na fonte oficial ligada na própria página.
4. Atualizar o texto, a data `meta[name="last-reviewed"]` e `content-status.json`.
5. Executar QA de links, âncoras, PT↔EN, JavaScript e acessibilidade estática.
6. Criar novo deployment de produção.

## Importante
A sinalização automática de “conteúdo potencialmente desatualizado” não verifica a lei nem substitui a revisão editorial.
