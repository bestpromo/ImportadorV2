import os
import csv
from collections import Counter

INPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'awin', 'inputs')
RELATORIO_HTML = os.path.join(INPUTS_DIR, "relatorio_colunas.html")

def listar_csvs(diretorio):
    return [os.path.join(diretorio, f) for f in os.listdir(diretorio) if f.endswith('.csv')]

def ler_cabecalho_csv(caminho_arquivo):
    with open(caminho_arquivo, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return next(reader)

def main():
    arquivos = listar_csvs(INPUTS_DIR)
    colunas_por_arquivo = {}
    todas_colunas = set()
    contador_colunas = Counter()

    for arquivo in arquivos:
        try:
            colunas = ler_cabecalho_csv(arquivo)
            colunas_set = set(colunas)
            colunas_por_arquivo[os.path.basename(arquivo)] = colunas_set
            todas_colunas.update(colunas)
            contador_colunas.update(colunas)
        except Exception as e:
            print(f"[ERRO] Não foi possível ler {arquivo}: {e}")

    # Ordena as colunas por frequência de uso (mais usadas primeiro)
    colunas_ordenadas = [col for col, _ in contador_colunas.most_common()]
    arquivos = sorted(colunas_por_arquivo.keys())

    # Gera HTML
    html = [
        "<html><head><meta charset='utf-8'><title>Relatório de Colunas CSV</title>",
        "<style>table{border-collapse:collapse;}th,td{border:1px solid #ccc;padding:4px;}th{background:#eee;}</style>",
        "</head><body>",
        "<h2>Relatório de Colunas dos CSVs</h2>",
        f"<p>Total de arquivos analisados: <b>{len(arquivos)}</b></p>",
        "<table><tr><th>Arquivo</th>"
    ]
    for col in colunas_ordenadas:
        html.append(f"<th>{col}</th>")
    html.append("</tr>")

    for arquivo in arquivos:
        html.append(f"<tr><td>{arquivo}</td>")
        for col in colunas_ordenadas:
            html.append("<td style='text-align:center'>" + ("✔️" if col in colunas_por_arquivo[arquivo] else "❌") + "</td>")
        html.append("</tr>")
    html.append("</table>")

    html.append("<h3>Colunas únicas encontradas (ordenadas por frequência):</h3><ul>")
    for col in colunas_ordenadas:
        html.append(f"<li>{col} ({contador_colunas[col]} arquivos)</li>")
    html.append("</ul>")

    html.append("</body></html>")

    with open(RELATORIO_HTML, "w", encoding="utf-8") as f:
        f.write("".join(html))

    print(f"Relatório HTML gerado em: {RELATORIO_HTML}")

if __name__ == "__main__":
    main()