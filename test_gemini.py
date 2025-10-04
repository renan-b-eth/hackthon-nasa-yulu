# test_gemini.py
import google.generativeai as genai
import os

# Coloque a sua NOVA chave de API aqui diretamente para este teste
# ATENÇÃO: Lembre-se de apagar esta chave do ficheiro depois do teste!
API_KEY = "AIzaSyBMRc3oVl_JG3LXdzXGQLvCrGOCh-Rurus"

print("--- A iniciar teste da API Gemini ---")
try:
    genai.configure(api_key=API_KEY)
    print("Configuração da API bem-sucedida.")

    print("\nA tentar usar o modelo 'gemini-pro-vision'...")
    model = genai.GenerativeModel('gemini-pro-vision')
    print("✅ SUCESSO! O modelo 'gemini-pro-vision' foi encontrado e carregado.")
    print("\nO seu ambiente está corrigido! Pode executar o Streamlit agora.")

except Exception as e:
    print(f"\n❌ FALHA: Ocorreu um erro ao tentar usar 'gemini-pro-vision'.")
    print(f"   Erro detalhado: {e}")

    print("\n--- A listar todos os modelos disponíveis para a sua chave ---")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
        print("\nSe 'gemini-pro-vision' não estiver na lista acima, use um dos nomes listados.")
    except Exception as list_e:
        print(f"Não foi possível listar os modelos: {list_e}")

print("\n--- Teste concluído ---")