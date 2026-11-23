# Combinator Research Preprints

This repository contains preprints and mechanized proofs related to N. E. Davis' research on combinators, particularly the combinator $S = \lambda x.\lambda y.\lambda z. x z (y z)$ or Smullyan's Starling.  All theorems are mechanized in [`sigilante/lean-ski`](https://github.com/sigilante/lean-ski).

This work was carried out in a centaur fashion, with high-level human direction but the bulk of the mechanization and formalization done by the LLM agent.

## Papers

* [Head Normal Forms of the Combinator $S$](s1-head-normal-forms/main.pdf)
  **It settles Question 10 of "Dance of the Starlings" by proving that their 35-state tree automaton accepts exactly the $S$-terms with a head normal form, so whether such a term ever reaches head form can be decided mechanically.**

  > A closed term built from $S$ alone has a head normal form when it reduces to $S$, $S\,X$ or $S\,X\,Y$. Barendregt, Endrullis, Klop and Waldmann asked whether a 35-state tree automaton they gave accepts exactly these terms ("Dance of the Starlings", Question 10). We prove that it does. The automaton is a homomorphic image of a 38-element model of the $S$-law, so its state is a reduction invariant, and rejection implies the absence of a head normal form. For the converse we read a weight along the spine of a term; a finite certificate of small integers makes the weight, with two tie-breakers, decrease at every head step. The whole proof is mechanized in Lean~4 with no axioms beyond propositional extensionality and quotient soundness, and the finite facts are checked by kernel evaluation.
* [Productive Terms of the Combinator $S$](s2-productive-terms/main.pdf)
  **It answers Question 5 of "Dance of the Starlings": a 39-state tree automaton accepts exactly the productive $S$-terms, those whose Böhm tree has no $\bot$, so this set is regular and productivity is decidable, where before only normalization was known to be decidable.**

  > A closed term built from $S$ alone is productive when its Böhm tree has no $\bot$. Barendregt, Endrullis, Klop and Waldmann asked how to characterize these terms, whether they form a regular set, and whether productivity is decidable ("Dance of the Starlings", Question 5). We give a 39-state bottom-up tree automaton that accepts exactly the productive closed $S$-terms, so the set is regular and productivity is decidable. The automaton is a model of the $S$-law, so its state is a reduction invariant, and acceptance implies productivity by the head-normal-form theorem of a companion paper. The converse reduces to 2,757 pairs of states, which a certificate of 7,244 claims about symbolic head reduction settles. The proof, including the soundness of the certificate checker and its run on the certificate, is mechanized in Lean~4 with no axioms beyond propositional extensionality and quotient soundness, for productivity stated as "the Böhm tree is defined to every depth"; its equivalence with the Böhm-tree statement is a short argument on paper.
* [Infinitary Normal Forms of the Combinator $S$](s3-infinitary-normal-forms/main.pdf)
  **It gives a machine-checked proof of Waldmann's theorem that no reduction of an $S$-term rewrites the root infinitely often, and shows that a term is productive exactly when no node of its infinitary normal form has an infinite left spine, linking the infinite behaviour of $S$-terms to the finite automaton of the previous paper.**

  > Waldmann proved that no reduction of a closed term built from $S$ alone rewrites the root infinitely often. We mechanize his proof in Lean 4, with the case analysis restated over a 38-element model of the $S$-law, so that every side condition becomes a finite table fact. Hereditarily, every infinite reduction from a finite $S$-term converges (mechanized), and each term $t$ has a unique infinitary normal form $t^\infty$, its Berarducci tree (uniqueness is cited; Lean has $t^\infty$ through its finite prefixes). With the head-normal-form automaton of a companion paper, every finite prefix of $t^\infty$ is computable. And $t$ is productive---its Böhm tree has no $\bot$---exactly when no node of $t^\infty$ has an infinite left spine; so a 39-state automaton decides which infinitary normal forms have a node with an infinite left spine.
* [Join Bounds and the Word Problem for the Combinator $S$](s4-word-problem/main.pdf)
  **It shows that Barendregt's 1975 word problem for $S$ (RTA open problem #97) would be solved by a computable bound on the size of common reducts, and it rules out the simplest such bound, an additive one.**

  > Whether convertibility of closed terms built from $S$ alone is decidable has been open since Barendregt asked in 1975. We show that it is decidable if convertible terms always have a common reduct whose size is bounded by a computable function of their sizes. We also show that no bound has the form $\max(|t|,|u|)+c$, by a family of convertible pairs whose common reducts all exceed the larger term by a linear amount. Both results are mechanized in Lean 4.
* [A 373-Element Model Computes the Depth-Two Prefix of an $S$-Term](s5-depth-two-prefixes/main.pdf)
  **It shows that a finite algebra can read two levels of an $S$-term's infinitary normal form, not just whether it has a head normal form, so the terms with a given depth-two prefix form a regular set; it is the first step beyond head normal forms toward finite descriptions of the infinite behaviour of $S$-terms.**

  > Every closed term $t$ built from the combinator $S$ has an infinitary normal form $t^\infty$, whose finite prefixes are computable. We show that the prefix of depth two is computed by a 373-element model of the $S$-law: the fold of $t$ into the model determines it. The 38-element model that decides head normal forms is a homomorphic image of this one. The proof reduces the claim to finitely many conditions on the model's table, and it is mechanized in Lean 4 for the prefix rules of the companion paper on infinitary normal forms.
* [No Ground Loops for the Combinator $S$, Constructively](s7-no-ground-loops/main.pdf)
  **It gives a constructive, machine-checked proof of Waldmann's theorem that no $S$-term reduces to a term containing itself, so no $S$-term can head-reduce back to itself with extra arguments, emitting them forever.**

  > Waldmann proved that no closed term built from the combinator $S$ reduces, in one or more steps, to a term that contains it. We give a constructive proof and mechanize it in Lean 4. We prove termination of a variant of Waldmann's labelled reduction by direct induction on accessibility instead of a recursive path order. The theorem follows by replaying a loop inside its own result. As a consequence, no closed $S$-term head-reduces to itself applied to arguments.

## Ancillary papers

* [The $SKI$ Self-Interpreter, Mechanized](self-interpreter-mechanized/main.pdf)
  **It machine-checks a published self-interpreter for $SKI$ against the terms as printed, so the 618-atom interpreter and 43-atom unquoter are certified to do what their paper claims, and it adds a converse of fuel adequacy, which shows that the interpreter's answer does not depend on its budget.**

  > A recent paper gives a self-interpreter for the $SKI$ combinator calculus: a 618-atom closed term `whnfF` that runs a Scott-encoded term to weak head normal form under a fuel budget, with a 43-atom unquoter `UQ`, and proves that the interpreter is adequate. We prove in Lean 4 that the definitions bracket-abstract to the printed terms, that these satisfy step and fuel adequacy as stated, and that `UQ` inverts the encoding. We also prove a converse of fuel adequacy and the independence of the answer from the budget, from which the paper's three listed consequences follow.

## Related papers

Other papers by N. E. Davis on combinatory logic, outside this series; their mechanizations are also in [`sigilante/lean-ski`](https://github.com/sigilante/lean-ski).

* N. E. Davis, *A Self-Interpreter for $SKI$: Authoring Semantics for New Symbols*. In review at the *Journal of Functional Programming*. Preprint: [doi:10.5281/zenodo.22867957](https://doi.org/10.5281/zenodo.22867957). Mechanized above in *The $SKI$ Self-Interpreter, Mechanized*.
* N. E. Davis, *SKIjack: A Low-Level Native Language for the $SKI$ Calculus*. In review at *The Art, Science, and Engineering of Programming*. Compiler: [`sigilante/SKIjack`](https://github.com/sigilante/SKIjack).
* N. E. Davis, *The Staging Line, Calibrated: Uniform Continuity of Oracle Functionals Is the Decidable Fan Theorem*. In preparation.
