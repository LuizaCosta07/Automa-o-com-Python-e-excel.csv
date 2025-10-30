import pandas as pd
import time
from playwright.sync_api import sync_playwright


input_excel = "produtos_recibom.xlsx"
output_csv = "resultados_recibom.csv"


URL = "https://www.recibomdelivery.com.br/loja/162"


def buscar_precos():
   
    df = pd.read_excel(input_excel)
    eans = df["EAN"].astype(str).tolist()

    resultados = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        
        print("Acessando loja Recibom...")
        page.goto(URL)
        time.sleep(2.5)

        
        try:
            page.locator("button:has-text('Entendi')").click(timeout=3000)
            print("Popup fechado.")
        except:
            pass

        for idx, ean in enumerate(eans, start=1):
            print(f"[{idx}/{len(eans)}] Buscando EAN: {ean}")

            try:
                
                search_box = page.locator("input[placeholder='Pesquise seus produtos aqui!']").first
                search_box.fill("")
                search_box.fill(ean)
                search_box.press("Enter")

                
                page.wait_for_selector("p.current-price-product", timeout=15000)

               
                preco = page.locator("p.current-price-product").first.inner_text().strip()
                resultados.append({"EAN": ean, "Preco": preco})
                print(f"✅ EAN {ean} -> Preço encontrado: {preco}")

            except Exception as e:
                print(f"⚠️ EAN {ean} não encontrado ({str(e)[:80]}...)")
                resultados.append({"EAN": ean, "Preco": "NÃO ENCONTRADO"})

            
            time.sleep(2.5)

        browser.close()

    resultado_df = pd.DataFrame(resultados)
    resultado_df.to_csv(output_csv, index=False, sep=";")
    print(f"\n✅ Busca finalizada! Resultados salvos em '{output_csv}'")

if __name__ == "__main__":
    buscar_precos()
