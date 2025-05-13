DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database
      WHERE  datname = 'quickbooks') THEN
      CREATE DATABASE quickbooks;
   END IF;
END
$do$;
