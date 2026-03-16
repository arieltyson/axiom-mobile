# Ariel Task Guide

Below is the complete, optimal, hand-held solution for the next logical chunk for Ariel:

**SwiftUI Testbed Shell (iOS First)**

Follow it exactly and you will end with a clean PR that creates the first real app surface for AXIOM-Mobile.

This is intentionally **iOS-first**. Do not try to solve full Core ML integration or full macOS support in the same chunk. The goal is a clean app shell that proves the end-user interaction loop.

---

## Goal of This Step

By the end, the repo will contain:

- an Xcode project under `app/`
- a SwiftUI testbed shell that can:
  - import/select a screenshot
  - accept a natural-language question
  - choose a model id from the current shortlist
  - display a placeholder answer
  - display a small debug/metrics panel
- `app/README.md` with build instructions

This task matters because the project now has a Python-side baseline scaffold but no app interface at all.

---

## What You Will Accomplish in This Chunk

1. Create the first iOS app target for AXIOM-Mobile
2. Build a usable SwiftUI shell for screenshot QA
3. Add a placeholder inference engine so the interface is testable before Core ML exists
4. Open a PR that starts the mobile side of the system

---

## 1) Create a New Branch for This Step

From inside the repo:

```bash
git checkout main
git pull upstream main
git checkout -b app/testbed-shell-v0
```

---

## 2) Create the Xcode Project

Inside `app/`, create a new SwiftUI iOS app project.

### Recommended project settings

- Product name: `AXIOMMobile`
- Interface: `SwiftUI`
- Language: `Swift`
- Testing: include unit tests if convenient, but not required for this first shell

### Recommended location

Create the project under:

- `app/AXIOMMobile/`

Expected repo-visible items should include:

- `app/AXIOMMobile/AXIOMMobile.xcodeproj`
- source files under `app/AXIOMMobile/AXIOMMobile/`

Do **not** commit:

- personal user data
- derived data
- workspace state files that do not belong in git

---

## 3) Build the First Testbed Screen

Create a single main screen for screenshot question answering.

### Required UI elements

Your screen should include:

1. a screenshot import area
2. a text field for the question
3. a model picker using these current model ids:
   - `question_lookup_v0`
   - `florence_2_base`
   - `llava_mobile`
   - `qwen_vl_chat_int4`
4. a `Run` button
5. an answer output card
6. a small debug/metrics card

### Recommended SwiftUI file split

You do **not** have to use these exact filenames, but this is the cleanest first pass:

- `AXIOMMobileApp.swift`
- `TestbedView.swift`
- `TestbedViewModel.swift`
- `ModelCatalog.swift`
- `DemoInferenceEngine.swift`
- `AnswerCardView.swift`
- `MetricsCardView.swift`

---

## 4) Add Placeholder App Behavior

Do **not** try to wire in real ML yet.

Instead, add a simple local demo engine that:

1. accepts:
   - selected model id
   - imported screenshot
   - question text
2. waits briefly or records a fake latency
3. returns a placeholder answer such as:
   - `Demo answer: model not connected yet`
4. updates the debug/metrics card with:
   - selected model id
   - question length
   - whether an image is loaded
   - simulated latency in ms

This is enough to prove the app flow without blocking on Core ML.

---

## 5) Add Screenshot Import

Implement a simple import path for screenshots.

### Acceptable first-pass options

Choose one:

1. `PhotosPicker`
2. file importer
3. drag-and-drop if you decide to support iPad/macOS later

For this first chunk, the imported image only needs to display in the UI. It does **not** need to be serialized or passed to a model yet.

---

## 6) Add `app/README.md`

Create:

- `app/README.md`

### Required sections

Use:

1. `Purpose`
2. `Current Scope`
3. `Project Structure`
4. `How to Build`
5. `What Is Still Placeholder`

### Required content

Document:

- this is the Phase 2 SwiftUI shell
- it currently uses placeholder inference
- real Core ML/model execution is not connected yet
- how to open the project in Xcode

---

## 7) Build and Verify Locally

Use Xcode to confirm the app builds and runs.

### Minimum verification checklist

You should be able to:

- launch the app in the simulator
- import/select a screenshot
- type a question
- switch model ids in the picker
- tap `Run`
- see the placeholder answer and debug info update

If you want a CLI build check, run:

```bash
xcodebuild -project app/AXIOMMobile/AXIOMMobile.xcodeproj -scheme AXIOMMobile -destination 'generic/platform=iOS Simulator' build
```

---

## 8) Check Your Changes Before Committing

Run:

```bash
git status
```

You should see the new app project and source files, plus:

- `app/README.md`

If Xcode generated obvious user-specific junk files, remove them before committing.

---

## 9) Commit Cleanly

```bash
git add app
git commit -m "app: add SwiftUI screenshot QA testbed shell"
```

---

## 10) Push Your Branch

```bash
git push -u origin app/testbed-shell-v0
```

---

## 11) Open a PR to the Team Repo

Use:

- Base repository: `AIML-Research-SFU/axiom-mobile`
- Base branch: `main`
- Compare branch: `app/testbed-shell-v0`

### PR title

```text
app: add SwiftUI screenshot QA testbed shell
```

### PR description

```text
Adds the first iOS SwiftUI testbed shell for AXIOM-Mobile with screenshot import, question input, model picker, and placeholder inference/debug output.
```

---

## Done Definition

You are done with this chunk when:

- the Xcode project exists under `app/`
- the app builds locally
- the testbed screen supports screenshot import + question input + model picker + placeholder answer
- `app/README.md` exists
- the PR is open
