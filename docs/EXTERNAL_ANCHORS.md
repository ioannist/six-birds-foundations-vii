# External anchors — every citation to literature outside the Six Birds corpus

Rule: nothing enters `paper/references.bib` unverified. Each entry below records the metadata as
verified on 2026-09-02, how it was verified, and the passage in the paper it supports. The paper
recovers no external *theorem* as its own. External sources are cited for standard vocabulary and
definitions, technical comparison classes, methodological boundaries, and domain-specific analogies;
every comparison says what is not being identified or imported.

| Key | Citation (verified) | Verification | Supports | Label context |
|---|---|---|---|---|
| `Newman1942` | M. H. A. Newman, "On theories with a combinatorial definition of 'equivalence'", *Annals of Mathematics* (2) 43(2), 1942, pp. 223–243. DOI 10.2307/1968867. | Crossref record for the DOI (title, author, journal, vol. 43 no. 2, first page 223, year 1942); page range 223–243 confirmed by the *Journal of Symbolic Logic* review record (Cambridge Core). | Thm. confluence (VII-C018): the lemma that termination together with local confluence gives confluence. Cited for vocabulary only: VII's record formalises neither termination nor this lemma. | RECOVERED STANDARD (vocabulary) |
| `KnuthBendix1970` | D. E. Knuth and P. B. Bendix, "Simple word problems in universal algebras", in J. Leech (ed.), *Computational Problems in Abstract Algebra*, Pergamon Press, Oxford, 1970, pp. 263–297. DOI 10.1016/B978-0-08-012975-4.50028-X. | Crossref record for the DOI (authors, container title, pages 263–297, year 1970). | Thm. confluence (VII-C018): the critical-pair criterion for local confluence of a rewriting system. Cited for vocabulary only. | RECOVERED STANDARD (vocabulary) |
| `Huet1980` | G. Huet, "Confluent reductions: abstract properties and applications to term rewriting systems", *Journal of the ACM* 27(4), October 1980, pp. 797–821. DOI 10.1145/322217.322230. | Crossref record for the DOI (title, author, journal, vol. 27 no. 4, pp. 797–821, 1980-10-01); ACM DL page. | Thm. confluence (VII-C018): the critical-pair lemma for term rewriting. Cited for vocabulary only; VII's `CriticalPairCriterion` and `ConfluentAtDeclaredScope` are two predicates over a declared list of pairs, not this lemma. | RECOVERED STANDARD (vocabulary) |
| `MacLane1998` | S. Mac Lane, *Categories for the Working Mathematician*, 2nd ed., Graduate Texts in Mathematics 5, Springer, New York, 1998. ISBN 978-0-387-98403-2. DOI 10.1007/978-1-4757-4721-8. | Crossref record for the DOI (title, author, series); edition, year and ISBN from the publisher listing (hardcover 25 September 1998, edition number 2, 318 pp.). Crossref lists an "issued" year of 1978 for this DOI; the print edition cited is the 1998 second edition. | Deferral VII-C026: the definitions of product, pullback and pushout as universal constructions. | RECOVERED STANDARD (definitions only) |
| `LeanReferenceAxioms` | *The Lean Language Reference*, §"Axioms" (`propext`, `Quot.sound`, `Classical.choice`; `sorryAx` as the placeholder axiom). Lean FRO. https://lean-lang.org/doc/reference/latest/Axioms/ (accessed 2026-09-02). | Page fetched 2026-09-02; it lists the three axioms and states that `sorryAx` "is used as part of the implementation of the `sorry` tactic" and is "not intended to occur in finished proofs". | §2.3, §14.2, Appendix B: the statement that `propext` and `Quot.sound` are part of Lean's own foundational base and that the receipt reports no `sorryAx` and no `Classical.choice`. | supporting citation (verification axis) |

## External-literature expansion

A broad external search corpus was used for discovery, not as a bibliography. The 21 sources
below survived editorial shortlisting, Crossref and OpenAlex identifier checks, primary-text
inspection, and independent review of both the source and its exact in-context placement. Repeated citations in the introduction and at the local
definition or caveat are intentional: the first occurrence maps the surrounding literature; the
second makes the comparison boundary visible where it matters.

| Key | Citation (verified) | Independent verification | Exact use and boundary |
|---|---|---|---|
| `NelsonOppen1979` | G. Nelson and D. C. Oppen, “Simplification by Cooperating Decision Procedures,” *ACM TOPLAS* 1(2), 245–257 (1979). DOI 10.1145/357073.357079. | DOI/Crossref, ACM, DBLP, and independent primary-text review. | §§1 and 3: canonical comparison for cooperation of decision procedures over quantifier-free fragments under stated separation hypotheses; not a representation of the VII join. |
| `GoguenBurstall1992` | J. A. Goguen and R. M. Burstall, “Institutions: Abstract Model Theory for Specification and Programming,” *JACM* 39(1), 95–146 (1992). DOI 10.1145/147508.147524. | DOI/Crossref, ACM, DBLP, primary text, and independent review. | §§1, 3 and 12: signatures, sentences, models and satisfaction invariant under change of notation; comparison/reopen data only. |
| `SannellaTarlecki2012` | D. Sannella and A. Tarlecki, *Foundations of Algebraic Specification and Formal Software Development*, Springer (2012). DOI 10.1007/978-3-642-17336-3. | DOI/Crossref, Springer, Edinburgh Research Explorer, OpenAlex, and independent review. | §§1, 3 and 12: structured specifications and categorical specification constructions; not a completed primitive-operation algebra or categorical reduction. |
| `DeAlfaroHenzinger2001` | L. de Alfaro and T. A. Henzinger, “Interface Automata,” ESEC/FSE 2001, 109–120. DOI 10.1145/503209.503226. | DOI/Crossref, ACM, ISTA record, primary text, and independent review. | §§1 and 3: compatibility, optimistic composition and alternating refinement as a comparison of roles, not an identification of formalisms. |
| `BenvenisteEtAl2018` | A. Benveniste et al., “Contracts for System Design,” *Foundations and Trends in EDA* 12(2–3), 124–400 (2018). DOI 10.1561/1000000053. | DOI/Crossref, publisher text, HAL, OpenAlex, and independent review. | §§1 and 3: assumptions, guarantees, refinement and composition; contract operators are not the VII join. |
| `AbadiLamport1993` | M. Abadi and L. Lamport, “Composing Specifications,” *ACM TOPLAS* 15(1), 73–132 (1993). DOI 10.1145/151646.151649. | DOI/Crossref, ACM, Microsoft Research, author text, and independent review. | §1: compositional reasoning under environment assumptions with safety and liveness; external comparison only. |
| `BarrettHalvorson2016` | T. W. Barrett and H. Halvorson, “Morita Equivalence,” *Review of Symbolic Logic* 9(3), 556–582 (2016). DOI 10.1017/S1755020316000186. | DOI/Crossref, Cambridge, institutional record, PhilSci Archive, and independent review. | §§1 and 12: comparison among definitional, Morita and categorical equivalence; motivates data needed by the deferral, does not settle it. |
| `Weatherall2021` | J. O. Weatherall, “Why Not Categorical Equivalence?”, in J. Madarász and G. Székely (eds.), *Hajnal Andréka and István Németi on Unity of Science*, 427–451 (2021). DOI 10.1007/978-3-030-64187-0_18. | DOI/Crossref, Springer book record, arXiv author manuscript, OpenAlex, and independent review; the discovery-corpus container title was corrected. | §§1 and 12: interpretive limits of categorical equivalence; no conclusion about the VII join's reducibility. |
| `AlpernSchneider1985` | B. Alpern and F. B. Schneider, “Defining Liveness,” *Information Processing Letters* 21(4), 181–185 (1985). DOI 10.1016/0020-0190(85)90056-0. | DOI/Crossref, ScienceDirect, primary text, OpenAlex, and independent review. | §§1 and 7: safety/liveness only; reachability and bounded-search claims are assigned to the model-checking sources. |
| `ClarkeEtAl2018` | E. M. Clarke, T. A. Henzinger, H. Veith and R. Bloem (eds.), *Handbook of Model Checking*, Springer (2018). DOI 10.1007/978-3-319-10575-8. | DOI/Crossref, Springer, institutional copy, OpenAlex, and independent review. | §§1 and 7: broad transition-system, reachability and model-checking comparison; does not define VII's five operational statuses. |
| `BiereEtAl1999` | A. Biere, A. Cimatti, E. M. Clarke and Y. Zhu, “Symbolic Model Checking without BDDs,” TACAS 1999, LNCS 1579, 193–207. DOI 10.1007/3-540-49059-0_14. | DOI/Crossref, Springer, CMU record, primary text, OpenAlex, and independent review. | §§1 and 7: canonical bounded LTL model-checking reference; reinforces rather than removes the paper's carrier/horizon qualification. |
| `NosekEtAl2018` | B. A. Nosek, C. R. Ebersole, A. C. DeHaven and D. T. Mellor, “The Preregistration Revolution,” *PNAS* 115(11), 2600–2606 (2018). DOI 10.1073/pnas.1708274114. | DOI/Crossref, PNAS, PubMed, OpenAlex, primary text, and independent review. | §5: methodological reason to distinguish a plan fixed before outcomes from a post-hoc reconstruction; not a source for VII's formal record. |
| `GreenEtAl2007` | T. J. Green, G. Karvounarakis and V. Tannen, “Provenance Semirings,” PODS 2007, 31–40. DOI 10.1145/1265530.1265535. | DOI/Crossref, ACM, UPenn primary text, OpenAlex, and independent review. | §§1 and 6: derivational lineage of relational-query outputs; not statistical or causal independence and not VII's ancestry witness. |
| `Pearl2009` | J. Pearl, *Causality: Models, Reasoning, and Inference*, 2nd ed., Cambridge University Press (2009). DOI 10.1017/CBO9780511803161. | DOI/Crossref, Cambridge, author page, OpenAlex, and independent review. | §§1 and 6: common-cause structure and distinction between causal and statistical relations; no substitution of d-separation for VII source independence. |
| `MontevilMossio2015` | M. Montévil and M. Mossio, “Biological Organisation as Closure of Constraints,” *Journal of Theoretical Biology* 372, 179–191 (2015). DOI 10.1016/j.jtbi.2015.02.029. | DOI/Crossref, PubMed, author primary text, OpenAlex, and independent review. | §§1 and 7: comparison with constraints acting on processes while mutually maintained; VII is not claimed to formalize biological closure. |
| `Landauer1961` | R. Landauer, “Irreversibility and Heat Generation in the Computing Process,” *IBM Journal of Research and Development* 5(3), 183–191 (1961). DOI 10.1147/rd.53.0183. | DOI/Crossref, IBM, primary text, OpenAlex, and independent review. | §6: boundary marker—physical information-processing costs require an application bridge and do not prove the abstract ledger law. |
| `Bennett1982` | C. H. Bennett, “The Thermodynamics of Computation—A Review,” *International Journal of Theoretical Physics* 21(12), 905–940 (1982). DOI 10.1007/BF02084158. | DOI/Crossref, Springer, open primary text, OpenAlex, and independent review. | §6: review companion to Landauer and the same physical-instantiation boundary; no VII theorem dependence. |
| `Berry1984` | M. V. Berry, “Quantal Phase Factors Accompanying Adiabatic Changes,” *Proceedings of the Royal Society A* 392(1802), 45–57 (1984). DOI 10.1098/rspa.1984.0023. | DOI/Crossref, Royal Society, author primary text, OpenAlex, and independent review. | §§1 and 8: canonical cyclic adiabatic geometric-phase comparison; the text expressly refuses to infer a bundle, connection, curvature, or adiabatic dynamics for VII. |
| `Crooks1999` | G. E. Crooks, “Entropy Production Fluctuation Theorem and the Nonequilibrium Work Relation for Free Energy Differences,” *Physical Review E* 60(3), 2721–2726 (1999). DOI 10.1103/PhysRevE.60.2721. | DOI/Crossref, APS, arXiv author manuscript, OpenAlex, and independent review. | §§1 and 8: forward/reverse path-probability relation under stochastic microscopically reversible dynamics; physical comparison, not interpretation of an abstract profile. |
| `DeMouraUllrich2021` | L. de Moura and S. Ullrich, “The Lean 4 Theorem Prover and Programming Language,” CADE 28, LNCS 12699, 625–635 (2021). DOI 10.1007/978-3-030-79876-5_37. | DOI/Crossref, Springer, Lean project text, OpenAlex, and independent review. | §§1 and 14: Lean architecture, extensibility and relatively small trusted kernel; the repository macro, not this source, supplies the pinned version. |
| `Pollack1998` | R. Pollack, “How to Believe a Machine-Checked Proof,” in G. Sambin and J. M. Smith (eds.), *Twenty Five Years of Constructive Type Theory*, 205–220, OUP (1998). DOI 10.1093/oso/9780198501275.003.0013. | DOI/Crossref, OUP, BRICS report version, OpenAlex, and independent review. | §§1 and 14: trust boundary around machine-checked proof; derivability does not establish specification adequacy. |

### Refused candidates

- Wolpert--Macready optimization “No Free Lunch” theorems: shared wording, unrelated
  quantifiers and object of study.
- Recent Zenodo “structural holonomy” and variational-inference preprints: noncanonical and no
  exact bridge; Berry is retained solely with an explicit domain boundary.
- Generic non-monotonic logic and generic model-diagnosis papers: no support for the paper's
  refuted contact-degree claim or its bespoke residual ledger.
- Vector/cryptographic commitment literature: VII's commitment is methodological
  preregistration, not a hiding/binding primitive.
- A rejected Pamela Zave feature-interaction candidate: its supplied DOI
  `10.1109/IWSSD.1993.315508` resolves to J. C. Corbett's unrelated verification paper.
- The remaining autopoiesis and closure suggestions: one canonical comparison is enough before
  a biological instantiation exists.

Corpus citations added in this audit (all vendored under `source/papers/`, so no "canonical
source not in repo" flag is needed): `TsiokosFlatten` (To Flatten a Stone, P048),
`TsiokosNotch` (To Notch a Stone, P051), `TsiokosClassify` (To Classify a Stone, P045),
`TsiokosNeedleKiller` (Emergence IS the Needle Killer, P009), `TsiokosStrictTest`
(Strict-Test-to-Event Package Admissibility, P037). Their theorem numbers quoted in the paper
were recovered from scratch compiles of the vendored TeX (`PRESHIP_AUDIT.md` §0.1).

The original five-anchor audit removed nothing because the manuscript then contained no external
citation. The later expansion refused the candidates listed above and retained only sources with a
specific comparison, methodological, physical-boundary, or trust-boundary role. None is used as a
premise of a VII theorem.
