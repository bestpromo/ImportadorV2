# ImportadorV2 - Integração de Catálogo AWIN

Automatiza o download, filtragem e preparação de catálogos de produtos da AWIN para uso em sistemas de e-commerce.

## Funcionalidades

- Baixa a lista de catálogos da AWIN (.gz), extrai e salva como CSV.
- Filtra apenas lojas com status **ativo**.
- Baixa e extrai catálogos das lojas ativas.
- Gera logs detalhados do processo.

## Estrutura de Pastas

```
ImportadorV2/
│
├── data/             # Arquivos baixados (NÃO versionar)
│   └── awin/
│       ├── lists/    # Listas principais e logs de execução
│       └── inputs/   # Catálogos das lojas ativas
│
├── src/
│   └── awin_catalog_downloader.py
│
├── .env              # Variáveis de acesso (NÃO versionar)
├── .gitignore
├── requirements.txt
└── README.md
```

## Regras Gerais

- **NUNCA versionar arquivos em `data/` ou `.env`.**
- Sempre conferir se há espaço em disco antes de rodar o script.
- Logs de execução ficam em `data/awin/lists/`.
- O script pode ser agendado via cron ou orquestradores.
- Para novas integrações ou ajustes, documente no README e mantenha o código limpo e comentado.

## Setup

1. **Clone o repositório**
2. **Crie o arquivo `.env` na raiz:**
    ```
    AWIN_API_KEY=seu_apikey
    AWIN_PUBLISHER_ID=seu_publisher_id
    ```
3. **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## Execução

Execute o script principal:

```bash
python src/awin_catalog_downloader.py
```

Acompanhe o progresso pelo terminal e pelo log gerado.

## Contribuição

- Siga o padrão de código e mantenha as dependências atualizadas.
- Descreva mudanças relevantes neste README.
- Abra PRs claros e objetivos.

---

## Licença

MIT License. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

**Autor:** André Luiz Faustino