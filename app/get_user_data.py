import pandas as pd
import json
import os
 
# Rutas locales de los CSV
local_paths = {
    "transactions": "data/transaction_history.csv",
    "products": "data/product_table.csv",
    "customers": "data/customer_table.csv",
    "service": "data/customer_service_interactions.csv",
    "liabilities": "data/liability_table.csv",
    "payments": "data/payment_history.csv",
    "product_usage": "data/product_usage.csv",
}
 
# Función para leer CSV local
def read_csv_local(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo {path}")
    return pd.read_csv(path)
 
 
def get_customer_full_info(customer_name):
    """
    Devuelve un JSON con toda la información de un cliente
    según el modelo relacional (lee datos desde local).
    """
 
    # --- Leer todos los datasets desde local ---
    customers = read_csv_local(local_paths["customers"])
    transactions = read_csv_local(local_paths["transactions"])
    products = read_csv_local(local_paths["products"])
    product_usage = read_csv_local(local_paths["product_usage"])
    liabilities = read_csv_local(local_paths["liabilities"])
    payments = read_csv_local(local_paths["payments"])
    service = read_csv_local(local_paths["service"])
 
    # Buscar cliente por nombre
    customer_row = customers[customers["customer_name"] == customer_name]
 
    if customer_row.empty:
        return {"error": f"No se encontró el cliente {customer_name}"}
 
    customer_id = customer_row.iloc[0]["customer_id"]
 
    # --- Customer ---
    customer_info = customer_row.to_dict(orient="records")[0]
 
    # --- Transaction History ---
    customer_transactions = transactions[transactions["customer_id"] == customer_id]
    transactions_info = customer_transactions.to_dict(orient="records")
 
    # --- Product Usage ---
    customer_usage = product_usage[product_usage["customer_id"] == customer_id]
    usage_info = customer_usage.to_dict(orient="records")
 
    # --- Product Table (usando product_id en Product Usage) ---
    product_ids = customer_usage["product_id"].unique().tolist()
    customer_products = products[products["product_id"].isin(product_ids)]
    products_info = customer_products.to_dict(orient="records")
 
    # --- Liabilities ---
    customer_liabilities = liabilities[liabilities["customer_id"] == customer_id]
    liabilities_info = customer_liabilities.to_dict(orient="records")
 
    # --- Payment History (via liability_id) ---
    liability_ids = customer_liabilities["liability_id"].unique().tolist()
    customer_payments = payments[payments["liability_id"].isin(liability_ids)]
    payments_info = customer_payments.to_dict(orient="records")
 
    # --- Customer Service Interactions ---
    customer_service = service[service["customer_id"] == customer_id]
    service_info = customer_service.to_dict(orient="records")
 
    # --- Armar JSON final ---
    result = {
        "Customer": customer_info,
        "Transaction_History": transactions_info,
        "Product_Usage": usage_info,
        "Product_Table": products_info,
        "Liabilities": liabilities_info,
        "Payment_History": payments_info,
        "Customer_Service_Interactions": service_info,
    }
 
    return result
 
 
# -------------------------------
# 🔹 Ejemplo de uso
# -------------------------------
# cliente_json = get_customer_full_info("Noah Rhodes")

# Imprimir en formato JSON legible
# print(json.dumps(cliente_json, indent=2))
