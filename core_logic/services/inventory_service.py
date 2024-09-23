# core_logic/services/inventory_service.py

class InventoryService:
    def __init__(self, database_adapter):
        self.database_adapter = database_adapter

    def update_inventory(self, drug_code, new_quantity):
        query = "UPDATE Drug SET drug_inventory = ? WHERE drug_code = ?"
        parameters = (new_quantity, drug_code)
        self.database_adapter.execute_query(query, parameters)

    def check_inventory(self, drug_code):
        query = "SELECT drug_inventory FROM Drug WHERE drug_code = ?"
        parameters = (drug_code,)
        result = self.database_adapter.fetch_all(query, parameters)
        return result[0][0] if result else None
