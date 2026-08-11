

import os
import sys
import logging
import math
from typing import Dict, List, Tuple, Any, Optional
import torch

logger = logging.getLogger("mucit_ai.topolojik_islem_sevk")


class TopolojikIslemSevk:
    def __init__(self, idareci: Optional[Any] = None, model: Optional[Any] = None):
        self.idareci = idareci
        self.model = model
        logger.info("[TopolojikIslemSevk] Sevk koprusu ilklendi.")

    def n1_byte_sevk(self, e1_girdi: Any, n1_module: Any) -> Tuple[Any, torch.Tensor]:
        e2_byte, x_initial = n1_module.forward(e1_girdi)
        return e2_byte, x_initial

    def n2_n11_laplasyen_sevk(
        self,
        e2_byte: Any,
        x_initial: torch.Tensor,
        n2_module: Any,
        laplasyen_insa_module: Any
    ) -> Tuple[Any, Any, torch.Tensor, torch.Tensor]:
        e3_sinir = n2_module.forward(e2_byte, x_initial=x_initial, mode='train')

        D0_op, Delta_0_op = laplasyen_insa_module.insa_et(e3_sinir, n2_module.config if hasattr(n2_module, 'config') else {})
        return e2_byte, e3_sinir, D0_op, Delta_0_op

    def n6_kohomolojik_sevk(
        self,
        v_vector: torch.Tensor,
        D0_op: torch.Tensor,
        n6_module: Any
    ) -> torch.Tensor:
        result = torch.matmul(v_vector, D0_op.T) if D0_op.dim() == 2 else v_vector
        return result

    def n8_n10_chebyshev_softmax_sevk(
        self,
        e10_kulli: Any,
        n9_vandermonde: Any,
        n10_sozluk: Any,
        T_matrix: torch.Tensor
    ) -> Tuple[Any, Any]:
        e11_gomulu = n9_vandermonde.forward(e10_kulli, T_matrix)

        e12_olasilik = n10_sozluk.forward(e11_gomulu)
        return e11_gomulu, e12_olasilik

    def smw_biyortogonal_bellek_sevk(
        self,
        sorgu_q: torch.Tensor,
        cevap_a: torch.Tensor,
        bellek_module: Any
    ) -> torch.Tensor:
        
        
        if cevap_a.device != sorgu_q.device:
            cevap_a = cevap_a.to(sorgu_q.device)

        part_product = torch.bmm(sorgu_q.unsqueeze(1), cevap_a.unsqueeze(2)).squeeze()
        return part_product

    def adim_icra_et(self, metin: str, hedef_tensor: torch.Tensor) -> Any:
        logger.debug("[TopolojikIslemSevk] Adim icra sevk ediliyor.")
        return True
