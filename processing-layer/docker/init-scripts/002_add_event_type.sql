-- 002_add_event_type.sql
-- Migración idempotente: agrega alerts.event_type (F1, DEC-0003).
--
-- Contexto de ejecución:
--   * Base NUEVA: los scripts de /docker-entrypoint-initdb.d corren solo con el
--     data-dir vacío. init.sql ya crea la columna inline; este script queda como
--     no-op idempotente. Es seguro aunque el runner lo ejecute ANTES que init.sql
--     (ordena por nombre: "002_" < "init.sql"), porque valida que la tabla exista.
--   * Base EXISTENTE (volumen persistido): los init-scripts NO se re-ejecutan.
--     Correr este archivo manualmente:  psql -U <user> -d <db> -f 002_add_event_type.sql
--
-- Idempotente: puede correrse varias veces sin efecto adicional.
-- Las filas existentes quedan como 'deauth' (compatibilidad legacy).

DO $$
BEGIN
    -- Solo si la tabla ya existe (evita fallar si corre antes que init.sql en un init limpio).
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'alerts'
    ) THEN
        -- 1) Columna (idempotente).
        ALTER TABLE alerts
            ADD COLUMN IF NOT EXISTS event_type VARCHAR(16) NOT NULL DEFAULT 'deauth';

        -- 2) CHECK constraint (ADD CONSTRAINT no soporta IF NOT EXISTS → se guarda por catálogo).
        --    Nombre = el que Postgres autogenera para el CHECK inline de init.sql.
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint WHERE conname = 'alerts_event_type_check'
        ) THEN
            ALTER TABLE alerts
                ADD CONSTRAINT alerts_event_type_check
                CHECK (event_type IN ('deauth', 'disassoc'));
        END IF;
    END IF;
END $$;
