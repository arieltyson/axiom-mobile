# Speaker Notes -- AXIOM-Mobile Presentation (Slide Deck v2)

Target duration: ~15 minutes (roughly 45-50 seconds per slide).

---

## Slide 1: Title (30 seconds)

**Say**: "We're presenting AXIOM-Mobile, a research project investigating the minimal amount of training data needed to deploy effective domain reasoning on mobile devices. This is joint work by Annie Boltwood, Mahim Chaudhary, and Ariel Tyson for CMPT 416 at SFU."

**Emphasis**: The word "minimal" -- this is an efficiency question, not just an accuracy question.

---

## Slide 2: Problem / Motivation (1 minute)

**Say**: "Most users interact with computing primarily through their phones. When we want a model to reason about what's on screen -- answering questions about a UI screenshot, for example -- we need training data. But mobile deployment imposes hard constraints on latency, energy, memory, and model size. So there's a fundamental tension: quality usually demands more data and bigger models, but deployment demands the opposite."

**Transition**: "This tension leads directly to our research question."

---

## Slide 3: Research Question (1 minute)

**Say**: "We ask: what is k-star -- the minimum number of training examples needed for the model to be effective? And we define effective strictly: the model must simultaneously meet all six thresholds. It's not enough to be fast if accuracy is low, and it's not enough to be accurate if latency is unacceptable."

**Emphasis**: The joint definition of effectiveness. All six thresholds must be met simultaneously.

**Do not claim**: That we have answered this question. We have built the infrastructure to answer it.

---

## Slide 4: System Architecture (1 minute)

**Say**: "The system has two components. The iOS app is a SwiftUI testbed that loads Core ML models and runs inference with real-time latency measurement. The Python pipeline handles everything upstream: curating data, training models, running active-learning selection strategies, exporting to Core ML, and statistical analysis. The two connect through the exported model artifact."

**Emphasis**: End-to-end reproducibility -- every step is scripted.

---

## Slide 5: Dataset (45 seconds)

**Say**: "Dataset v2 contains 452 screenshot-question-answer triples collected from 152 real iOS screenshots, covering 128 answer classes -- a significant expansion from the original 52-example, 24-class dataset v1. We use a frozen split: 382 examples for training, with held-out validation and test sets. The screenshots are private and stored off-repo. We currently have a single annotator; dual-annotator agreement is planned but not yet completed."

**Do not claim**: That the dataset is large enough. 452 examples across 128 classes is still only ~3.5 per class on average.

---

## Slide 6: Models (45 seconds)

**Say**: "We have two model generations. The v0 baseline is a 40-thousand-parameter CNN-plus-embedding model trained on 37 examples across 24 classes, achieving about 10% test EM. The current default, tiny_multimodal_v1, is a 47-thousand-parameter model trained on 382 examples across 128 classes using dataset v2, achieving 27.5% test EM -- a 2.75x improvement over v0. The app uses model metadata sidecars to set per-model confidence thresholds (0.45 for v1). Both models exist to validate and iterate on the pipeline."

**Emphasis**: v1 achieves 27.5% test EM on 128 classes -- 2.75x improvement over v0 -- but still far from the 70% target.

**Do not claim**: That 27.5% EM is a strong accuracy result. It is progress, not success.

---

## Slide 7: Selection Strategies (45 seconds)

**Say**: "We implemented three active-learning selection strategies: random sampling, uncertainty-based selection using prediction entropy, and diversity-based selection using k-center greedy. A fourth strategy, guided by a knowledge graph, is blocked pending KG infrastructure. We ran a full sweep: three strategies, six budget levels, three random seeds -- 54 runs total. Note: these selection sweeps were conducted under the v0/dataset-v1 regime with 52 examples. Re-running them with dataset v2 is a planned next step."

**Transition**: "Let's look at what those 54 runs produced."

---

## Slide 8: Learning Curves (1 minute)

**Say**: "Here are the learning curves from the v0/dataset-v1 regime. The key finding is negative: all strategies converge to the same 10% exact match at full pool size, and the power-law fits have very low R-squared values. The uncertainty strategy is degenerate -- it produces all-zero predictions at every budget except the maximum. With only 52 examples, there was not enough signal to differentiate strategies. These curves have not yet been re-run with dataset v2's 452 examples -- that is a planned next step."

**Emphasis**: These learning curves are still from v0/dataset-v1. Re-running with dataset v2 is needed to see whether the larger dataset provides enough signal.

**Do not claim**: That any strategy is better than another at the v0 scale, or that v1's 27.5% EM invalidates these curves (they were run under different conditions).

---

## Slide 9: On-Device Latency Results (1 minute)

**Say**: "For latency, we measured on a physical iPhone 15 Pro Max with an A17 Pro chip. The v0 model (24 classes) had p50=14.0ms. The v1 model (128 classes, 47K params) has p50=14.5ms -- essentially identical, confirming that scaling from 24 to 128 classes has negligible latency cost. Both pass all latency thresholds with a 28-times margin."

**Emphasis**: v1 physical-device latency (14.5ms) is essentially identical to v0 (14.0ms), confirming that scaling from 24 to 128 classes has negligible latency cost. Physical device measurement, not simulator.

---

## Slide 10: Simulator vs Physical Device (45 seconds)

**Say**: "This table makes the simulator-versus-device gap concrete. The simulator in debug mode is roughly 14 times slower than the physical device. Even in release mode, the simulator is 7 times slower. This is why we report simulator numbers only as pipeline validation, never for threshold evaluation."

**Transition**: "Now let's see where we stand overall."

---

## Slide 11: Effectiveness Threshold Scorecard (1 minute)

**Say**: "Three of six thresholds pass: both latency targets and the model size target. Energy and memory are not yet measured -- we need Instruments traces for those. The quality threshold still fails: v1 achieves 27.5% test exact match versus the 70% target -- a 2.75x improvement over v0's 10%, but still far from the goal. Closing this gap requires continued dataset scaling and a stronger model architecture."

**Emphasis**: Honest accounting. 27.5% is real progress over 10%, but do not minimize the remaining gap to 70%.

**Do not claim**: That passing 3/6 means the system is "mostly effective," or that 27.5% is close to the target.

---

## Slide 12: Pareto View (30 seconds)

**Say**: "With only two model points, the Pareto frontier is trivial -- both are optimal by default. This view becomes meaningful once we add stronger models that trade off size and latency for accuracy."

**Transition**: Brief slide. Move to the demo.

---

## Slide 13: App Demo (1 minute)

**Say**: "The app supports the full workflow: import a screenshot, type a question, and get an answer with latency displayed in real time. Benchmark mode runs batch evaluation and exports results to CSV. The UI uses a glass-morphism design system with staggered animations, haptic feedback, and TipKit onboarding tips."

**If doing a live demo**: Walk through one screenshot import, one question, show the latency readout, then switch to benchmark mode briefly.

**If not doing a live demo**: Reference the demo flow document and show a screenshot of the app.

---

## Slide 14: Statistical Methods (45 seconds)

**Say**: "We use bootstrap confidence intervals with 10,000 resamples for all metric estimates, paired bootstrap for strategy comparisons, and power-law fits in log-log space for scaling analysis. Every output carries an explicit status label from a fixed vocabulary: complete, partial, blocked, or degenerate. This prevents us from accidentally presenting incomplete results as conclusions."

**Emphasis**: The status vocabulary -- this is a methodological contribution.

---

## Slide 15: Limitations (1 minute)

**Say**: "We want to be upfront about limitations. The quality gap remains large -- 27.5% versus 70%, even after scaling to 128 classes and 452 examples. The v1 model has only 47 thousand parameters with no pretrained weights. Learning curves and selection sweeps are still from the v0/dataset-v1 regime (52 examples) and need to be re-run with dataset v2. We have a single annotator. Energy and memory are unmeasured. The KG-guided strategy is blocked. And three seeds per condition is not enough for reliable bootstrap intervals."

**Emphasis**: Read these as facts, not apologies. The pipeline is designed to address each one.

**Do not claim**: That these limitations are minor or easily fixed.

---

## Slide 16: Key Contributions (1 minute)

**Say**: "Despite the limitations, we make four contributions. First, a fully reproducible end-to-end pipeline from data curation through deployment and analysis. Second, physical-device latency evidence showing 14.0-14.5ms inference across two model generations on the A17 Pro, confirming that scaling from 24 to 128 classes has negligible latency cost. Third, an honest status tracking system with model metadata sidecars that prevents overstatement. Fourth, infrastructure that is ready for stronger models and larger datasets without architectural changes."

**Emphasis**: Contributions are infrastructure and methodology, not accuracy claims.

---

## Slide 17: Next Steps (45 seconds)

**Say**: "Going forward, we plan to re-run the selection sweeps and learning curves with dataset v2's 452 examples, train a stronger model such as a LoRA-adapted vision-language model to close the quality gap, collect Instruments traces for memory and energy, build the knowledge graph for KG-guided selection, and prepare the paper for submission."

**Transition**: "With that, we're happy to take questions."

---

## Slide 18: Thank You / Questions (open-ended)

**Say**: "Thank you. The repository is public on GitHub. We welcome questions."

---

# Handling Questions

## "Why is the EM so low?"

**Honest answer**: With v1, we have improved from 10% to 27.5% test EM by scaling from 52 examples (24 classes) to 452 examples (128 classes). But 27.5% on 128 classes is still far from the 70% target. The v1 model is a 47-thousand-parameter network trained from scratch with no pretrained weights -- it needs pretrained visual features to go further. Both continued data scaling and a stronger model architecture are needed.

**Do not say**: "It's just a baseline." Instead say: "v1 shows meaningful improvement -- 2.75x over v0 -- but reaching 70% EM requires a model with pretrained visual features, such as a LoRA-adapted vision-language model, which the pipeline is designed to support."

## "Is 14ms a meaningful latency result?"

**Honest answer**: Yes, for three reasons. First, it confirms that the Core ML inference path works correctly on physical hardware. Second, the 28x margin means we have substantial room to use a larger model before latency becomes a concern. Third, v1 (128 classes, 47K params) runs at p50=14.5ms versus v0's 14.0ms -- essentially identical -- which confirms that scaling from 24 to 128 classes has negligible latency cost. But latency alone does not make the system effective; quality must improve.

## "Will you reach 70% EM?"

**Honest answer**: The trend is encouraging -- v1 improved from 10% to 27.5% by scaling data from 52 to 452 examples -- but we still need to nearly triple accuracy. Reaching 70% EM will require a model with pretrained visual features, such as a LoRA-adapted vision-language model, and potentially further dataset expansion. The pipeline is designed to support exactly this progression.

**Do not say**: "Definitely" or "Easily." The honest answer is "the trend is positive but the gap is still large, and we need to do the work."

## "What about energy and memory?"

**Honest answer**: We have not yet measured energy or memory on-device. These require Instruments Energy Log and Instruments Allocations traces, respectively. The benchmark infrastructure in the app is ready to collect this data; we simply have not completed those measurement sessions yet.

## "Why not use a bigger model?"

**Honest answer**: We deliberately started with a minimal model to validate the entire pipeline end-to-end: data curation, training, export, deployment, benchmarking, and analysis. Now that the pipeline is validated, the next step is to train a LoRA-adapted vision-language model, which the export and deployment infrastructure already supports.

## "How do you know 52 examples is too few?"

**Honest answer**: The learning curves from the v0/dataset-v1 regime show it. All three selection strategies converge to the same 10% EM, the power-law fits have very low R-squared, and the uncertainty strategy is degenerate. There is no signal to differentiate strategies. Note: these curves have not yet been re-run with dataset v2's 452 examples -- that re-run is planned and may show a different picture.

## "Is this publishable?"

**Honest answer**: The infrastructure and methodology are solid. The empirical results show progress (v1's 27.5% is 2.75x over v0's 10%) but are still partial -- the quality gap to 70% remains large, learning curves need re-running with dataset v2, and energy/memory measurements are outstanding. For a publication, we need to close the quality gap and complete those measurements. The honest status tracking, model metadata sidecars, and reproducible pipeline are genuine contributions regardless of the final accuracy numbers.
