import tkinter as tk
from tkinter import messagebox
import math
import hashlib
import hmac
import json
import os
import sys


# warna tema (disatuin biar semua warna kalkulator sama)
BG_UTAMA = "#1e1e2e"
BG_KARTU = "#313244"
BG_INPUT = "#45475a"
TEKS_UTAMA = "#cdd6f4"
UNGU = "#cba6f7"
MERAH_MUDA = "#f38ba8"
HIJAU = "#a6e3a1"
BIRU_MUDA = "#89dceb"
ORANYE = "#fab387"
ABU = "#6c7086"

FONT_JUDUL = ("Arial", 16, "bold")
FONT_LABEL = ("Arial", 10)
FONT_HASIL = ("Arial", 11, "bold")


# data akun (disimpan ke file users.json di folder yang sama dengan aplikasi)
# password TIDAK disimpan langsung, tapi dalam bentuk hash + salt (PBKDF2)
def lokasi_file_users():
    if getattr(sys, "frozen", False):  # kalau dijalankan sebagai .exe
        folder = os.path.dirname(sys.executable)
    else:
        folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, "users.json")


FILE_USERS = lokasi_file_users()


def hash_password(password, salt=None):
    """Mengembalikan (salt_hex, hash_hex) dari password."""
    if salt is None:
        salt = os.urandom(16)
    hasil = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                salt, 100_000)
    return salt.hex(), hasil.hex()


def muat_users():
    try:
        with open(FILE_USERS, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def simpan_users(users):
    with open(FILE_USERS, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def cek_login(username, password):
    data = muat_users().get(username)
    if not data:
        return False
    _, hash_hex = hash_password(password, bytes.fromhex(data["salt"]))
    return hmac.compare_digest(hash_hex, data["hash"])


MAX_PERCOBAAN = 3
percobaan_gagal = 0
user_aktif = None


root = tk.Tk()
root.title("Kalkulator Bangun Ruang")
root.geometry("420x480")
root.resizable(False, False)
root.configure(bg=BG_UTAMA)

# tempat semua frame
container = tk.Frame(root, bg=BG_UTAMA)
container.pack(fill="both", expand=True)

frames = {}  # simpan semua frame


def tampilkan_frame(nama_frame):
    """Menampilkan frame yang dipilih ke depan (mengganti 'halaman')."""
    frame = frames[nama_frame]
    frame.tkraise()


def buat_entry_baris(parent, label_text):
    """Membuat satu baris label + input, mengembalikan widget Entry-nya."""
    row = tk.Frame(parent, bg=BG_KARTU)
    row.pack(fill="x", pady=4)
    tk.Label(row, text=label_text, width=14, anchor="w", bg=BG_KARTU,
             fg=TEKS_UTAMA, font=FONT_LABEL).pack(side="left")
    entry = tk.Entry(row, font=FONT_LABEL, bg=BG_INPUT, fg=TEKS_UTAMA,
                     insertbackground="white", relief="flat", width=16)
    entry.pack(side="left", ipady=4)
    return entry


def buat_tombol_aksi(parent, teks_hitung, fungsi_hitung, fungsi_reset):
    """Membuat baris tombol Hitung, Reset, dan Kembali ke Menu."""
    btn_frame = tk.Frame(parent, bg=BG_UTAMA)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text=teks_hitung, command=fungsi_hitung, bg=UNGU,
              fg=BG_UTAMA, font=("Arial", 10, "bold"), relief="flat",
              padx=15, pady=6).pack(side="left", padx=6)

    tk.Button(btn_frame, text="Reset", command=fungsi_reset, bg=MERAH_MUDA,
              fg=BG_UTAMA, font=("Arial", 10, "bold"), relief="flat",
              padx=15, pady=6).pack(side="left", padx=6)

    tk.Button(parent, text="< Kembali ke Menu",
              command=lambda: tampilkan_frame("menu"), bg=BG_UTAMA,
              fg=ABU, font=("Arial", 9, "underline"), relief="flat",
              bd=0, cursor="hand2").pack(pady=(4, 10))


# halaman login
def buat_frame_login():
    frame = tk.Frame(container, bg=BG_UTAMA)
    frame.place(x=0, y=0, relwidth=1, relheight=1)

    tk.Label(frame, text="KALKULATOR BANGUN RUANG", font=FONT_JUDUL,
             bg=BG_UTAMA, fg=UNGU).pack(pady=(50, 5))
    tk.Label(frame, text="Silakan login untuk melanjutkan",
             font=FONT_LABEL, bg=BG_UTAMA, fg=TEKS_UTAMA).pack(pady=(0, 25))

    kartu = tk.Frame(frame, bg=BG_KARTU, padx=20, pady=15)
    kartu.pack(padx=20, fill="x")

    entry_user = buat_entry_baris(kartu, "Username:")
    entry_pass = buat_entry_baris(kartu, "Password:")
    entry_pass.config(show="*")

    # checkbox lihat/sembunyikan password
    tampil_pass = tk.BooleanVar(value=False)

    def toggle_password():
        entry_pass.config(show="" if tampil_pass.get() else "*")

    tk.Checkbutton(kartu, text="Tampilkan password", variable=tampil_pass,
                   command=toggle_password, bg=BG_KARTU, fg=TEKS_UTAMA,
                   selectcolor=BG_INPUT, activebackground=BG_KARTU,
                   activeforeground=TEKS_UTAMA, font=("Arial", 9),
                   bd=0, highlightthickness=0).pack(anchor="w", pady=(6, 0))

    label_status = tk.Label(frame, text="", font=("Arial", 9),
                            bg=BG_UTAMA, fg=MERAH_MUDA)

    btn_login = tk.Button(frame, text="Login", bg=UNGU, fg=BG_UTAMA,
                          font=("Arial", 11, "bold"), relief="flat",
                          padx=30, pady=6)

    def proses_login(event=None):
        global percobaan_gagal, user_aktif

        username = entry_user.get().strip().lower()
        password = entry_pass.get()

        if not username or not password:
            label_status.config(text="Username dan password harus diisi!")
            return

        if cek_login(username, password):
            percobaan_gagal = 0
            user_aktif = username
            entry_user.delete(0, tk.END)
            entry_pass.delete(0, tk.END)
            label_status.config(text="")
            label_selamat_datang.config(text=f"Halo, {user_aktif}!")
            tampilkan_frame("menu")
        else:
            percobaan_gagal += 1
            sisa = MAX_PERCOBAAN - percobaan_gagal
            entry_pass.delete(0, tk.END)
            if sisa <= 0:
                messagebox.showerror(
                    "Login Gagal",
                    "Terlalu banyak percobaan gagal. Aplikasi akan ditutup.")
                root.destroy()
                return
            label_status.config(
                text=f"Username atau password salah! Sisa percobaan: {sisa}")

    btn_login.config(command=proses_login)
    btn_login.pack(pady=(20, 8))
    label_status.pack()

    def ke_halaman_daftar():
        label_status.config(text="")
        tampilkan_frame("daftar")

    tk.Button(frame, text="Belum punya akun? Daftar di sini",
              command=ke_halaman_daftar, bg=BG_UTAMA, fg=BIRU_MUDA,
              activebackground=BG_UTAMA, activeforeground=UNGU,
              font=("Arial", 9, "underline"), relief="flat", bd=0,
              cursor="hand2").pack(pady=(14, 0))

    # tekan Enter untuk login
    entry_user.bind("<Return>", proses_login)
    entry_pass.bind("<Return>", proses_login)

    # simpan referensi supaya bisa dikosongkan saat logout
    frame.entry_user = entry_user
    frame.entry_pass = entry_pass
    frame.label_status = label_status

    frames["login"] = frame
    entry_user.focus_set()


# halaman daftar akun
def buat_frame_daftar():
    frame = tk.Frame(container, bg=BG_UTAMA)
    frame.place(x=0, y=0, relwidth=1, relheight=1)

    tk.Label(frame, text="BUAT AKUN BARU", font=("Arial", 14, "bold"),
             bg=BG_UTAMA, fg=UNGU).pack(pady=(40, 5))
    tk.Label(frame, text="Isi data di bawah untuk mendaftar",
             font=FONT_LABEL, bg=BG_UTAMA, fg=TEKS_UTAMA).pack(pady=(0, 20))

    kartu = tk.Frame(frame, bg=BG_KARTU, padx=20, pady=15)
    kartu.pack(padx=20, fill="x")

    entry_user = buat_entry_baris(kartu, "Username:")
    entry_pass = buat_entry_baris(kartu, "Password:")
    entry_ulang = buat_entry_baris(kartu, "Konfirmasi:")
    entry_pass.config(show="*")
    entry_ulang.config(show="*")

    tampil_pass = tk.BooleanVar(value=False)

    def toggle_password():
        mode = "" if tampil_pass.get() else "*"
        entry_pass.config(show=mode)
        entry_ulang.config(show=mode)

    tk.Checkbutton(kartu, text="Tampilkan password", variable=tampil_pass,
                   command=toggle_password, bg=BG_KARTU, fg=TEKS_UTAMA,
                   selectcolor=BG_INPUT, activebackground=BG_KARTU,
                   activeforeground=TEKS_UTAMA, font=("Arial", 9),
                   bd=0, highlightthickness=0).pack(anchor="w", pady=(6, 0))

    tk.Label(kartu, text="* username min. 3 karakter, password min. 6 karakter",
             bg=BG_KARTU, fg=ABU, font=("Arial", 8)).pack(anchor="w",
                                                         pady=(4, 0))

    label_status = tk.Label(frame, text="", font=("Arial", 9),
                            bg=BG_UTAMA, fg=MERAH_MUDA)

    def bersihkan():
        for e in (entry_user, entry_pass, entry_ulang):
            e.delete(0, tk.END)
        label_status.config(text="")

    def proses_daftar(event=None):
        username = entry_user.get().strip().lower()
        password = entry_pass.get()
        ulang = entry_ulang.get()

        if not username or not password or not ulang:
            label_status.config(text="Semua kolom harus diisi!")
            return
        if len(username) < 3 or " " in username:
            label_status.config(
                text="Username min. 3 karakter dan tanpa spasi!")
            return
        if len(password) < 6:
            label_status.config(text="Password minimal 6 karakter!")
            return
        if password != ulang:
            label_status.config(text="Konfirmasi password tidak sama!")
            return

        users = muat_users()
        if username in users:
            label_status.config(text="Username sudah dipakai!")
            return

        salt, hash_hex = hash_password(password)
        users[username] = {"salt": salt, "hash": hash_hex}
        try:
            simpan_users(users)
        except OSError:
            messagebox.showerror(
                "Error", "Akun gagal disimpan. Pastikan folder aplikasi "
                         "bisa ditulis.")
            return

        messagebox.showinfo("Berhasil",
                            f"Akun '{username}' berhasil dibuat! Silakan login.")
        bersihkan()
        login_frame = frames["login"]
        login_frame.entry_user.delete(0, tk.END)
        login_frame.entry_user.insert(0, username)
        login_frame.entry_pass.delete(0, tk.END)
        login_frame.label_status.config(text="")
        tampilkan_frame("login")
        login_frame.entry_pass.focus_set()

    def kembali_ke_login():
        bersihkan()
        tampilkan_frame("login")

    tk.Button(frame, text="Daftar", command=proses_daftar, bg=UNGU,
              fg=BG_UTAMA, font=("Arial", 11, "bold"), relief="flat",
              padx=30, pady=6).pack(pady=(20, 8))
    label_status.pack()
    tk.Button(frame, text="< Kembali ke Login", command=kembali_ke_login,
              bg=BG_UTAMA, fg=ABU, font=("Arial", 9, "underline"),
              relief="flat", bd=0, cursor="hand2").pack(pady=(14, 0))

    for e in (entry_user, entry_pass, entry_ulang):
        e.bind("<Return>", proses_daftar)

    frames["daftar"] = frame


def logout():
    """Kembali ke halaman login dan menghapus sesi user."""
    global user_aktif
    if messagebox.askyesno("Logout", "Yakin ingin logout?"):
        user_aktif = None
        login_frame = frames["login"]
        login_frame.entry_user.delete(0, tk.END)
        login_frame.entry_pass.delete(0, tk.END)
        login_frame.label_status.config(text="")
        tampilkan_frame("login")
        login_frame.entry_user.focus_set()


# menu utama
label_selamat_datang = None


def buat_frame_menu():
    global label_selamat_datang

    frame = tk.Frame(container, bg=BG_UTAMA)
    frame.place(x=0, y=0, relwidth=1, relheight=1)

    tk.Label(frame, text="KALKULATOR BANGUN RUANG", font=FONT_JUDUL,
             bg=BG_UTAMA, fg=UNGU).pack(pady=(20, 2))
    label_selamat_datang = tk.Label(frame, text="", font=("Arial", 9),
                                    bg=BG_UTAMA, fg=ORANYE)
    label_selamat_datang.pack()
    tk.Label(frame, text="Pilih bangun ruang yang ingin dihitung:",
             font=FONT_LABEL, bg=BG_UTAMA, fg=TEKS_UTAMA).pack(pady=(6, 12))

    menu_items = [
        ("Balok", "balok"),
        ("Bola", "bola"),
        ("Kerucut", "kerucut"),
        ("Prisma Segitiga", "prisma"),
        ("Tabung", "tabung"),
    ]

    for teks, nama in menu_items:
        tk.Button(frame, text=teks, font=("Arial", 11, "bold"),
                  bg=BG_KARTU, fg=TEKS_UTAMA, relief="flat",
                  activebackground=UNGU, activeforeground=BG_UTAMA,
                  width=25, pady=8,
                  command=lambda n=nama: tampilkan_frame(n)).pack(pady=4)

    tk.Button(frame, text="Logout", command=logout, bg=MERAH_MUDA,
              fg=BG_UTAMA, font=("Arial", 10, "bold"), relief="flat",
              padx=20, pady=4).pack(pady=(14, 0))

    frames["menu"] = frame


# balok
def buat_frame_balok():
    frame = tk.Frame(container, bg=BG_UTAMA)
    frame.place(x=0, y=0, relwidth=1, relheight=1)

    tk.Label(frame, text="KALKULATOR BALOK", font=("Arial", 14, "bold"),
             bg=BG_UTAMA, fg=UNGU).pack(pady=12)

    kartu = tk.Frame(frame, bg=BG_KARTU, padx=20, pady=15)
    kartu.pack(padx=20, fill="x")

    entry_p = buat_entry_baris(kartu, "Panjang (p):")
    entry_l = buat_entry_baris(kartu, "Lebar (l):")
    entry_t = buat_entry_baris(kartu, "Tinggi (t):")

    hasil_volume = tk.Label(frame, text="Volume: -", font=FONT_HASIL,
                            bg=BG_UTAMA, fg=HIJAU)
    hasil_luas = tk.Label(frame, text="Luas Permukaan: -", font=FONT_HASIL,
                          bg=BG_UTAMA, fg=BIRU_MUDA)

    def hitung_balok():
        try:
            p = float(entry_p.get())
            l = float(entry_l.get())
            t = float(entry_t.get())
            if p <= 0 or l <= 0 or t <= 0:
                messagebox.showerror("Error", "Nilai harus lebih dari 0!")
                return
            volume = p * l * t
            luas = 2 * (p * l + p * t + l * t)
            hasil_volume.config(text=f"Volume: {volume:.2f} satuan³")
            hasil_luas.config(text=f"Luas Permukaan: {luas:.2f} satuan²")
        except ValueError:
            messagebox.showerror("Error", "Masukkan angka yang valid!")

    def reset_balok():
        for e in (entry_p, entry_l, entry_t):
            e.delete(0, tk.END)
        hasil_volume.config(text="Volume: -")
        hasil_luas.config(text="Luas Permukaan: -")

    buat_tombol_aksi(frame, "Hitung", hitung_balok, reset_balok)
    hasil_volume.pack(pady=2)
    hasil_luas.pack()

    frames["balok"] = frame


# bola
def buat_frame_bola():
    frame = tk.Frame(container, bg=BG_UTAMA)
    frame.place(x=0, y=0, relwidth=1, relheight=1)

    tk.Label(frame, text="KALKULATOR BOLA", font=("Arial", 14, "bold"),
             bg=BG_UTAMA, fg=UNGU).pack(pady=12)

    kartu = tk.Frame(frame, bg=BG_KARTU, padx=20, pady=15)
    kartu.pack(padx=20, fill="x")

    entry_r = buat_entry_baris(kartu, "Jari-jari (r):")

    hasil_volume = tk.Label(frame, text="Volume: -", font=FONT_HASIL,
                            bg=BG_UTAMA, fg=HIJAU)
    hasil_luas = tk.Label(frame, text="Luas Permukaan: -", font=FONT_HASIL,
                          bg=BG_UTAMA, fg=BIRU_MUDA)

    def hitung_bola():
        try:
            r = float(entry_r.get())
            if r <= 0:
                messagebox.showerror("Error", "Nilai harus lebih dari 0!")
                return
            volume = (4 / 3) * math.pi * r ** 3
            luas = 4 * math.pi * r ** 2
            hasil_volume.config(text=f"Volume: {volume:.2f} satuan³")
            hasil_luas.config(text=f"Luas Permukaan: {luas:.2f} satuan²")
        except ValueError:
            messagebox.showerror("Error", "Masukkan angka yang valid!")

    def reset_bola():
        entry_r.delete(0, tk.END)
        hasil_volume.config(text="Volume: -")
        hasil_luas.config(text="Luas Permukaan: -")

    buat_tombol_aksi(frame, "Hitung", hitung_bola, reset_bola)
    hasil_volume.pack(pady=2)
    hasil_luas.pack()

    frames["bola"] = frame


# kerucut
def buat_frame_kerucut():
    frame = tk.Frame(container, bg=BG_UTAMA)
    frame.place(x=0, y=0, relwidth=1, relheight=1)

    tk.Label(frame, text="KALKULATOR KERUCUT", font=("Arial", 14, "bold"),
             bg=BG_UTAMA, fg=UNGU).pack(pady=12)

    kartu = tk.Frame(frame, bg=BG_KARTU, padx=20, pady=15)
    kartu.pack(padx=20, fill="x")

    entry_r = buat_entry_baris(kartu, "Jari-jari (r):")
    entry_t = buat_entry_baris(kartu, "Tinggi (t):")

    hasil_s = tk.Label(frame, text="Garis Pelukis (s): -", font=FONT_LABEL,
                       bg=BG_UTAMA, fg=ORANYE)
    hasil_volume = tk.Label(frame, text="Volume: -", font=FONT_HASIL,
                            bg=BG_UTAMA, fg=HIJAU)
    hasil_luas = tk.Label(frame, text="Luas Permukaan: -", font=FONT_HASIL,
                          bg=BG_UTAMA, fg=BIRU_MUDA)

    def hitung_kerucut():
        try:
            r = float(entry_r.get())
            t = float(entry_t.get())
            if r <= 0 or t <= 0:
                messagebox.showerror("Error", "Nilai harus lebih dari 0!")
                return
            s = math.sqrt(r ** 2 + t ** 2)
            volume = (1 / 3) * math.pi * r ** 2 * t
            luas = math.pi * r * (r + s)
            hasil_volume.config(text=f"Volume: {volume:.2f} satuan³")
            hasil_luas.config(text=f"Luas Permukaan: {luas:.2f} satuan²")
            hasil_s.config(text=f"Garis Pelukis (s): {s:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Masukkan angka yang valid!")

    def reset_kerucut():
        entry_r.delete(0, tk.END)
        entry_t.delete(0, tk.END)
        hasil_volume.config(text="Volume: -")
        hasil_luas.config(text="Luas Permukaan: -")
        hasil_s.config(text="Garis Pelukis (s): -")

    buat_tombol_aksi(frame, "Hitung", hitung_kerucut, reset_kerucut)
    hasil_s.pack(pady=2)
    hasil_volume.pack(pady=2)
    hasil_luas.pack()

    frames["kerucut"] = frame


# prisma segitiga
def buat_frame_prisma():
    frame = tk.Frame(container, bg=BG_UTAMA)
    frame.place(x=0, y=0, relwidth=1, relheight=1)

    tk.Label(frame, text="KALKULATOR PRISMA SEGITIGA",
             font=("Arial", 13, "bold"), bg=BG_UTAMA, fg=UNGU).pack(pady=12)

    kartu = tk.Frame(frame, bg=BG_KARTU, padx=20, pady=15)
    kartu.pack(padx=20, fill="x")

    entry_a = buat_entry_baris(kartu, "Sisi a:")
    entry_b = buat_entry_baris(kartu, "Sisi b:")
    entry_c = buat_entry_baris(kartu, "Sisi c:")
    entry_t = buat_entry_baris(kartu, "Tinggi (t):")

    tk.Label(kartu, text="* a, b, c = sisi-sisi segitiga alas", bg=BG_KARTU,
             fg=ABU, font=("Arial", 8)).pack(anchor="w", pady=(4, 0))

    hasil_alas = tk.Label(frame, text="Luas Alas: -", font=FONT_LABEL,
                          bg=BG_UTAMA, fg=ORANYE)
    hasil_volume = tk.Label(frame, text="Volume: -", font=FONT_HASIL,
                            bg=BG_UTAMA, fg=HIJAU)
    hasil_luas = tk.Label(frame, text="Luas Permukaan: -", font=FONT_HASIL,
                          bg=BG_UTAMA, fg=BIRU_MUDA)

    def hitung_prisma():
        try:
            a = float(entry_a.get())
            b = float(entry_b.get())
            c = float(entry_c.get())
            t = float(entry_t.get())
            if a <= 0 or b <= 0 or c <= 0 or t <= 0:
                messagebox.showerror("Error", "Nilai harus lebih dari 0!")
                return
            if a + b <= c or a + c <= b or b + c <= a:
                messagebox.showerror(
                    "Error", "Sisi a, b, c tidak bisa membentuk segitiga!")
                return

            s = (a + b + c) / 2
            luas_alas = math.sqrt(s * (s - a) * (s - b) * (s - c))
            volume = luas_alas * t
            luas = (2 * luas_alas) + ((a + b + c) * t)
            hasil_volume.config(text=f"Volume: {volume:.2f} satuan³")
            hasil_luas.config(text=f"Luas Permukaan: {luas:.2f} satuan²")
            hasil_alas.config(text=f"Luas Alas: {luas_alas:.2f} satuan²")
        except ValueError:
            messagebox.showerror("Error", "Masukkan angka yang valid!")

    def reset_prisma():
        for e in (entry_a, entry_b, entry_c, entry_t):
            e.delete(0, tk.END)
        hasil_volume.config(text="Volume: -")
        hasil_luas.config(text="Luas Permukaan: -")
        hasil_alas.config(text="Luas Alas: -")

    buat_tombol_aksi(frame, "Hitung", hitung_prisma, reset_prisma)
    hasil_alas.pack(pady=2)
    hasil_volume.pack(pady=2)
    hasil_luas.pack()

    frames["prisma"] = frame


# tabung
def buat_frame_tabung():
    frame = tk.Frame(container, bg=BG_UTAMA)
    frame.place(x=0, y=0, relwidth=1, relheight=1)

    tk.Label(frame, text="KALKULATOR TABUNG", font=("Arial", 14, "bold"),
             bg=BG_UTAMA, fg=UNGU).pack(pady=12)

    kartu = tk.Frame(frame, bg=BG_KARTU, padx=20, pady=15)
    kartu.pack(padx=20, fill="x")

    entry_r = buat_entry_baris(kartu, "Jari-jari (r):")
    entry_t = buat_entry_baris(kartu, "Tinggi (t):")

    hasil_volume = tk.Label(frame, text="Volume: -", font=FONT_HASIL,
                            bg=BG_UTAMA, fg=HIJAU)
    hasil_luas = tk.Label(frame, text="Luas Permukaan: -", font=FONT_HASIL,
                          bg=BG_UTAMA, fg=BIRU_MUDA)

    def hitung_tabung():
        try:
            r = float(entry_r.get())
            t = float(entry_t.get())
            if r <= 0 or t <= 0:
                messagebox.showerror("Error", "Nilai harus lebih dari 0!")
                return
            volume = math.pi * r ** 2 * t
            luas = 2 * math.pi * r * (r + t)
            hasil_volume.config(text=f"Volume: {volume:.2f} satuan³")
            hasil_luas.config(text=f"Luas Permukaan: {luas:.2f} satuan²")
        except ValueError:
            messagebox.showerror("Error", "Masukkan angka yang valid!")

    def reset_tabung():
        entry_r.delete(0, tk.END)
        entry_t.delete(0, tk.END)
        hasil_volume.config(text="Volume: -")
        hasil_luas.config(text="Luas Permukaan: -")

    buat_tombol_aksi(frame, "Hitung", hitung_tabung, reset_tabung)
    hasil_volume.pack(pady=2)
    hasil_luas.pack()

    frames["tabung"] = frame


# halaman awal
buat_frame_menu()
buat_frame_balok()
buat_frame_bola()
buat_frame_kerucut()
buat_frame_prisma()
buat_frame_tabung()
buat_frame_daftar()
buat_frame_login()  # dibuat terakhir supaya berada paling depan


if __name__ == "__main__":
    tampilkan_frame("login")
    root.mainloop()