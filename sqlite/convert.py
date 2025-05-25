import yaml

# Caminho para o arquivo YAML com seus dados
yaml_file = "ativos.yml"
sql_file = "import_indicadores_ativos.sql"

with open(yaml_file, "r", encoding="utf-8") as f:
    dados = yaml.safe_load(f)

with open(sql_file, "w", encoding="utf-8") as f:
    for tipo, info in dados.items():
        spread = info["spread"]
        for item in info["tickers"]:
            ticker = item["ticker"].strip()
            f.write(f"INSERT INTO indicadores_ativos (ticker, tipo, spread) VALUES ('{ticker}', '{tipo}', {spread});\n")

print(f"Arquivo {sql_file} gerado com sucesso a partir de {yaml_file}!")



