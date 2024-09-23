
class Pharmacy:
    def __init__(self, pharmacy_code, name, established_date, phone_number, address, license):
        self.pharmacy_code = pharmacy_code
        self.name = name
        self.established_date = established_date
        self.phone_number = phone_number
        self.address = address
        self.license = license

    def __str__(self):
        return f"Pharmacy {self.name} (Code: {self.pharmacy_code})"
