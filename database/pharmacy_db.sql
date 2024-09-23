
CREATE TABLE Pharmacy (
    pharmacy_code INT PRIMARY KEY,
    name VARCHAR(255),
    established_date DATE,
    phone_number VARCHAR(15),
    address VARCHAR(255),
    license INT
);

CREATE TABLE Drug (
    drug_code TEXT PRIMARY KEY,
    name VARCHAR(255),
    production_date DATE,
    expiration_date DATE,
    price DECIMAL(10, 2),
    dosage VARCHAR(50),
    usage_instructions TEXT,
    drug_inventory INT,
    pharmacy_code INT,
    company_code INT,
    FOREIGN KEY (pharmacy_code) REFERENCES Pharmacy(pharmacy_code),
    FOREIGN KEY (company_code) REFERENCES DrugCompany(registration_number)
);

CREATE TABLE User (
    user_id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    birthdate DATE,
    address VARCHAR(255),
    age INT,
    sex VARCHAR(10),
    username VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    role INT
);




CREATE TABLE DrugCompany (
    registration_number INT PRIMARY KEY,
    name VARCHAR(255),
    date_established DATE,
    phone_number VARCHAR(15),
    address VARCHAR(255)
);

CREATE TABLE DrugManufacturer (
    manufacturer_number INT PRIMARY KEY,
    registration_number INT,
    FOREIGN KEY (registration_number) REFERENCES DrugCompany(registration_number)
);


CREATE TABLE DrugOrder (
    order_code INT PRIMARY KEY,
    patient_code INT,
    pharmacy_code INT,
    quantity INT,
    FOREIGN KEY (patient_code) REFERENCES User(user_id),
    FOREIGN KEY (pharmacy_code) REFERENCES Pharmacy(pharmacy_code)
);


CREATE TABLE DrugComment (
    comment_id INTEGER PRIMARY KEY,
    patient_code INT,
    drug_code TEXT,
    comment TEXT,
    rating INT,
    FOREIGN KEY (patient_code) REFERENCES User(user_id),
    FOREIGN KEY (drug_code) REFERENCES Drug(drug_code)
);


CREATE TABLE WarehouseOrder (
    order_code INT PRIMARY KEY,
    drug_code INT,
    quantity INT,
    warehouse_clerk_id INT,
    pharmacy_code INT,
    FOREIGN KEY (warehouse_clerk_id) REFERENCES User(user_id),
    FOREIGN KEY (pharmacy_code) REFERENCES Pharmacy(pharmacy_code)
);
