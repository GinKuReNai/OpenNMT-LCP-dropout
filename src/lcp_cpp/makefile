all: lcp_random lcp_paircomp lcp_paircomp_faster
	
# -----------------------

# コンパイル対象となるC++ソースファイル
ALL_SOURCES 				= main.cpp lcp_utility.cpp lcp_random.cpp lcp_paircomp.cpp lcp_paircomp_faster.cpp
LCP_RADNOM_SOURCES   		= main.cpp lcp_random.cpp lcp_utility.cpp
LCP_PAIRCOMP_SOURCES 		= main.cpp lcp_paircomp.cpp lcp_utility.cpp
LCP_PAIRCOMP_FASTER_SOURCES = main.cpp lcp_paircomp_faster.cpp lcp_utility.cpp

# コンパイル対象となるオブジェクトファイル
ALL_OBJECTS 				= $(ALL_SOURCES:.cpp=.o)
LCP_RANDOM_OBJECTS 			= $(LCP_RADNOM_SOURCES:.cpp=.o)
LCP_PAIRCOMP_OBJECTS 		= $(LCP_PAIRCOMP_SOURCES:.cpp=.o)
LCP_PAIRCOMP_FASTER_OBJECTS = $(LCP_PAIRCOMP_FASTER_SOURCES:.cpp=.o)

# コンパイルフラグ
CXXFLAGS = -std=c++20 -I/usr/local/include

# リンクフラグ
LDFLAGS = -L/usr/local/lib -lyaml-cpp

# オプション : gdbでデバッグする際は, 最適化オプションを-O0にすること
# -fexec-charsetを指定してユニコードを処理可能にしている
OPTIONS = -Wall -O3 -fexec-charset=utf-8

# -----------------------

# リンク : lcp_random
lcp_random: $(LCP_RANDOM_OBJECTS)
				g++ $(OPTIONS) -o lcp_random $(LCP_RANDOM_OBJECTS) $(LDFLAGS)
				
# リンク : lcp_paircomp
lcp_paircomp: $(LCP_PAIRCOMP_OBJECTS)
				g++ $(OPTIONS) -o lcp_paircomp $(LCP_PAIRCOMP_OBJECTS) $(LDFLAGS)
				
# リンク : lcp_paircomp_faster
lcp_paircomp_faster: $(LCP_PAIRCOMP_FASTER_OBJECTS)
				g++ $(OPTIONS) -o lcp_paircomp_faster $(LCP_PAIRCOMP_FASTER_OBJECTS) $(LDFLAGS)

# -----------------------
				
# コンパイル
%.o: %.cpp
				g++ $(CXXFLAGS) -c $< -o $@

# -----------------------

# 不要な中間ファイル（オブジェクトコード）の削除
.PHONY: clean
clean:
				rm -f lcp_random lcp_paircomp lcp_paircomp_faster $(ALL_OBJECTS)
