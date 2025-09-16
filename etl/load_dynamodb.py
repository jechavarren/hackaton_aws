import boto3
import csv
import os
from pathlib import Path
from botocore.exceptions import ClientError

# Configuración
CSV_FOLDER = "./data"
REGION_NAME = "us-west-2"

# Cliente DynamoDB
dynamodb = boto3.resource("dynamodb", region_name=REGION_NAME)


def crear_tabla_si_no_existe(table_name, hash_key="id"):
    try:
        table = dynamodb.Table(table_name)
        table.load()
        print(f"La tabla '{table_name}' ya existe.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"Creando tabla '{table_name}'...")
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[{"AttributeName": hash_key, "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": hash_key, "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )
            table.wait_until_exists()
            print(f"Tabla '{table_name}' creada.")
        else:
            raise
    return dynamodb.Table(table_name)


def cargar_csv_a_dynamodb(csv_file, table_name):
    table = crear_tabla_si_no_existe(table_name)

    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        with table.batch_writer() as batch:
            for row in reader:
                if "id" not in row or row["id"] == "":
                    row["id"] = str(hash(str(row)))
                item = {k: v for k, v in row.items() if v is not None and v != ""}
                batch.put_item(Item=item)
                print(f"[{table_name}] Insertado: {item}")


def cargar_carpeta_csv(carpeta):
    csv_files = Path(carpeta).glob("*.csv")
    for csv_file in csv_files:
        table_name = os.path.splitext(os.path.basename(csv_file))[0]
        print(f"\nProcesando {csv_file}. Tabla: {table_name}")
        cargar_csv_a_dynamodb(csv_file, table_name)
    print("\nCarga completada para todos los CSV en", carpeta)


if __name__ == "__main__":
    cargar_carpeta_csv(CSV_FOLDER)
