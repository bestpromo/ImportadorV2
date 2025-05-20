# ImportadorV2 - Integração de Catálogo AWIN

Este projeto realiza a ingestão automatizada de catálogos de produtos fornecidos pela AWIN, baixando arquivos CSV compactados, filtrando lojas ativas e salvando os catálogos prontos para uso em sistemas de e-commerce.

## Funcionalidades

- Baixa a lista de catálogos da AWIN (arquivo .gz), descompacta e salva como CSV.
- Filtra apenas lojas com status **active**.
- Baixa e descompacta os catálogos das lojas ativas.
- Salva logs detalhados do processo.

## Estrutura de Pastas

```
ImportadorV2/
│
├── data/             # diretório com arquivos baixados (Não versionado)  
│   └── awin/
│       ├── lists/    # Lista principal e logs de execução
│       └── inputs/   # Catálogos das lojas ativas
│
├── src/
│   └── baixar_catalogos_awin.py
│
├── .env              # variáveis de acesso (NÃO versionar)
├── .gitignore
├── requirements.txt
└── README.md
```

## Configuração

1. **Clone o repositório**
2. **Crie o arquivo `.env` na raiz do projeto:**
    ```
    AWIN_API_KEY=sua_apikey
    AWIN_PUBLISHER_ID=seu_publisher_id
    ```
3. **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## Execução

Execute o script principal:

```bash
python src/baixar_catalogos_awin.py
```

Acompanhe o progresso pelo terminal e pelo arquivo de log gerado em `data/awin/lists/`.

## Observações

- O arquivo `.env` **NÃO** deve ser versionado.
- Os arquivos baixados podem ser grandes, certifique-se de ter espaço em disco.
- O script pode ser adaptado para rodar via cron ou orquestradores.

---

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

**Autor:** André Luiz Faustino