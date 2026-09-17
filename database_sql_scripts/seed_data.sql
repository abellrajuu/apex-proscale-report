-- Default Admin and Technician User Seed Data
-- File: sql/seed_data.sql

INSERT OR IGNORE INTO users (id, username, password_hash, full_name, role) 
VALUES 
(1, 'admin', 'scrypt:32768:8:1$2iH3tDXchgTZkinG$03debc8cd5cf04d2d16e05e5ae5a7e8ce06736db4a409340db8671a9cd782f60f11de885de76829235ac2a789fbbf25f818db21d2501d718dd2e81d73afdb1bd', 'System Administrator', 'Admin'),
(2, 'tech', 'scrypt:32768:8:1$UWVYXMjEPhjroA50$230f53d958f5a09e1e6b79058caeff2fd3bc01dbc3b8b90c32f8542864645f0e2f5300048d9ce8bfc7b9e99ec571acec6a5dd2638eaea54945a3cd585af221e7', 'Field Technician', 'Technician');
