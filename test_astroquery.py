# test_astroquery.py
print("Iniciando teste de astroquery...")
try:
    from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive

    print("Importação bem-sucedida.")

    nexsci_archive = NasaExoplanetArchive()
    print("Instanciação da classe bem-sucedida.")

    print("Consultando o planeta 'Kepler-186 f'...")
    test_data = nexsci_archive.query_planet('Kepler-186 f', all_columns=True)

    if test_data is not None:
        print("\nSUCESSO! Dados recebidos do arquivo da NASA.")
        print(f"Planeta: {test_data['hostname'][0]}")
        print(f"Período Orbital: {test_data['pl_orbper'][0]} dias")
    else:
        print("\nFALHA: A consulta retornou None.")

except AttributeError as e:
    print(f"\nERRO DE ATRIBUTO DETECTADO: {e}")
except Exception as e:
    print(f"\nUM ERRO INESPERADO OCORREU: {e}")