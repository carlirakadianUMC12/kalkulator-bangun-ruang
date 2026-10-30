import math


def test_perhitungan():
    """Unit test sederhana untuk memverifikasi rumus-rumus di atas."""
    print("--- Menjalankan Pengujian Perhitungan ---")
 
    # Balok
    p, l, t = 2, 3, 4
    assert p * l * t == 24
    assert 2 * (p * l + p * t + l * t) == 52
    print("Test Balok: BERHASIL")
 
    # Bola
    r = 3
    volume_bola = (4 / 3) * math.pi * r ** 3
    assert round(volume_bola, 2) == 113.10
    print("Test Bola: BERHASIL")
 
    # Kerucut
    r, t = 3, 4
    s = math.sqrt(r ** 2 + t ** 2)
    assert s == 5.0
    print("Test Kerucut: BERHASIL")
 
    # Prisma segitiga (3-4-5 adalah segitiga siku-siku)
    a, b, c = 3, 4, 5
    s_keliling = (a + b + c) / 2
    luas_alas = math.sqrt(s_keliling * (s_keliling - a) *
                          (s_keliling - b) * (s_keliling - c))
    assert luas_alas == 6.0
    print("Test Prisma Segitiga: BERHASIL")
 
    # Tabung
    r, t = 2, 5
    volume_tabung = math.pi * r ** 2 * t
    assert round(volume_tabung, 2) == 62.83
    print("Test Tabung: BERHASIL")
 
    print("--- Semua Pengujian Perhitungan Berhasil ---\n")