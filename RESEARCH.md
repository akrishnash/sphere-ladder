# Research plan: Seeing S³

> **Working title:** *Seeing S³: a dimensional-ladder visualization of the Hopf fibration for quantum states and rigid-body attitude*

This file collects the research directions for Sphere Ladder. Each item is tracked as a GitHub issue
(see the [issue list](https://github.com/akrishnash/sphere-ladder/issues)), grouped into milestones M1–M5.

---

## 1. Why this can be research, not just a visualization

Beautiful Hopf-fibration visualizations already exist (Niles Johnson's animations, the film
*Dimensions*). "Another pretty picture" is not a contribution. What is new here:

1. **The ladder itself as a teaching device.** S¹ → S² → T² → S³ → S⁴ with one consistent trick
   (stereographic shadow from the north pole) and one consistent flow. The hypothesis is that
   climbing the analogy makes S³ easier to reason about than jumping straight to it.
2. **Verified correctness.** Every claim on the pages is checked numerically by the NumPy companion
   (`python -m sphere_ladder verify`, currently 26 checks). Few visualization systems ship a proof
   harness for what they show.
3. **Two real domains live on S³.**
   - **Qubits.** A normalised qubit state (α, β), |α|² + |β|² = 1, *is* a point of S³. The Hopf map
     *is* the map to the Bloch sphere, and each Hopf fiber *is* the global phase. Two-qubit states
     live on S⁷, which fibres over S⁴ (quaternionic Hopf fibration); Mosseri & Dandoloff relate this
     to entanglement.
   - **Spacecraft attitude.** Unit quaternions are S³ (a double cover of SO(3)). SLERP interpolation
     runs along great circles of S³, and the Hopf split corresponds to the swing–twist
     (tilt/twist) decomposition used in attitude control: *where the body axis points* (a point of S²)
     plus *roll about that axis* (position along the fiber).

## 2. Research questions

- **RQ1 (learning).** Does climbing the ladder (S¹, S² first) improve people's ability to answer
  questions about S³ (linking, fibers, what the projection distorts) compared with seeing S³ alone?
- **RQ2 (domain insight, quantum).** Does showing a qubit state on S³ *together with* the Bloch
  sphere help learners understand global phase, and why it is physically unobservable but
  mathematically real?
- **RQ3 (domain insight, attitude).** Can an S³ view of real attitude trajectories help engineers spot
  things that Euler-angle plots hide: unwinding, sign flips q ↔ −q, and the swing–twist structure of
  a manoeuvre?
- **RQ4 (visualization technique).** Which views best convey linking and fiber structure: stereographic
  shadow, slicing, or linked S² brushing (click a point, see its fiber)?

## 3. Planned contributions

1. **System:** the ladder, extended with qubit and attitude modes that load real data.
2. **Verification:** the numerical checker, extended to every new claim (qubit and attitude).
3. **Evaluation:** a controlled user study for RQ1/RQ2 and expert case studies for RQ3.
4. **Open source:** the whole thing is a static page plus a small Python package, MIT licensed.

---

## 4. Milestones

### M1: Visual foundation
- [x] WebGL renderer for S³: lit tubes, bloom, glowing particles, fallback to 2D if WebGL fails
- [x] S² picker: click a point, its fiber appears; drag a path, a family of fibers sweeps out
- [ ] Hopf tori as surfaces: draw a closed curve on S², render the torus it lifts to (not just sampled rings)
- [ ] Dense fibration mode: thousands of fibers with instanced rendering
- [ ] Morph transitions between ladder levels (S² view continuously becoming the S³ view)
- [ ] Guided tour: a narrated, scroll-driven walkthrough for first-time visitors
- [ ] Typeset maths (KaTeX) and high-resolution image / video export for talks and figures

### M2: Quantum mode
- [ ] Qubit state as a point of S³ with its Bloch-sphere image side by side
- [ ] Gates (X, Y, Z, H, S, T, arbitrary U) as S³ motions; global phase shown moving along the fiber
- [ ] Circuits: play a gate sequence and watch the trajectory on S³ and S²
- [ ] Two-qubit mode: the S⁷ → S⁴ quaternionic Hopf fibration, and where entangled states sit
- [ ] Verifier: check the qubit ↔ S³ ↔ Bloch correspondences numerically

### M3: Attitude mode
- [ ] Load a quaternion attitude log (CSV: t, q0, q1, q2, q3) and draw it on S³
- [ ] Show the swing–twist split live: the pointing direction on S², the twist along the fiber
- [ ] SLERP vs. other interpolations as great-circle vs. other paths on S³
- [ ] Double cover: show q and −q, detect sign flips and unwinding in real data
- [ ] Case study data: a public or simulated spacecraft manoeuvre
- [ ] Verifier: check the swing–twist ↔ Hopf correspondence numerically

### M4: Evaluation
- [ ] RQ1 study design: between-subjects, "ladder first" vs. "S³ only"; pre/post questions on
      linking, fibers and projection distortion; timing and accuracy
- [ ] RQ2 study with students who have taken an intro quantum course
- [ ] RQ3 expert interviews / think-aloud sessions with attitude and GNC engineers
- [ ] Ethics / consent paperwork as required by the host institution

### M5: Write-up
- [ ] Related-work survey (see §6)
- [ ] Paper draft; pick the venue from §5 and check its current call for papers
- [ ] Artifact: tag a release, archive it (e.g. Zenodo DOI), link the live demo

---

## 5. Candidate venues (check each year's call for papers)

| Venue | Fit |
|---|---|
| IEEE VIS (short papers, or the education track) | System + evaluation (RQ1, RQ4) |
| EuroVis (short papers) | Same, European venue |
| Bridges (Mathematics, Art, Music, Architecture, Culture) | The visual and mathematical side; also has an art exhibition |
| Journal of Mathematics and the Arts | Longer mathematical-visualization article |
| Physical Review Physics Education Research | Quantum-mode study (RQ2) |
| AIAA / aerospace GNC venues | Attitude case study (RQ3) |

## 6. Related work to read first

- H. Hopf, "Über die Abbildungen der dreidimensionalen Sphäre auf die Kugelfläche", *Mathematische Annalen* 104 (1931).
- D. W. Lyons, "An Elementary Introduction to the Hopf Fibration", *Mathematics Magazine* 76(2) (2003).
- R. Mosseri and R. Dandoloff, "Geometry of entangled states, Bloch spheres and Hopf fibrations", *J. Phys. A* 34 (2001).
- H. K. Urbantke, "The Hopf fibration: seven times in physics", *J. Geometry and Physics* 46 (2003).
- A. J. Hanson, *Visualizing Quaternions*, Morgan Kaufmann (2006).
- K. Shoemake, "Animating rotation with quaternion curves", SIGGRAPH (1985).
- J. Leys, É. Ghys and A. Alvarez, *Dimensions* (film, 2008), dimensions-math.org.
- N. Johnson, Hopf fibration video and notes, nilesjohnson.net.
- Literature on the swing–twist decomposition in robotics and character animation.

*(Verify every reference against the original before citing it in a paper.)*

## 7. Risks and how to handle them

| Risk | Mitigation |
|---|---|
| "Not novel": Hopf visualizations exist | Lead with the ladder pedagogy, the verification harness and the two domain modes, not with the rendering |
| User study too small to show an effect | Pre-register hypotheses; use within-task accuracy and time; fall back to a qualitative study |
| Attitude data is sensitive | Use public or simulated manoeuvres; keep the loader local-only (nothing uploaded) |
| Maths errors in new modes | Every new claim gets a check in `verify.py` before it goes on a page |

## 8. Current status

- Live: https://akrishnash.github.io/sphere-ladder/
- Done: five-level ladder (S¹, S², torus, S³, S⁴), light/dark themes, WebGL S³ view with S² picker,
  NumPy geometry + 26-check verifier + matplotlib figures.
- Next: M1 remaining items, then M2 (quantum mode).
