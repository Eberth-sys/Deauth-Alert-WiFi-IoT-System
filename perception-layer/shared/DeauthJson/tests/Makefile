# Build y ejecucion de las pruebas de host de DeauthJson (F5-1): serializador del
# contrato de eventos v1. Solo necesita deauth_json.c y el header de DeauthEvent
# (deauth_event_t); NO enlaza deauth_event.c (no invoca ninguna funcion suya).
# Todos los binarios y artefactos van a tests/build/ (gitignored).
CC    := gcc
CXX   := g++
CLANG := clang

CFLAGS   := -std=c99 -Wall -Wextra -Werror
CXXFLAGS := -std=c++11 -Wall -Wextra -Werror
SAN      := -fsanitize=address,undefined -fno-sanitize-recover=all
INC      := -I../src -I../../DeauthEvent/src
SRC      := ../src/deauth_json.c
BUILD    := build

all: test cpp-test fuzz contract

$(BUILD):
	mkdir -p $(BUILD)

# Unit tests (tamanos 113/164, limites de out_size, salida vacia en fallo) bajo ASAN/UBSAN
test: | $(BUILD)
	$(CC) $(CFLAGS) $(SAN) $(INC) $(SRC) test_deauth_json.c -o $(BUILD)/test_runner
	./$(BUILD)/test_runner

# Enlace C/C++: serializador como C, smoke test como C++, enlazados con g++
cpp-test: | $(BUILD)
	$(CC)  $(CFLAGS)   $(SAN) $(INC) -c $(SRC) -o $(BUILD)/deauth_json.o
	$(CXX) $(CXXFLAGS) $(SAN) $(INC) -c test_cpp_linkage.cpp -o $(BUILD)/test_cpp_linkage.o
	$(CXX) $(SAN) $(BUILD)/deauth_json.o $(BUILD)/test_cpp_linkage.o -o $(BUILD)/cpp_test_runner
	./$(BUILD)/cpp_test_runner

# Fuzzing reproducible (semilla fija) del serializador, acotado por tiempo y runs
fuzz: | $(BUILD)
	$(CLANG) -std=c99 $(INC) -g -fsanitize=fuzzer,address,undefined $(SRC) fuzz_deauth_json.c -o $(BUILD)/fuzz_runner
	cd $(BUILD) && ./fuzz_runner -seed=1337 -max_total_time=60 -runs=200000

# Contrato C->Python: emit_vectors emite SOLO JSON valido; el parse_event REAL lo acepta/normaliza
contract: | $(BUILD)
	$(CC) $(CFLAGS) $(SAN) $(INC) $(SRC) emit_vectors.c -o $(BUILD)/emit_vectors
	python3 contract_cross.py ./$(BUILD)/emit_vectors

clean:
	rm -rf $(BUILD)

.PHONY: all test cpp-test fuzz contract clean
