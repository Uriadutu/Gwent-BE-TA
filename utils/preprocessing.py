import re
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# Inisialisasi stopword remover
stop_factory = StopWordRemoverFactory()
stopword_remover = stop_factory.create_stop_word_remover()

# Fungsi membersihkan teks
def bersihkan_teks(teks: str) -> str:
    teks = teks.replace('\n', ' ')  # Ubah baris baru menjadi spasi
    teks = teks.lower()  # Ubah menjadi huruf kecil semua
    # teks = re.sub(r'\d+', '', teks)  # Hapus angka
    teks = re.sub(r'[^\w\s]', '', teks)  # Hapus karakter selain huruf dan spasi
    teks = stopword_remover.remove(teks)  # Hapus stopword
    return teks.strip()  # Hapus spasi di awal/akhir
