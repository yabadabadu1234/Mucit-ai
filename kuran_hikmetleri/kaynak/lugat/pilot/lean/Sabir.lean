namespace Sabir

structure Durum where
  lam : Nat
  cek : Nat
  hudut : Nat

def Sabir (d : Durum) : Prop := d.cek ≤ d.hudut * d.lam

def Cez (d : Durum) : Prop := d.hudut * d.lam < d.cek

instance (d : Durum) : Decidable (Sabir d) := inferInstanceAs (Decidable (d.cek ≤ d.hudut * d.lam))

instance (d : Durum) : Decidable (Cez d) := inferInstanceAs (Decidable (d.hudut * d.lam < d.cek))

theorem sabir_veya_cez (d : Durum) : Sabir d ∨ Cez d :=
  (Nat.lt_or_ge (d.hudut * d.lam) d.cek).symm

theorem sabir_cez_dislar (d : Durum) : ¬ (Sabir d ∧ Cez d) :=
  fun ⟨h1, h2⟩ => absurd h1 (Nat.not_le.mpr h2)

theorem cez_sabrin_yoklugu (d : Durum) : Cez d ↔ ¬ Sabir d :=
  ⟨fun h1 h2 => sabir_cez_dislar d ⟨h2, h1⟩, fun h => Nat.not_le.mp h⟩

def destekle (d : Durum) (delta : Nat) : Durum := { d with lam := d.lam + delta }

theorem destek_sabri_korur (d : Durum) (delta : Nat) : Sabir d → Sabir (destekle d delta) :=
  fun h => Nat.le_trans h (Nat.mul_le_mul_left _ (Nat.le_add_right _ _))

def sikayet_p (d : Durum) (mu : Nat) : Durum := destekle d mu

def sikayet_baska (d : Durum) (mu : Nat) : Durum := { d with lam := d.lam - mu }

theorem sikayet_p_sabri_korur (d : Durum) (mu : Nat) : Sabir d → Sabir (sikayet_p d mu) :=
  destek_sabri_korur d mu

theorem sikayet_baska_geri (d : Durum) (mu : Nat) : Sabir (sikayet_baska d mu) → Sabir d :=
  fun h => Nat.le_trans h (Nat.mul_le_mul_left _ (Nat.sub_le _ _))

theorem sikayet_baska_sabri_bozabilir :
    ∃ (d : Durum) (mu : Nat), Sabir d ∧ Cez (sikayet_baska d mu) :=
  ⟨⟨1, 1, 1⟩, 1, by decide, by decide⟩

theorem cekim_artisi_bozabilir :
    ∃ (d : Durum) (delta : Nat), Sabir d ∧ Cez { d with cek := d.cek + delta } :=
  ⟨⟨1, 1, 1⟩, 1, by decide, by decide⟩

theorem cekim_artisi_garanti_degil :
    ¬ (∀ (d : Durum) (delta : Nat), Sabir d → Sabir { d with cek := d.cek + delta }) := by
  intro h
  have := h ⟨1, 1, 1⟩ 1 (by decide)
  exact absurd this (by decide)

theorem huzunle_sabir_mumkun (cek hudut : Nat) (h : 0 < hudut) : Sabir ⟨cek, cek, hudut⟩ :=
  Nat.le_mul_of_pos_left cek h

theorem cekimsiz_sabir_bos (d : Durum) (h : d.cek = 0) : Sabir d := by
  unfold Sabir; rw [h]; exact Nat.zero_le _

theorem kesilince_cez (d : Durum) (h : 0 < d.cek) : Cez { d with lam := 0 } := by
  unfold Cez; simpa using h

structure Sahne where
  tutan : String
  tutulan : String
  yer : String
  ceken : String
  tutma : Bool

def Sahne.yansimali (s : Sahne) : Prop := s.tutan = s.tutulan

def birlestir (s : Sahne) : Sahne := { s with tutulan := s.tutan }

def kes (s : Sahne) : Sahne := { s with tutma := false }

theorem birlestir_yansimali (s : Sahne) : (birlestir s).yansimali := rfl

theorem birlestir_idempotent (s : Sahne) : birlestir (birlestir s) = birlestir s := rfl

theorem kes_idempotent (s : Sahne) : kes (kes s) = kes s := rfl

theorem kes_birlestir_degisir (s : Sahne) : kes (birlestir s) = birlestir (kes s) := rfl

theorem kes_yansimaliyi_korur (s : Sahne) : s.yansimali → (kes s).yansimali := id

def sabir_sahnesi : Sahne := ⟨"nefs", "nefs", "maksat", "cez'", true⟩

def cez_sahnesi : Sahne := kes sabir_sahnesi

theorem cez_tutulan_ne_olursa_olsun (m : String) :
    kes (birlestir ⟨"nefs", m, "maksat", "cez'", true⟩) = cez_sahnesi := rfl

theorem sabir_sahnesi_yansimali : sabir_sahnesi.yansimali := rfl

end Sabir

#print axioms Sabir.sabir_veya_cez
#print axioms Sabir.sabir_cez_dislar
#print axioms Sabir.destek_sabri_korur
#print axioms Sabir.sikayet_baska_sabri_bozabilir
#print axioms Sabir.cekim_artisi_garanti_degil
#print axioms Sabir.cez_tutulan_ne_olursa_olsun
