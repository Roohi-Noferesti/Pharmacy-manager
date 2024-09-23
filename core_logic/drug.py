
class Drug:
    def __init__(self, drug_code, name, production_date, expiration_date, price, dosage, usage_instructions, drug_inventory, pharmacy_code, company_code):
        self.drug_code = drug_code
        self.name = name
        self.production_date = production_date
        self.expiration_date = expiration_date
        self.price = price
        self.dosage = dosage
        self.usage_instructions = usage_instructions
        self.drug_inventory = drug_inventory
        self.pharmacy_code = pharmacy_code
        self.company_code = company_code
        self.drug_code = drug_code

    def __str__(self):
        return f"Drug {self.name} (Code: {self.drug_code})"
