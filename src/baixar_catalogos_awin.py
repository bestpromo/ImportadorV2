import os
import csv
import gzip
import shutil
import requests
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

# Diretórios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTS_DIR = os.path.join(BASE_DIR, 'data', 'awin', 'lists')
INPUTS_DIR = os.path.join(BASE_DIR, 'data', 'awin', 'inputs')

os.makedirs(LISTS_DIR, exist_ok=True)
os.makedirs(INPUTS_DIR, exist_ok=True)

# Configurações
AWIN_API_KEY = os.getenv("AWIN_API_KEY")
AWIN_PUBLISHER_ID = os.getenv("AWIN_PUBLISHER_ID")
AWIN_LIST_URL = f"https://ui.awin.com/productdata-darwin-download/publisher/{AWIN_PUBLISHER_ID}/{AWIN_API_KEY}/1/feedList"
DATA_HOJE = datetime.now().strftime("%d%m%Y")
LIST_FILENAME = f"{DATA_HOJE}-Lista_Awin.csv"
LIST_PATH = os.path.join(LISTS_DIR, LIST_FILENAME)
LOG_PATH = os.path.join(LISTS_DIR, f"{DATA_HOJE}-execucao.log")

def log(msg, tipo="INFO"):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    linha = f"[{tipo}] {msg} ({now})"
    print(linha)
    with open(LOG_PATH, "a") as f:
        f.write(linha + "\n")

def baixar_e_descompactar(url, destino_csv):
    gz_path = destino_csv + ".gz"
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(gz_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    with gzip.open(gz_path, 'rb') as f_in, open(destino_csv, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(gz_path)

def filtrar_lojas_ativas(csv_path):
    lojas_ativas = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get("Membership Status", "").strip().lower() == "active":
                lojas_ativas.append(row)
    return lojas_ativas

def baixar_catalogos_lojas(lojas):
    for loja in lojas:
        advertiser_id = loja["Advertiser ID"].strip()
        advertiser_name = loja["Advertiser Name"].strip().replace(" ", "_")
        url = loja["URL"].strip()
        nome_arquivo = f"{DATA_HOJE}-{advertiser_id}-{advertiser_name}.csv"
        destino_csv = os.path.join(INPUTS_DIR, nome_arquivo)
        try:
            log(f"Baixando catálogo: {advertiser_id} - {advertiser_name}")
            baixar_e_descompactar(url, destino_csv)
            log(f"Catálogo salvo em: {destino_csv}")
        except Exception as e:
            log(f"Erro ao baixar catálogo {advertiser_id} - {advertiser_name}: {e}", tipo="ERROR")

def main():
    inicio = datetime.now()
    log("Iniciando processo de ingestão AWIN")

    # 1. Baixar e descompactar lista principal
    try:
        log("Baixando lista principal da AWIN...")
        baixar_e_descompactar(AWIN_LIST_URL, LIST_PATH)
        log(f"Arquivo de lista baixado e descompactado: {LIST_PATH}")
    except Exception as e:
        log(f"Erro ao baixar/descompactar lista principal: {e}", tipo="ERROR")
        return

    # 2. Filtrar lojas ativas
    lojas_ativas = filtrar_lojas_ativas(LIST_PATH)
    log(f"Lojas ativas encontradas: {len(lojas_ativas)}")

    # 3. Baixar catálogos das lojas ativas
    baixar_catalogos_lojas(lojas_ativas)

    fim = datetime.now()
    tempo_total = (fim - inicio).total_seconds()
    log(f"Processo finalizado")
    log(f"Tempo total de execução: {tempo_total:.2f} segundos")

if __name__ == "__main__":
    main()