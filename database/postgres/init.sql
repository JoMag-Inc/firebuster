SELECT 'CREATE DATABASE firebuster' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'firebuster')\gexec
SELECT 'CREATE DATABASE keycloak' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'keycloak')\gexec
