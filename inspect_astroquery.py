# inspect_astroquery.py
print("--- Inspecionando a biblioteca Astroquery ---")

try:
    from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive

    # Criamos o objeto que está nos dando o erro
    nexsci_archive = NasaExoplanetArchive()

    print("\n--- MÉTODOS E ATRIBUTOS disponíveis no objeto 'nexsci_archive': ---")
    # O comando dir() é um detetive: ele lista tudo que existe dentro de um objeto!

    count = 0
    for item in dir(nexsci_archive):
        # Vamos ignorar os itens internos que começam com '_'
        if not item.startswith('_'):
            print(item)
            count += 1

    print(f"\n--- Encontrados {count} itens públicos. Fim da Inspeção ---")

except Exception as e:
    print(f"Ocorreu um erro durante a inspeção: {e}")