DROP TABLE IF EXISTS transactions;

DROP TABLE IF EXISTS alerts;

CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    step INT,
    type VARCHAR(20),
    amount DECIMAL(15, 2),
    nameOrig VARCHAR(50),
    oldbalanceOrg DECIMAL(15, 2),
    newbalanceOrig DECIMAL(15, 2),
    nameDest VARCHAR(50),
    oldbalanceDest DECIMAL(15, 2),
    newbalanceDest DECIMAL(15, 2),
    timestamp TIMESTAMP
);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    nameOrig VARCHAR(50),
    nameDest VARCHAR(50),
    amount DECIMAL(15, 2),
    type VARCHAR(20),
    probability FLOAT,
    timestamp TIMESTAMP
);