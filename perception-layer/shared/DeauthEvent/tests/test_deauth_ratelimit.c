/*
 * Unit tests de deauth_ratelimit (F5-3). Verifican: supresion de misma clave dentro de
 * la ventana; ataque continuo que NO renueva la ventana con supresiones; limite exacto
 * (elapsed == window -> permitir); claves distintas por dst y por subtype; expiracion;
 * wrap-around del tick; reutilizacion de una entrada expirada; y tabla llena de entradas
 * activas -> fail-open observable. Bajo ASAN/UBSAN, -Wall -Wextra -Werror.
 */
#include "deauth_ratelimit.h"
#include <stdio.h>
#include <string.h>

static int g_fail = 0;

#define CHECK(cond, msg)                                                   \
    do {                                                                   \
        if (!(cond)) {                                                     \
            printf("FAIL: %s (linea %d)\n", (msg), __LINE__);              \
            ++g_fail;                                                      \
        }                                                                  \
    } while (0)

#define WIN 1000u

/* Construye una MAC de destino con un byte distintivo. */
static void mk_dst(uint8_t out[6], uint8_t tag)
{
    int i;
    for (i = 0; i < 6; ++i) out[i] = tag;
}

int main(void)
{
    deauth_rate_limiter_t rl;
    uint8_t a[6], b[6];
    mk_dst(a, 0xA1);
    mk_dst(b, 0xB2);

    /* 1) Misma clave dentro de la ventana -> primera ALLOW, siguientes SUPPRESS. */
    deauth_ratelimit_init(&rl);
    CHECK(deauth_ratelimit_check(&rl, a, 12, 100, WIN) == DEAUTH_RL_ALLOW,    "1a: primera emite");
    CHECK(deauth_ratelimit_check(&rl, a, 12, 500, WIN) == DEAUTH_RL_SUPPRESS, "1b: duplicado en ventana suprime");
    CHECK(deauth_ratelimit_check(&rl, a, 12, 999, WIN) == DEAUTH_RL_SUPPRESS, "1c: sigue suprimiendo");

    /* 2) Ataque CONTINUO: las supresiones NO renuevan la ventana. Con last=100 y WIN=1000,
     *    a t=1100 debe permitir (elapsed 1000 desde el ULTIMO PERMITIDO en 100, no desde 999). */
    CHECK(deauth_ratelimit_check(&rl, a, 12, 1100, WIN) == DEAUTH_RL_ALLOW, "2: continuo permite 1/ventana (supresion no renueva)");
    CHECK(deauth_ratelimit_check(&rl, a, 12, 1600, WIN) == DEAUTH_RL_SUPPRESS, "2b: tras renovar en 1100, vuelve a suprimir");

    /* 3) Limite exacto: elapsed == window -> PERMITE. */
    deauth_ratelimit_init(&rl);
    CHECK(deauth_ratelimit_check(&rl, a, 12, 0, WIN) == DEAUTH_RL_ALLOW,      "3a: primera en t=0");
    CHECK(deauth_ratelimit_check(&rl, a, 12, WIN - 1, WIN) == DEAUTH_RL_SUPPRESS, "3b: un tick antes del limite suprime");
    CHECK(deauth_ratelimit_check(&rl, a, 12, WIN, WIN) == DEAUTH_RL_ALLOW,    "3c: elapsed == window permite");

    /* 4) dst distinto -> clave distinta -> permite (slot propio). */
    deauth_ratelimit_init(&rl);
    CHECK(deauth_ratelimit_check(&rl, a, 12, 100, WIN) == DEAUTH_RL_ALLOW, "4a: dst A emite");
    CHECK(deauth_ratelimit_check(&rl, b, 12, 100, WIN) == DEAUTH_RL_ALLOW, "4b: dst B (distinto) emite");
    CHECK(deauth_ratelimit_check(&rl, a, 12, 200, WIN) == DEAUTH_RL_SUPPRESS, "4c: dst A duplicado suprime");

    /* 5) subtype distinto -> clave distinta -> permite. */
    deauth_ratelimit_init(&rl);
    CHECK(deauth_ratelimit_check(&rl, a, 12, 100, WIN) == DEAUTH_RL_ALLOW, "5a: (A,12) emite");
    CHECK(deauth_ratelimit_check(&rl, a, 10, 100, WIN) == DEAUTH_RL_ALLOW, "5b: (A,10) subtype distinto emite");
    CHECK(deauth_ratelimit_check(&rl, a, 12, 300, WIN) == DEAUTH_RL_SUPPRESS, "5c: (A,12) duplicado suprime");

    /* 6) Expiracion: pasada la ventana, la misma clave vuelve a emitir. */
    deauth_ratelimit_init(&rl);
    CHECK(deauth_ratelimit_check(&rl, a, 12, 100, WIN) == DEAUTH_RL_ALLOW, "6a: emite");
    CHECK(deauth_ratelimit_check(&rl, a, 12, 100 + WIN + 1, WIN) == DEAUTH_RL_ALLOW, "6b: tras expirar, reemite");

    /* 7) Wrap-around del tick de 32 bits: last cerca de UINT32_MAX, now envuelto. */
    deauth_ratelimit_init(&rl);
    CHECK(deauth_ratelimit_check(&rl, a, 12, 0xFFFFFF00u, WIN) == DEAUTH_RL_ALLOW, "7a: emite cerca del wrap");
    /* now = 0x100 -> elapsed = (uint32_t)(0x100 - 0xFFFFFF00) = 0x200 = 512 < 1000 -> suprime */
    CHECK(deauth_ratelimit_check(&rl, a, 12, 0x100u, WIN) == DEAUTH_RL_SUPPRESS, "7b: elapsed wrap-safe < ventana suprime");
    /* now tal que elapsed == 1000 cruzando el wrap: 0xFFFFFF00 + 1000 = 0x000002E8 */
    CHECK(deauth_ratelimit_check(&rl, a, 12, 0x000002E8u, WIN) == DEAUTH_RL_ALLOW, "7c: elapsed==1000 cruzando wrap permite");

    /* 8) Reutilizacion de una entrada EXPIRADA por una clave nueva (no fail-open). */
    deauth_ratelimit_init(&rl);
    {
        uint8_t k[6];
        int i;
        /* Llenar las 8 entradas con claves distintas en t=100. */
        for (i = 0; i < (int)DEAUTH_RL_SLOTS; ++i) {
            mk_dst(k, (uint8_t)(0x10 + i));
            CHECK(deauth_ratelimit_check(&rl, k, 12, 100, WIN) == DEAUTH_RL_ALLOW, "8a: llena 8 slots");
        }
        /* En t=100+WIN+1 TODAS expiraron; una clave NUEVA reutiliza una entrada expirada -> ALLOW. */
        mk_dst(k, 0x99);
        CHECK(deauth_ratelimit_check(&rl, k, 12, 100 + WIN + 1, WIN) == DEAUTH_RL_ALLOW, "8b: clave nueva reutiliza slot expirado");
    }

    /* 9) Tabla llena de entradas ACTIVAS -> fail-open observable para la 9a clave nueva. */
    deauth_ratelimit_init(&rl);
    {
        uint8_t k[6];
        int i;
        for (i = 0; i < (int)DEAUTH_RL_SLOTS; ++i) {
            mk_dst(k, (uint8_t)(0x20 + i));
            CHECK(deauth_ratelimit_check(&rl, k, 12, 100, WIN) == DEAUTH_RL_ALLOW, "9a: 8 claves activas");
        }
        /* 9a clave nueva mientras las 8 siguen activas (dentro de la ventana) -> fail-open. */
        mk_dst(k, 0x77);
        CHECK(deauth_ratelimit_check(&rl, k, 12, 200, WIN) == DEAUTH_RL_ALLOW_FULL, "9b: tabla activa llena -> fail-open");
        /* Una de las 8 originales, aun en ventana, sigue suprimiendose (no fue desalojada). */
        mk_dst(k, 0x20);
        CHECK(deauth_ratelimit_check(&rl, k, 12, 300, WIN) == DEAUTH_RL_SUPPRESS, "9c: clave existente no fue desalojada por el fail-open");
    }

    /* Defensivo: rl NULL -> fail-open. */
    CHECK(deauth_ratelimit_check(NULL, a, 12, 0, WIN) == DEAUTH_RL_ALLOW_FULL, "10: rl NULL -> fail-open");

    /* Defensivo: dst NULL con rl valido -> fail-open (el contrato promete fail-open para rl O dst NULL). */
    deauth_ratelimit_init(&rl);
    CHECK(deauth_ratelimit_check(&rl, NULL, 12, 0, WIN) == DEAUTH_RL_ALLOW_FULL, "11: dst NULL -> fail-open");

    /* 12) Reuso de slot expirado en el limite EXACTO elapsed==window (cubre el `>=` del camino de
     *     eviccion): con las 8 entradas ocupadas, una clave nueva a elapsed==window debe reusar
     *     (ALLOW), no fail-open. Distingue `>=` de `>` en la deteccion de expirado. */
    deauth_ratelimit_init(&rl);
    {
        uint8_t k[6];
        int i;
        for (i = 0; i < (int)DEAUTH_RL_SLOTS; ++i) {
            mk_dst(k, (uint8_t)(0x30 + i));
            CHECK(deauth_ratelimit_check(&rl, k, 12, 100, WIN) == DEAUTH_RL_ALLOW, "12a: llena 8 slots");
        }
        mk_dst(k, 0x88);
        CHECK(deauth_ratelimit_check(&rl, k, 12, 100 + WIN, WIN) == DEAUTH_RL_ALLOW, "12b: reuso de expirado en elapsed==window (no fail-open)");
    }

    /* 13) Guarda defensiva: deauth_ratelimit_init(NULL) no debe desreferenciar (ASAN abortaria si se
     *     quitara la guarda); tras la llamada nula, un limitador valido sigue operando. */
    deauth_ratelimit_init(NULL);
    deauth_ratelimit_init(&rl);
    CHECK(deauth_ratelimit_check(&rl, a, 12, 0, WIN) == DEAUTH_RL_ALLOW, "13: init(NULL) no crashea y el limitador valido opera");

    if (g_fail == 0) {
        printf("OK: deauth_ratelimit (ventana, continuo, limite exacto, dst/subtype, expiracion, wrap, reuso, reuso@limite, fail-open, null-defensivo)\n");
        return 0;
    }
    printf("FALLARON %d comprobaciones\n", g_fail);
    return 1;
}
