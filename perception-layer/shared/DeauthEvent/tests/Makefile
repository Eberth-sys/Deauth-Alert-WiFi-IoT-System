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
BUILD    := build

all: test cpp-test fuzz

$(BUILD):
	mkdir -p $(BUILD)

# Unit tests (sizeof + parser de BSSID) bajo ASAN/UBSAN
test: | $(BUILD)
	$(CC) $(CFLAGS) $(SAN) $(INC) $(SRC) test_deauth_event.c -o $(BUILD)/test_runner
	./$(BUILD)/test_runner

# Enlace C/C++: parser como C, smoke test como C++, enlazados con g++
cpp-test: | $(BUILD)
	$(CC)  $(CFLAGS)   $(SAN) $(INC) -c $(SRC) -o $(BUILD)/deauth_event.o
	$(CXX) $(CXXFLAGS) $(SAN) $(INC) -c test_cpp_linkage.cpp -o $(BUILD)/test_cpp_linkage.o
	$(CXX) $(SAN) $(BUILD)/deauth_event.o $(BUILD)/test_cpp_linkage.o -o $(BUILD)/cpp_test_runner
	./$(BUILD)/cpp_test_runner

# Fuzzing reproducible (semilla fija) del parser de BSSID, acotado por tiempo y runs
fuzz: | $(BUILD)
	$(CLANG) -std=c99 $(INC) -g -fsanitize=fuzzer,address,undefined $(SRC) fuzz_deauth_event.c -o $(BUILD)/fuzz_runner
	cd $(BUILD) && ./fuzz_runner -seed=1337 -max_total_time=60 -runs=200000

clean:
	rm -rf $(BUILD)

.PHONY: all test cpp-test fuzz clean
