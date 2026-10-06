import Main.LegalQuotient
import Xi.AdequacyResidual

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Xi.AdequacyResidual

namespace SixBirdsMetaMath.Xi.DataProcessing

/-!
Ξ companion paper §9 "Data processing and transfer".

This module mechanizes the data-processing identities available in
the finite rational matrix model.  Dissolving post-processing is fully
proved by matrix algebra; the bridge and native-coarsening statements
retain explicit paper-standing hypotheses for the missing Moore-
Penrose/range/isometry infrastructure.
-/

/-- `K_DD` is equivariant under dissolving post-processing. -/
private theorem blockCurrencyDD_post {e z z' : Nat}
    (C : Mat e e) (D : Mat z e) (F : Mat z' z) :
    blockCurrencyDD C (matMul F D) =
      matMul (matMul F (blockCurrencyDD C D)) (transpose F) := by
  unfold blockCurrencyDD
  calc
    matMul (matMul (matMul F D) (diagonalPseudoInverse C))
        (transpose (matMul F D))
        = matMul (matMul (matMul F D) (diagonalPseudoInverse C))
            (matMul (transpose D) (transpose F)) := by
            rw [transpose_matMul]
    _ = matMul (matMul F (matMul D (diagonalPseudoInverse C)))
            (matMul (transpose D) (transpose F)) := by
            rw [matMul_assoc F D (diagonalPseudoInverse C)]
    _ = matMul F
            (matMul (matMul D (diagonalPseudoInverse C))
              (matMul (transpose D) (transpose F))) := by
            rw [matMul_assoc F (matMul D (diagonalPseudoInverse C))
              (matMul (transpose D) (transpose F))]
    _ = matMul F
            (matMul (matMul (matMul D (diagonalPseudoInverse C)) (transpose D))
              (transpose F)) := by
            rw [← matMul_assoc (matMul D (diagonalPseudoInverse C))
              (transpose D) (transpose F)]
    _ = matMul (matMul F
            (matMul (matMul D (diagonalPseudoInverse C)) (transpose D)))
            (transpose F) := by
            rw [← matMul_assoc F
              (matMul (matMul D (diagonalPseudoInverse C)) (transpose D))
              (transpose F)]

/-- `K_DL` is left-multiplied by the dissolving post-processor. -/
private theorem blockCurrencyDL_post {e y z z' : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (F : Mat z' z) :
    blockCurrencyDL C L (matMul F D) =
      matMul F (blockCurrencyDL C L D) := by
  unfold blockCurrencyDL
  calc
    matMul (matMul (matMul F D) (diagonalPseudoInverse C)) (transpose L)
        = matMul (matMul F (matMul D (diagonalPseudoInverse C))) (transpose L) := by
            rw [matMul_assoc F D (diagonalPseudoInverse C)]
    _ = matMul F (matMul (matMul D (diagonalPseudoInverse C)) (transpose L)) := by
            rw [matMul_assoc F (matMul D (diagonalPseudoInverse C)) (transpose L)]

/-- `K_LD` is right-multiplied by the transpose post-processor. -/
private theorem blockCurrencyLD_post {e y z z' : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (F : Mat z' z) :
    blockCurrencyLD C L (matMul F D) =
      matMul (blockCurrencyLD C L D) (transpose F) := by
  unfold blockCurrencyLD
  calc
    matMul (matMul L (diagonalPseudoInverse C)) (transpose (matMul F D))
        = matMul (matMul L (diagonalPseudoInverse C))
            (matMul (transpose D) (transpose F)) := by
            rw [transpose_matMul]
    _ = matMul (matMul (matMul L (diagonalPseudoInverse C)) (transpose D))
            (transpose F) := by
            rw [← matMul_assoc (matMul L (diagonalPseudoInverse C))
              (transpose D) (transpose F)]

/-- The Schur term in `Ξ` is equivariant under dissolving post-processing. -/
private theorem schurTerm_post {e y z z' : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (F : Mat z' z)
    (KLLdagger : Mat y y) :
    matMul (matMul (blockCurrencyDL C L (matMul F D)) KLLdagger)
        (blockCurrencyLD C L (matMul F D)) =
      matMul
        (matMul F
          (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
            (blockCurrencyLD C L D)))
        (transpose F) := by
  rw [blockCurrencyDL_post, blockCurrencyLD_post]
  calc
    matMul (matMul (matMul F (blockCurrencyDL C L D)) KLLdagger)
        (matMul (blockCurrencyLD C L D) (transpose F))
        = matMul (matMul F (matMul (blockCurrencyDL C L D) KLLdagger))
            (matMul (blockCurrencyLD C L D) (transpose F)) := by
            rw [matMul_assoc F (blockCurrencyDL C L D) KLLdagger]
    _ = matMul F
          (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
            (matMul (blockCurrencyLD C L D) (transpose F))) := by
            rw [matMul_assoc F (matMul (blockCurrencyDL C L D) KLLdagger)
              (matMul (blockCurrencyLD C L D) (transpose F))]
    _ = matMul F
          (matMul
            (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
              (blockCurrencyLD C L D))
            (transpose F)) := by
            rw [← matMul_assoc (matMul (blockCurrencyDL C L D) KLLdagger)
              (blockCurrencyLD C L D) (transpose F)]
    _ = matMul
          (matMul F
            (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
              (blockCurrencyLD C L D)))
          (transpose F) := by
            rw [← matMul_assoc F
              (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
                (blockCurrencyLD C L D))
              (transpose F)]

/-- Dissolving post-processing: `Ξ_C(FD | L) = F Ξ_C(D | L) F^T`. -/
theorem dissolvingPostProcessing {e y z z' : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (F : Mat z' z) (KLLdagger : Mat y y) :
    adequacyResidual C L (matMul F D) KLLdagger =
      matMul (matMul F (adequacyResidual C L D KLLdagger)) (transpose F) := by
  calc
    adequacyResidual C L (matMul F D) KLLdagger
        = matSub (blockCurrencyDD C (matMul F D))
            (matMul (matMul (blockCurrencyDL C L (matMul F D)) KLLdagger)
              (blockCurrencyLD C L (matMul F D))) := rfl
    _ = matSub
          (matMul (matMul F (blockCurrencyDD C D)) (transpose F))
          (matMul
            (matMul F
              (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
                (blockCurrencyLD C L D)))
            (transpose F)) := by
            rw [blockCurrencyDD_post, schurTerm_post]
    _ = matMul
          (matMul F
            (matSub (blockCurrencyDD C D)
              (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
                (blockCurrencyLD C L D))))
          (transpose F) := by
            rw [← matSub_matMul_conjugate F
              (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
                (blockCurrencyLD C L D))
              (blockCurrencyDD C D)]
    _ = matMul (matMul F (adequacyResidual C L D KLLdagger)) (transpose F) := rfl

/-- `K_{D,AL} = K_{DL} A^T` for native post-composition. -/
private theorem blockCurrencyDL_compose_native {e y y' z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (A : Mat y' y) :
    blockCurrencyDL C (matMul A L) D =
      matMul (blockCurrencyDL C L D) (transpose A) := by
  unfold blockCurrencyDL
  calc
    matMul (matMul D (diagonalPseudoInverse C)) (transpose (matMul A L))
        = matMul (matMul D (diagonalPseudoInverse C))
            (matMul (transpose L) (transpose A)) := by
            rw [transpose_matMul]
    _ = matMul (matMul (matMul D (diagonalPseudoInverse C)) (transpose L))
            (transpose A) := by
            rw [← matMul_assoc (matMul D (diagonalPseudoInverse C))
              (transpose L) (transpose A)]

/-- `K_{AL,D} = A K_{LD}` for native post-composition. -/
private theorem blockCurrencyLD_compose_native {e y y' z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (A : Mat y' y) :
    blockCurrencyLD C (matMul A L) D =
      matMul A (blockCurrencyLD C L D) := by
  unfold blockCurrencyLD
  calc
    matMul (matMul (matMul A L) (diagonalPseudoInverse C)) (transpose D)
        = matMul (matMul A (matMul L (diagonalPseudoInverse C))) (transpose D) := by
            rw [matMul_assoc A L (diagonalPseudoInverse C)]
    _ = matMul A (matMul (matMul L (diagonalPseudoInverse C)) (transpose D)) := by
            rw [matMul_assoc A (matMul L (diagonalPseudoInverse C)) (transpose D)]

/-- `K_{AL,AL} = A K_{LL} A^T` for native post-composition. -/
private theorem blockCurrencyLL_compose_native {e y y' : Nat}
    (C : Mat e e) (L : Mat y e) (A : Mat y' y) :
    blockCurrencyLL C (matMul A L) =
      matMul (matMul A (blockCurrencyLL C L)) (transpose A) := by
  unfold blockCurrencyLL
  calc
    matMul (matMul (matMul A L) (diagonalPseudoInverse C))
        (transpose (matMul A L))
        = matMul (matMul (matMul A L) (diagonalPseudoInverse C))
            (matMul (transpose L) (transpose A)) := by
            rw [transpose_matMul]
    _ = matMul (matMul A (matMul L (diagonalPseudoInverse C)))
            (matMul (transpose L) (transpose A)) := by
            rw [matMul_assoc A L (diagonalPseudoInverse C)]
    _ = matMul A
            (matMul (matMul L (diagonalPseudoInverse C))
              (matMul (transpose L) (transpose A))) := by
            rw [matMul_assoc A (matMul L (diagonalPseudoInverse C))
              (matMul (transpose L) (transpose A))]
    _ = matMul A
            (matMul (matMul (matMul L (diagonalPseudoInverse C)) (transpose L))
              (transpose A)) := by
            rw [← matMul_assoc (matMul L (diagonalPseudoInverse C))
              (transpose L) (transpose A)]
    _ = matMul (matMul A
            (matMul (matMul L (diagonalPseudoInverse C)) (transpose L)))
            (transpose A) := by
            rw [← matMul_assoc A
              (matMul (matMul L (diagonalPseudoInverse C)) (transpose L))
              (transpose A)]

/-- Differences with the same left endpoint reduce to the difference of right endpoints. -/
private theorem matSub_matSub_same_left {m n : Nat} (X Y Z : Mat m n) :
    matSub (matSub X Y) (matSub X Z) = matSub Z Y := by
  funext i j
  unfold matSub
  grind [Rat.sub_eq_add_neg, Rat.add_assoc, Rat.add_comm, Rat.add_left_comm]

/-- A middle matrix subtraction may be pulled through two matrix products. -/
private theorem matMul_matMul_matSub {m n p q : Nat}
    (A : Mat m n) (B C : Mat n p) (D : Mat p q) :
    matMul (matMul A (matSub B C)) D =
      matSub (matMul (matMul A B) D) (matMul (matMul A C) D) := by
  calc
    matMul (matMul A (matSub B C)) D
        = matMul (matSub (matMul A B) (matMul A C)) D := by
            rw [matMul_sub_right]
    _ = matSub (matMul (matMul A B) D) (matMul (matMul A C) D) := by
            rw [matMul_sub_left]

/-- Schur correction for `AL` rewritten over the original `L` block coordinates. -/
private theorem nativeCoarsening_schur_coarse {e y y' z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (A : Mat y' y)
    (KaLALdagger : Mat y' y') :
    matMul (matMul (blockCurrencyDL C (matMul A L) D) KaLALdagger)
        (blockCurrencyLD C (matMul A L) D) =
      matMul
        (matMul (blockCurrencyDL C L D)
          (matMul (matMul (transpose A) KaLALdagger) A))
        (blockCurrencyLD C L D) := by
  rw [blockCurrencyDL_compose_native, blockCurrencyLD_compose_native]
  calc
    matMul (matMul (matMul (blockCurrencyDL C L D) (transpose A)) KaLALdagger)
        (matMul A (blockCurrencyLD C L D))
        = matMul
            (matMul (blockCurrencyDL C L D) (matMul (transpose A) KaLALdagger))
            (matMul A (blockCurrencyLD C L D)) := by
            rw [matMul_assoc (blockCurrencyDL C L D) (transpose A) KaLALdagger]
    _ = matMul (blockCurrencyDL C L D)
          (matMul (matMul (transpose A) KaLALdagger)
            (matMul A (blockCurrencyLD C L D))) := by
            rw [matMul_assoc (blockCurrencyDL C L D)
              (matMul (transpose A) KaLALdagger)
              (matMul A (blockCurrencyLD C L D))]
    _ = matMul (blockCurrencyDL C L D)
          (matMul (matMul (matMul (transpose A) KaLALdagger) A)
            (blockCurrencyLD C L D)) := by
            rw [← matMul_assoc (matMul (transpose A) KaLALdagger) A
              (blockCurrencyLD C L D)]
    _ = matMul
          (matMul (blockCurrencyDL C L D)
            (matMul (matMul (transpose A) KaLALdagger) A))
          (blockCurrencyLD C L D) := by
            rw [← matMul_assoc (blockCurrencyDL C L D)
              (matMul (matMul (transpose A) KaLALdagger) A)
              (blockCurrencyLD C L D)]

/--
Native coarsening: a smaller native explanation subspace leaves a
larger residual.  The only elevated analytic content is the
Moore-Penrose comparison matrix being positive semidefinite.
-/
theorem nativeCoarsening {e y y' z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (A : Mat y' y)
    (KLLdagger : Mat y y) (KaLALdagger : Mat y' y')
    (hKLDsym : transpose (blockCurrencyDL C L D) = blockCurrencyLD C L D)
    (hMPComparePSD :
      PositiveSemidefinite
        (matSub KLLdagger (matMul (matMul (transpose A) KaLALdagger) A))) :
    loewnerLE
      (adequacyResidual C L D KLLdagger)
      (adequacyResidual C (matMul A L) D KaLALdagger) := by
  rw [loewnerLE_iff_psd_sub]
  let KDL := blockCurrencyDL C L D
  let KLD := blockCurrencyLD C L D
  let mpGap := matSub KLLdagger (matMul (matMul (transpose A) KaLALdagger) A)
  have hDiff :
      matSub (adequacyResidual C (matMul A L) D KaLALdagger)
          (adequacyResidual C L D KLLdagger) =
        matMul (matMul KDL mpGap) KLD := by
    calc
      matSub (adequacyResidual C (matMul A L) D KaLALdagger)
          (adequacyResidual C L D KLLdagger)
          = matSub
              (matSub (blockCurrencyDD C D)
                (matMul (matMul (blockCurrencyDL C (matMul A L) D) KaLALdagger)
                  (blockCurrencyLD C (matMul A L) D)))
              (matSub (blockCurrencyDD C D)
                (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
                  (blockCurrencyLD C L D))) := rfl
      _ = matSub
              (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
                (blockCurrencyLD C L D))
              (matMul (matMul (blockCurrencyDL C (matMul A L) D) KaLALdagger)
                (blockCurrencyLD C (matMul A L) D)) := by
              rw [matSub_matSub_same_left]
      _ = matSub
              (matMul (matMul KDL KLLdagger) KLD)
              (matMul
                (matMul KDL (matMul (matMul (transpose A) KaLALdagger) A))
                KLD) := by
              rw [nativeCoarsening_schur_coarse]
      _ = matMul (matMul KDL mpGap) KLD := by
              unfold mpGap
              rw [matMul_matMul_matSub]
  have hConj : PositiveSemidefinite (matMul (matMul KDL mpGap) (transpose KDL)) := by
    unfold mpGap
    exact posSemidef_conjugate KDL
      (matSub KLLdagger (matMul (matMul (transpose A) KaLALdagger) A))
      hMPComparePSD
  rw [hDiff]
  change PositiveSemidefinite (matMul (matMul KDL mpGap) (blockCurrencyLD C L D))
  rw [← hKLDsym]
  change PositiveSemidefinite (matMul (matMul KDL mpGap) (transpose KDL))
  exact hConj

/--
Exact reducing bridge: if the bridge transports the block `K_DD` term
and the Schur correction term by `B`-conjugation, then the residual
itself transports by `B`-conjugation.
-/
theorem exactReducingBridge {e y z e' y' z' : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (Cp : Mat e' e') (Lp : Mat y' e') (Dp : Mat z' e')
    (U : Mat e e') (A : Mat y' y) (B : Mat z' z)
    (KLLdagger : Mat y y) (KLpLpdagger : Mat y' y')
    (hCbridge : Cp = matMul (matMul (transpose U) C) U)
    (hLbridge : Lp = matMul (matMul A L) U)
    (hDbridge : Dp = matMul (matMul B D) U)
    (hDDTransport :
      blockCurrencyDD Cp Dp =
        matMul (matMul B (blockCurrencyDD C D)) (transpose B))
    (hSchurTransport :
      matMul (matMul (blockCurrencyDL Cp Lp Dp) KLpLpdagger)
          (blockCurrencyLD Cp Lp Dp) =
        matMul
          (matMul B
            (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
              (blockCurrencyLD C L D)))
          (transpose B)) :
    adequacyResidual Cp Lp Dp KLpLpdagger =
      matMul (matMul B (adequacyResidual C L D KLLdagger)) (transpose B) := by
  have _ : Cp = matMul (matMul (transpose U) C) U := hCbridge
  have _ : Lp = matMul (matMul A L) U := hLbridge
  have _ : Dp = matMul (matMul B D) U := hDbridge
  calc
    adequacyResidual Cp Lp Dp KLpLpdagger
        = matSub (blockCurrencyDD Cp Dp)
            (matMul (matMul (blockCurrencyDL Cp Lp Dp) KLpLpdagger)
              (blockCurrencyLD Cp Lp Dp)) := rfl
    _ = matSub
          (matMul (matMul B (blockCurrencyDD C D)) (transpose B))
          (matMul
            (matMul B
              (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
                (blockCurrencyLD C L D)))
            (transpose B)) := by
            rw [hDDTransport, hSchurTransport]
    _ = matMul
          (matMul B
            (matSub (blockCurrencyDD C D)
              (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
                (blockCurrencyLD C L D))))
          (transpose B) := by
            rw [← matSub_matMul_conjugate B
              (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
                (blockCurrencyLD C L D))
              (blockCurrencyDD C D)]
    _ = matMul (matMul B (adequacyResidual C L D KLLdagger)) (transpose B) := rfl

/--
Defective dissolving bridge: a residual decomposition plus an AM-GM
Loewner bound for PSD summands yields the stated bridge bound.
-/
theorem defectiveBridge {e y z e' y' z' : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (Cp : Mat e' e') (Lp : Mat y' e') (Dp : Mat z' e')
    (R : Mat z' e') (U : Mat e e') (A : Mat y' y) (B : Mat z' z)
    (KLLdagger : Mat y y) (KLpLpdagger : Mat y' y')
    (t : Rat) (ht : 0 < t)
    (hNativeExact : Lp = matMul (matMul A L) U)
    (hDefectivePrime : Dp = matAdd (matMul B (matMul D U)) R)
    (hResidualDecomposition :
      adequacyResidual Cp Lp Dp KLpLpdagger =
        matAdd
          (matMul (matMul B (adequacyResidual C L D KLLdagger)) (transpose B))
          (adequacyResidual Cp Lp R KLpLpdagger))
    (hBxiBT_psd :
      PositiveSemidefinite
        (matMul (matMul B (adequacyResidual C L D KLLdagger)) (transpose B)))
    (hXi_R_psd :
      PositiveSemidefinite (adequacyResidual Cp Lp R KLpLpdagger)) :
    loewnerLE
      (adequacyResidual Cp Lp Dp KLpLpdagger)
      (matAdd
        (matScale (1 + t)
          (matMul (matMul B (adequacyResidual C L D KLLdagger)) (transpose B)))
        (matScale (1 + t⁻¹)
          (adequacyResidual Cp Lp R KLpLpdagger))) := by
  have _ : 0 < t := ht
  have _ : Lp = matMul (matMul A L) U := hNativeExact
  have _ : Dp = matAdd (matMul B (matMul D U)) R := hDefectivePrime
  rw [hResidualDecomposition]
  exact loewnerLE_scaled_add
    (matMul (matMul B (adequacyResidual C L D KLLdagger)) (transpose B))
    (adequacyResidual Cp Lp R KLpLpdagger)
    t ht hBxiBT_psd hXi_R_psd

end SixBirdsMetaMath.Xi.DataProcessing
