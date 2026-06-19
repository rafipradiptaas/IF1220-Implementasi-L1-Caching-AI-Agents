"""
 Eksperimen Makalah IF1220 Matematika Diskrit - Sem. II 2025/2026
 Perbandingan Kompleksitas Pencarian Cache: O(n) Linear vs O(1) Hash Map
 untuk Reduksi Konsumsi Token API pada Arsitektur AI Agent
"""

import hashlib
import random
import string
import time


# 1. KONFIGURASI EKSPERIMEN

TOTAL_QUERIES       = 10_000        # total prompt yang masuk ke agent
DUPLICATE_RATE      = 0.30          # 30% sengaja dibuat duplikat
UNIQUE_POOL         = int(TOTAL_QUERIES * (1 - DUPLICATE_RATE))  
AVG_TOKENS_PER_CALL = 850           # asumsi rata-rata token per panggilan API
random.seed(42)                    


# 2. FUNGSI HASH  (domain: teks panjang-bebas, kodomain: digest 256-bit)

def hash_prompt(prompt: str) -> str:
    """h(prompt) -> SHA-256 hex digest. Contoh fungsi (bukan injektif total
    di dunia nyata -> Pigeonhole => kemungkinan collision)."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


# 3. GENERATE DATASET PROMPT (duplikat terkontrol)

def random_prompt(n_words: int = 12) -> str:
    words = [
        "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 9)))
        for _ in range(n_words)
    ]
    return " ".join(words)

pool   = [random_prompt() for _ in range(UNIQUE_POOL)]                 # 7.000 unik
stream = pool + [random.choice(pool)                                   # + 3.000 duplikat
                 for _ in range(TOTAL_QUERIES - UNIQUE_POOL)]
random.shuffle(stream)


# 4. METODE A - CACHE BERBASIS LIST + PENCARIAN LINEAR  =>  O(n)

def run_linear(stream):
    cache_keys, cache_vals = [], []
    hits = 0
    start = time.perf_counter()
    for p in stream:
        key = hash_prompt(p)
        found = False
        for i, k in enumerate(cache_keys):      #  scan linear, O(n)
            if k == key:
                _ = cache_vals[i]               # ambil respons lama (cache hit)
                hits += 1
                found = True
                break
        if not found:                           # cache miss -> "panggil API" -> simpan
            cache_keys.append(key)
            cache_vals.append("LLM_RESPONSE")
    return hits, time.perf_counter() - start



# 5. METODE B - CACHE BERBASIS DICTIONARY (HASH MAP)  =>  O(1) rata-rata

def run_hashmap(stream):
    cache = {}
    hits = 0
    start = time.perf_counter()
    for p in stream:
        key = hash_prompt(p)
        if key in cache:                        # lookup hash map, O(1) avg
            _ = cache[key]                      # cache hit
            hits += 1
        else:
            cache[key] = "LLM_RESPONSE"         # cache miss -> simpan
    return hits, time.perf_counter() - start


# 6. EKSEKUSI & LAPORAN

hits_lin, t_lin   = run_linear(stream)
hits_map, t_map   = run_hashmap(stream)

tokens_saved      = hits_map * AVG_TOKENS_PER_CALL
redundancy_pct    = hits_map / TOTAL_QUERIES * 100
speedup           = t_lin / t_map

print(" HASIL EKSPERIMEN SEMANTIC/EXACT CACHING")
print(f" Total kueri masuk          : {TOTAL_QUERIES:,}")
print(f" Prompt unik (kodomain)     : {UNIQUE_POOL:,}")
print(f" Kueri redundan (cache hit) : {hits_map:,}  ({redundancy_pct:.1f}%)")
print(" PERBANDINGAN RUNTIME")
print(f"  Metode A  O(n) linear list : {t_lin*1000:10.3f} ms")
print(f"  Metode B  O(1) hash map    : {t_map*1000:10.3f} ms")
print(f"  Speedup (A/B)              : {speedup:10.1f}x lebih cepat")
print(" REDUKSI KONSUMSI TOKEN API")
print(f"  Asumsi token / panggilan   : {AVG_TOKENS_PER_CALL:,}")
print(f"  Panggilan API dihindari    : {hits_map:,}")
print(f"  Total token diselamatkan   : {tokens_saved:,}")
print(f"  Penghematan biaya API      : {redundancy_pct:.1f}%")
print(f" Validasi konsistensi (hit A == hit B?) : {hits_lin == hits_map}")
