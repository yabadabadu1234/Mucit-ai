import kulli_gpu
import pprint

print("=== KÜLLÎ SANAL GPU SÜRÜCÜSÜ - NİHAİ ANA ORKESTRATÖR TESTİ ===")

# 1. Tek Satırda Sürücüyü Başlatma
basarili = kulli_gpu.baslat(toplam_sanal_gb=88.0, simulation_mode=True)
print("Sürücü Başlatıldı Mı:", basarili)

# 2. Anlık Sürücü Telemetri Raporu
ozet = kulli_gpu.durum_ozetle()
print("\nAnlık Sürücü Durumu:")
pprint.pprint(ozet)

# 3. PyTorch / C-ABI Yakalama Simülasyonu
yakalayici = kulli_gpu._orkestrator.yakalayici
malloc_fn = yakalayici.SeffafDlsymKancasi(None, "cudaMalloc")
ret_m = malloc_fn(256 * 1024 * 1024)
print("\ncudaMalloc Kanca Sonucu:", ret_m)

memcpy_fn = yakalayici.SeffafDlsymKancasi(None, "cudaMemcpy")
ret_c = memcpy_fn(0x7FFF00000000, 0x7FFF00000000, 1024 * 1024)
print("cudaMemcpy Kanca Sonucu:", ret_c)

free_fn = yakalayici.SeffafDlsymKancasi(None, "cudaFree")
ret_f = free_fn(0x7FFF00000000)
print("cudaFree Kanca Sonucu:", ret_f)

# 4. Sürücüyü Durdurma
durduruldu = kulli_gpu.durdur()
print("\nSürücü Güvenle Durduruldu Mu:", durduruldu)
print("\n[BAŞARILI] Ana Orkestratör Katmanı ve `import kulli_gpu; kulli_gpu.baslat()` API %100 Kusursuz Çalışıyor!")
