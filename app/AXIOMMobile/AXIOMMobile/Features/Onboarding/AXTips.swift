import TipKit

/// First-run tips explaining the research context and key interactions.
///
/// Uses Apple TipKit (iOS 17+) for system-standard tip presentation.
/// Tips are shown once and automatically dismissed after interaction.

// MARK: - Research Context Tip

/// Shown on first launch — explains what AXIOM is and what the app does.
struct ResearchContextTip: Tip {

    var title: Text {
        Text("Welcome to AXIOM")
    }

    var message: Text? {
        Text(
            "This research testbed evaluates screenshot question-answering models. "
                + "Import a screenshot, ask a question, and run inference to see results."
        )
    }

    var image: Image? {
        Image(systemName: "flask")
    }

    var options: [any TipOption] {
        MaxDisplayCount(1)
    }
}

// MARK: - Screenshot Import Tip

/// Shown near the screenshot section — encourages first import.
struct ScreenshotImportTip: Tip {

    @Parameter
    static var hasImportedScreenshot: Bool = false

    var title: Text {
        Text("Start with a Screenshot")
    }

    var message: Text? {
        Text(
            "Tap \"Select Screenshot\" to import an image from your photo library. "
                + "The model will analyze it to answer your question."
        )
    }

    var image: Image? {
        Image(systemName: "photo.badge.plus")
    }

    var rules: [Rule] {
        #Rule(Self.$hasImportedScreenshot) { $0 == false }
    }

    var options: [any TipOption] {
        MaxDisplayCount(1)
    }
}

// MARK: - Benchmark Mode Tip

/// Shown after the user has run a few single inferences.
struct BenchmarkModeTip: Tip {

    @Parameter
    static var singleRunCount: Int = 0

    var title: Text {
        Text("Try Benchmark Mode")
    }

    var message: Text? {
        Text(
            "Toggle Benchmark Mode to run multiple inference passes and collect latency statistics. "
                + "Export results as CSV for analysis."
        )
    }

    var image: Image? {
        Image(systemName: "timer")
    }

    var rules: [Rule] {
        #Rule(Self.$singleRunCount) { $0 >= 3 }
    }

    var options: [any TipOption] {
        MaxDisplayCount(1)
    }
}

// MARK: - Core ML Tip

/// Shown when the user selects a placeholder model.
struct CoreMLModelTip: Tip {

    @Parameter
    static var hasSelectedPlaceholder: Bool = false

    var title: Text {
        Text("Real Inference Available")
    }

    var message: Text? {
        Text(
            "\"Tiny Multimodal v0\" uses a real Core ML model for on-device inference. "
                + "Other models show placeholder results."
        )
    }

    var image: Image? {
        Image(systemName: "cpu")
    }

    var rules: [Rule] {
        #Rule(Self.$hasSelectedPlaceholder) { $0 == true }
    }

    var options: [any TipOption] {
        MaxDisplayCount(1)
    }
}
