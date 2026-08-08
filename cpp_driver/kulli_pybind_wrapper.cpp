/*
 * ================================================================================
 * KÜLLÎ C++ PYBIND11 BINDING WRAPPER (PYTHON-C++ İRTİBAT VE MASKELENME KÖPRÜSÜ)
 * MODÜL 9: PyBind11 / C-ABI Binding Bridge
 * 
 * Bu modül, Python tarafının ('import kulli_vmm_cpp' veya 'ctypes.CDLL') en alt seviyedeki
 * C++ CUDA VMM sürücü çekirdeğine (KulliVirtualGPUDriver) doğrudan ve milisaniyenin altında
 * erişmesini sağlar.
 * 
 * ÖZELLİKLERİ:
 * 1. Çift Yönlü İrtibat: Hem PyBind11 Native Module hem de C-ABI (extern "C") C-Types köprüsü içerir.
 * 2. C++ İstisna Güvenliği (Exception Safety): C++ seviyesindeki hataları yakalar, Python'a
 *    güvenli biçimde iletir ve çökme (Segmentation Fault) yaşanmasını engeller.
 * 3. Donanımsal Maskeleme: C++ seviyesinde çalışan harici kütüphaneler için 'cudaGetDeviceCount'
 *    ve 'cudaMemGetInfo' C-API kancalarını dışa aktarır (export).
 * ================================================================================
 */

#include <iostream>
#include <memory>
#include <cstdint>
#include <exception>

// C++ Sürücü Çekirdeği Dahil Edilir
#ifndef KULLI_VMM_CUDA_CPP_INCLUDED
#define KULLI_VMM_CUDA_CPP_INCLUDED
#include "kulli_vmm_cuda.cpp"
#endif

// ================================================================================
// 1. KISIM: C-ABI EXPORT İMZALARI (ctypes / CDLL / CFFI UYUMLU C KÖPRÜSÜ)
// ================================================================================

extern "C" {

    /**
     * @brief Sürücü Nesnesi Oluşturucu (C-ABI)
     */
    KulliVirtualGPUDriver* kulli_cpp_create_driver() {
        try {
            return new KulliVirtualGPUDriver();
        } catch (const std::exception& e) {
            std::cerr << "[C-ABI Error] Driver creation failed: " << e.what() << std::endl;
            return nullptr;
        } catch (...) {
            std::cerr << "[C-ABI Error] Unknown exception in driver creation!" << std::endl;
            return nullptr;
        }
    }

    /**
     * @brief Sürücü İlklendirici (C-ABI)
     */
    bool kulli_cpp_init_driver(KulliVirtualGPUDriver* driver) {
        if (!driver) return false;
        try {
            return driver->initialize_virtual_vram();
        } catch (const std::exception& e) {
            std::cerr << "[C-ABI Error] Driver initialization failed: " << e.what() << std::endl;
            return false;
        }
    }

    /**
     * @brief Sanal VRAM Tamponu Tahsis Edici (C-ABI)
     */
    uint64_t kulli_cpp_allocate_buffer(KulliVirtualGPUDriver* driver, uint64_t size_bytes) {
        if (!driver) return 0;
        try {
            return driver->allocate_virtual_buffer(size_bytes);
        } catch (const std::exception& e) {
            std::cerr << "[C-ABI Error] Allocation failed: " << e.what() << std::endl;
            return 0;
        }
    }

    /**
     * @brief Fiziki VRAM Haritalayıcı (C-ABI)
     */
    bool kulli_cpp_map_gpu(KulliVirtualGPUDriver* driver, uint64_t virt_ptr, uint64_t size_bytes, int gpu_id) {
        if (!driver) return false;
        try {
            return driver->map_gpu_memory(virt_ptr, size_bytes, gpu_id);
        } catch (const std::exception& e) {
            std::cerr << "[C-ABI Error] Map GPU memory failed: " << e.what() << std::endl;
            return false;
        }
    }

    /**
     * @brief Fiziki VRAM Harita Sökücü (C-ABI)
     */
    bool kulli_cpp_unmap_gpu(KulliVirtualGPUDriver* driver, uint64_t virt_ptr, uint64_t size_bytes) {
        if (!driver) return false;
        try {
            return driver->unmap_gpu_memory(virt_ptr, size_bytes);
        } catch (const std::exception& e) {
            std::cerr << "[C-ABI Error] Unmap GPU memory failed: " << e.what() << std::endl;
            return false;
        }
    }

    /**
     * @brief Telemetri ve Adres Sorgu Fonksiyonları (C-ABI)
     */
    uint64_t kulli_cpp_get_base_address(KulliVirtualGPUDriver* driver) {
        return driver ? driver->get_virtual_base_address() : 0;
    }

    uint64_t kulli_cpp_get_total_bytes(KulliVirtualGPUDriver* driver) {
        return driver ? driver->get_total_virtual_bytes() : 0;
    }

    uint64_t kulli_cpp_get_allocated_bytes(KulliVirtualGPUDriver* driver) {
        return driver ? driver->get_allocated_bytes() : 0;
    }

    uint64_t kulli_cpp_get_free_bytes(KulliVirtualGPUDriver* driver) {
        return driver ? driver->get_free_virtual_bytes() : 0;
    }

    int kulli_cpp_get_gpu_count(KulliVirtualGPUDriver* driver) {
        return driver ? driver->get_gpu_count() : 0;
    }

    uint64_t kulli_cpp_get_gpu_vram_capacity(KulliVirtualGPUDriver* driver, int gpu_id) {
        return driver ? driver->get_gpu_vram_capacity(gpu_id) : 0;
    }

    uint64_t kulli_cpp_get_gpu_free_vram(KulliVirtualGPUDriver* driver, int gpu_id) {
        return driver ? driver->get_gpu_free_vram(gpu_id) : 0;
    }

    bool kulli_cpp_is_valid_address(KulliVirtualGPUDriver* driver, uint64_t ptr, uint64_t size_bytes) {
        return driver ? driver->is_valid_virtual_address(ptr, size_bytes) : false;
    }

    /**
     * @brief Sürücü Yıkıcı (C-ABI)
     */
    void kulli_cpp_destroy_driver(KulliVirtualGPUDriver* driver) {
        if (driver) {
            try {
                driver->cleanup();
                delete driver;
            } catch (const std::exception& e) {
                std::cerr << "[C-ABI Error] Driver destruction notice: " << e.what() << std::endl;
            }
        }
    }

    /**
     * @brief C++ Uygulamaları İçin CUDA Sembol Kancaları (CUDA Symbol Interception Hooks)
     */
    int kulli_cudaGetDeviceCount(int* count) {
        return cudaGetDeviceCount(count);
    }

    int kulli_cudaMemGetInfo(size_t* free_bytes, size_t* total_bytes) {
        return cudaMemGetInfo(free_bytes, total_bytes);
    }

} // extern "C"


// ================================================================================
// 2. KISIM: PYBIND11 NATIVE PYTHON MODÜL TANIMI (IMPORT KULLI_VMM_CPP)
// ================================================================================

#if defined(KULLI_PYBIND11_ENABLED) || __has_include(<pybind11/pybind11.h>)

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

/**
 * @brief Python tarafında 'import kulli_vmm_cpp' diyerek doğrudan çağrılan C++ Modülü
 */
PYBIND11_MODULE(kulli_vmm_cpp, m) {
    m.doc() = "Küllî Sanal GPU C++ CUDA VMM Sürücü Çekirdeği PyBind11 Köprüsü";

    // KulliVirtualGPUDriver Sınıfının Python Bağlantısı
    py::class_<KulliVirtualGPUDriver, std::shared_ptr<KulliVirtualGPUDriver>>(m, "KulliVirtualGPUDriver")
        .def(py::init<>(), "Küllî Sanal GPU C++ Sürücü Çekirdeği Oluşturucu")
        .def("initialize_virtual_vram", &KulliVirtualGPUDriver::initialize_virtual_vram, 
             "Sistemdeki tüm GPU VRAM'lerini canlı sorgular ve kesintisiz sanal adresi ilklendirir.")
        .def("allocate_virtual_buffer", &KulliVirtualGPUDriver::allocate_virtual_buffer, 
             py::arg("size_bytes"), 
             "Sanal VRAM uzayından granüler boyutlu tampon rezerve eder.")
        .def("map_gpu_memory", &KulliVirtualGPUDriver::map_gpu_memory, 
             py::arg("virt_ptr"), py::arg("size_bytes"), py::arg("gpu_id"), 
             "Fiziki GPU VRAM'ini sanal adrese haritalar ve TÜM GPU'lara READWRITE izni açar.")
        .def("unmap_gpu_memory", &KulliVirtualGPUDriver::unmap_gpu_memory, 
             py::arg("virt_ptr"), py::arg("size_bytes"), 
             "Sanal adresteki fiziki VRAM haritasını söker ve kaynakları iade eder.")
        .def("get_virtual_base_address", &KulliVirtualGPUDriver::get_virtual_base_address, 
             "Rezerve edilen 64-bit sanal başlangıç adresini döndürür.")
        .def("get_total_virtual_bytes", &KulliVirtualGPUDriver::get_total_virtual_bytes, 
             "Toplam sanal VRAM kapasitesini bayt cinsinden döndürür.")
        .def("get_allocated_bytes", &KulliVirtualGPUDriver::get_allocated_bytes, 
             "Tahsis edilmiş toplam sanal VRAM miktarını döndürür.")
        .def("get_free_virtual_bytes", &KulliVirtualGPUDriver::get_free_virtual_bytes, 
             "Boştaki kesintisiz sanal VRAM miktarını döndürür.")
        .def("get_gpu_count", &KulliVirtualGPUDriver::get_gpu_count, 
             "Sistemdeki canlı fiziki GPU sayısını döndürür.")
        .def("get_gpu_vram_capacity", &KulliVirtualGPUDriver::get_gpu_vram_capacity, 
             py::arg("gpu_id"), 
             "Belirtilen fiziki GPU'nun toplam VRAM kapasitesini döndürür.")
        .def("get_gpu_free_vram", &KulliVirtualGPUDriver::get_gpu_free_vram, 
             py::arg("gpu_id"), 
             "Belirtilen fiziki GPU'nun anlık boş VRAM miktarını döndürür.")
        .def("is_valid_virtual_address", &KulliVirtualGPUDriver::is_valid_virtual_address, 
             py::arg("ptr"), py::arg("size_bytes") = 1, 
             "Sanal adresin ve aralığın Koruma Sayfası (Guard Page) sınırları dahilinde geçerli olup olmadığını doğrular.")
        .def("cleanup", &KulliVirtualGPUDriver::cleanup, 
             "Tüm C++ VMM haritalarını unmap eder ve donanım kaynaklarını C++ seviyesinde serbest bırakır.");

    // C++ Seviyesi Yürütme ve Maskeleme Yardımcıları
    m.def("get_virtual_gpu_count", []() {
        int count = 0;
        cudaGetDeviceCount(&count);
        return count;
    }, "Sanal GPU Sayısını Döndürür (C++ Maskeli: Her zaman 1)");

    m.def("get_virtual_vram_info", [](int gpu_id) {
        size_t free_bytes = 0, total_bytes = 0;
        cudaMemGetInfo(&free_bytes, &total_bytes);
        return std::make_pair(free_bytes, total_bytes);
    }, py::arg("gpu_id") = 0, "Sanal VRAM Bilgisini Döndürür (C++ Maskeli: Canlı Boş / Toplam Sanal VRAM)");

}

#endif // KULLI_PYBIND11_ENABLED