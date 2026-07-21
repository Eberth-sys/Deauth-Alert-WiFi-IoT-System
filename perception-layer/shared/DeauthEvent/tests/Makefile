# Build y ejecucion de las pruebas de host de DeauthEvent (F4c-1).
# Todos los binarios y artefactos (incl. crash-* del fuzzer) van a tests/build/ (gitignored).
CC    := gcc
CXX   := g++
CLANG := clang

CFLAGS   := -std=c99 -Wall -Wextra -Werror
CXXFLAGS := -std=c++11 -Wall -Wextra -Werror
SAN      := -fsanitize=address,undefined -fno-sanitize-recover=all
INC      := -I../src
SRC      := ../src/deauth_event.c
# El modulo diagnostico solo existe con el flag activo: se compila con el en los
# objetivos que lo ejercitan. NO se agrega fuzzing de DeauthDiag.
DIAG_ON  := -DDEAUTH_DIAG=1
BUILD    := build

all: test cpp-test fuzz

$(BUILD):
	mkdir -p $(BUILD)

# Unit tests (sizeof + parser de BSSID) bajo ASAN/UBSAN
test: | $(BUILD)
	$(CC) $(CFLAGS) $(SAN) $(INC) $(SRC) test_deauth_event.c -o $(BUILD)/test_runner
	./$(BUILD)/test_runner
	$(CC) $(CFLAGS) $(SAN) $(INC) ../src/deauth_ratelimit.c test_deauth_ratelimit.c -o $(BUILD)/ratelimit_runner
	./$(BUILD)/ratelimit_runner
	$(CC) $(CFLAGS) $(SAN) $(DIAG_ON) $(INC) ../src/deauth_diag.c test_deauth_diag.c -o $(BUILD)/diag_runner
	./$(BUILD)/diag_runner

# Enlace C/C++: parser como C, smoke test como C++, enlazados con g++
cpp-test: | $(BUILD)
	$(CC)  $(CFLAGS)   $(SAN) $(INC) -c $(SRC) -o $(BUILD)/deauth_event.o
	$(CC)  $(CFLAGS)   $(SAN) $(INC) -c ../src/deauth_ratelimit.c -o $(BUILD)/deauth_ratelimit.o
	$(CC)  $(CFLAGS)   $(SAN) $(DIAG_ON) $(INC) -c ../src/deauth_diag.c -o $(BUILD)/deauth_diag.o
	$(CXX) $(CXXFLAGS) $(SAN) $(DIAG_ON) $(INC) -c test_cpp_linkage.cpp -o $(BUILD)/test_cpp_linkage.o
	$(CXX) $(SAN) $(BUILD)/deauth_event.o $(BUILD)/deauth_ratelimit.o $(BUILD)/deauth_diag.o $(BUILD)/test_cpp_linkage.o -o $(BUILD)/cpp_test_runner
	./$(BUILD)/cpp_test_runner

# Fuzzing reproducible (semilla fija) del parser de BSSID, acotado por tiempo y runs
fuzz: | $(BUILD)
	$(CLANG) -std=c99 $(INC) -g -fsanitize=fuzzer,address,undefined $(SRC) fuzz_deauth_event.c -o $(BUILD)/fuzz_runner
	cd $(BUILD) && ./fuzz_runner -seed=1337 -max_total_time=60 -runs=200000

clean:
	rm -rf $(BUILD)

.PHONY: all test cpp-test fuzz clean
