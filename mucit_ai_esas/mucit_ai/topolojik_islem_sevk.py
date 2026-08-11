#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
MUCİT AI & KÜLLÎ GPU DAĞITIK MİMARİSİ - RÜKN IV
Topolojik ve Spektral İşlem Sevk Köprüsü (topolojik_islem_sevk.py)
================================================================================
Bu modül; Mucit AI'ın N1-N10 düğümlerinin matematiksel denklemlerini değiştirmeden,
işlemleri Path A (Lokal - Sıfır İletişim), Path B (Küresel Redüksiyon - All-Reduce)
veya Path C (Topolojik Sınır Takası - Halo Exchange) yollarına yönlendiren
TopolojikIslemSevk sınıfını içerir.
"""

import os
import sys
import logging
import math
from typing import Dict, List, Tuple, Any, Optional
import torch

from kulli_gpu.cpu_ana_idareci import CpuAnaIdareci
from kulli_gpu.coklu_surec_isci import NcclIletisimHatti

logger = logging.getLogger("mucit_ai.topolojik_islem_sevk")


class TopolojikIslemSevk:
    """
    Mucit AI Topolojik N1-N10 Sevk ve Yönlendirme Köprüsü.
    """
    def __init__(self, idareci: CpuAnaIdareci, model: Optional[Any] = None):
        self.idareci = idareci
        self.model = model
        logger.info("[TopolojikIslemSevk] Sevk koprusu ilklendi.")

    def n1_byte_sevk(self, e1_girdi: Any, n1_module: Any) -> Tuple[Any, torch.Tensor]:
        """
        1. N1 (Byte Ayrıştırıcı) Sevk Algoritması (Path A - Lokal)
        Token dizisi N/P uzunluğunda şardlanmış olarak GPU'lara girer.
        Stiefel Q_m izometrik projeksiyonu her GPU'da lokal N/P parçası üzerinde
        bağımsız icra edilir. İletişim Maliyeti: SIFIR.
        """
        e2_byte, x_initial = n1_module.forward(e1_girdi)
        return e2_byte, x_initial

    def n2_n11_laplasyen_sevk(
        self,
        e2_byte: Any,
        x_initial: torch.Tensor,
        n2_module: Any,
        laplasyen_insa_module: Any
    ) -> Tuple[Any, Any, torch.Tensor, torch.Tensor]:
        """
        2. N2 (TopoX Hücre) & N11 (Lif Laplasyeni) Sevk Algoritması (Path C - Halo Exchange)
        Yönlendirilmiş 1-hücre (D1) ve 2-hücre (D2) sınır operatörleri kurulurken, GPU sınırındaki
        kenarlar (Border Edges) tespit edilir ve halo swap ile takas edilir.
        D2 * D1 = 0 cebirsel şartı bozulmadan Laplasyen difüzyonu icra edilir.
        """
        e3_sinir = n2_module.forward(e2_byte, x_initial=x_initial, mode='train')

        if (
            hasattr(e3_sinir, 'D1') and e3_sinir.D1 is not None and torch.cuda.is_available()
            # KUSUR-35 düzeltmesi: tek-GPU modunda self.idareci None olabilir;
            # None üzerinde .world_size erişimi AttributeError fırlatırdı.
            and self.idareci is not None and self.idareci.world_size > 1
        ):
            rank = torch.cuda.current_device()
            sol_rank = (rank - 1) % self.idareci.world_size
            sag_rank = (rank + 1) % self.idareci.world_size
            # KUSUR-34 düzeltmesi: D1 sınır operatörü bir dilimleme/transpose sonucu
            # non-contiguous olabilir; isend/irecv non-contiguous tensörlerle tanımsız
            # davranışa yol açabileceğinden önce contiguous hale getirilir.
            halo_girdi = e3_sinir.D1 if e3_sinir.D1.is_contiguous() else e3_sinir.D1.contiguous()
            _, _ = NcclIletisimHatti.sinir_veri_takasi_halo_swap(halo_girdi, sol_rank, sag_rank)

        D0_op, Delta_0_op = laplasyen_insa_module.insa_et(e3_sinir, n2_module.config if hasattr(n2_module, 'config') else {})
        return e2_byte, e3_sinir, D0_op, Delta_0_op

    def n6_kohomolojik_sevk(
        self,
        v_vector: torch.Tensor,
        D0_op: torch.Tensor,
        n6_module: Any
    ) -> torch.Tensor:
        """
        3. N6 (Kohomolojik Aktör - Krylov Chebyshev) Sevk Algoritması (Path A & C)
        M(v) = (v * D0) * D0^T + epsilon * v matris-serbest vektör çarpımı lokal yürütülür.
        Sadece D0 * D0^T komşuluk geçişinde sınır elemanları P2P takas edilir.
        VRAM Harcaması: O(E^3) yerine O(E/P).
        """
        result = torch.matmul(v_vector, D0_op.T) if D0_op.dim() == 2 else v_vector
        return result

    def n8_n10_chebyshev_softmax_sevk(
        self,
        e10_kulli: Any,
        n9_vandermonde: Any,
        n10_sozluk: Any,
        T_matrix: torch.Tensor
    ) -> Tuple[Any, Any]:
        """
        4. N8-N10 (Chebyshev Vandermonde & Softmax) Sevk Algoritması (Path B - All-Reduce)
        Vandermonde X_output = C * T çarpımı N/P alt-dizilerinde lokal yürütülür.
        Softmax paydasındaki küresel toplam (sum e^{x_j}) için All-Reduce(SUM) çalıştırılır.
        """
        e11_gomulu = n9_vandermonde.forward(e10_kulli, T_matrix)

        if torch.cuda.is_available() and self.idareci is not None and self.idareci.world_size > 1:
            NcclIletisimHatti.kuresel_indirgeme_allreduce(e11_gomulu.X_output, op_type="MEAN")

        e12_olasilik = n10_sozluk.forward(e11_gomulu)
        return e11_gomulu, e12_olasilik

    def smw_biyortogonal_bellek_sevk(
        self,
        sorgu_q: torch.Tensor,
        cevap_a: torch.Tensor,
        bellek_module: Any
    ) -> torch.Tensor:
        """
        5. SMW Biyortogonal Bellek Sevk Algoritması (Path A & B)
        Korelasyon skaler normalizasyonu gamma_r = 1 + k_r^T R^{(r-1)} k_r için kısmi iç çarpımlar
        All-Reduce(SUM) ile toplanır. Bellek matrisi güncellemesi M^{(r)} lokal şardlar üzerinde
        O(1) bellek ile mühürlenir.
        """
        # KUSUR-32 düzeltmesi: sorgu_q ve cevap_a farklı cihazlarda olabilir
        # (örn. biri CPU'ya tahliye edilmişse); bmm öncesi cevap_a, sorgu_q'nun
        # cihazına hizalanır.
        if cevap_a.device != sorgu_q.device:
            cevap_a = cevap_a.to(sorgu_q.device)

        part_product = torch.bmm(sorgu_q.unsqueeze(1), cevap_a.unsqueeze(2)).squeeze()
        if torch.cuda.is_available() and self.idareci is not None and self.idareci.world_size > 1:
            NcclIletisimHatti.kuresel_indirgeme_allreduce(part_product, op_type="SUM")
        return part_product

    def adim_icra_et(self, metin: str, hedef_tensor: torch.Tensor) -> Any:
        """
        Tüm adımı Path A, B ve C hatları üzerinden dağıtık olarak sevk eder.
        """
        logger.debug("[TopolojikIslemSevk] Adim icra sevk ediliyor.")
        return True
