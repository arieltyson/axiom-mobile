import UIKit

/// Provides repeatable benchmark inputs for profiling sessions.
///
/// The provider follows a two-tier strategy:
/// 1. **Persisted screenshot**: If a `benchmark_screenshot.png` exists in the
///    app's Documents directory (placed there by a one-time manual import),
///    it is loaded and used. This is the preferred path for publishable
///    profiling because it exercises real image preprocessing on a real
///    screenshot.
/// 2. **Synthetic test pattern**: If no persisted screenshot is found, a
///    deterministic gradient+noise image is generated. This exercises the
///    full `CVPixelBuffer` pipeline (resize, color space conversion) with
///    non-trivial pixel data, unlike a blank black image.
///
/// ## Preparing a persisted screenshot
///
/// From the testbed UI:
/// 1. Import any screenshot via the photo picker.
/// 2. Tap "Save as Benchmark Input" (or manually copy a `.png` to the
///    app's Documents directory as `benchmark_screenshot.png`).
///
/// From the command line (simulator):
/// ```bash
/// DOCS=$(xcrun simctl get_app_container booted com.arieljtyson.AXIOMMobile data)/Documents
/// cp /path/to/screenshot.png "$DOCS/benchmark_screenshot.png"
/// ```
enum BenchmarkInputProvider {

    /// Well-known filename for the persisted benchmark screenshot.
    static let persistedFilename = "benchmark_screenshot.png"

    /// Default question used for auto-benchmark profiling sessions.
    static let defaultQuestion = "What is shown on screen?"

    /// Default iteration count for publishable profiling runs.
    static let publishableIterations = 50

    /// Loads the benchmark screenshot, preferring a persisted real image.
    ///
    /// - Returns: A tuple of the loaded image and a description of the source
    ///   (`"persisted"` or `"synthetic"`).
    static func loadScreenshot() -> (image: UIImage, source: String) {
        if let persisted = loadPersistedScreenshot() {
            return (persisted, "persisted")
        }
        return (generateSyntheticTestPattern(), "synthetic")
    }

    /// Saves the given image as the persisted benchmark screenshot.
    ///
    /// Call this once from the UI after importing a representative screenshot
    /// to enable repeatable profiling with real data.
    static func persistScreenshot(_ image: UIImage) throws {
        guard let data = image.pngData() else {
            throw BenchmarkInputError.imageEncodingFailed
        }
        let url = URL.documentsDirectory.appending(path: persistedFilename)
        try data.write(to: url, options: .atomic)
    }

    /// Whether a persisted benchmark screenshot exists in Documents.
    static var hasPersistedScreenshot: Bool {
        let url = URL.documentsDirectory.appending(path: persistedFilename)
        return FileManager.default.fileExists(atPath: url.path(percentEncoded: false))
    }

    // MARK: - Private

    /// Attempts to load the persisted screenshot from Documents.
    private static func loadPersistedScreenshot() -> UIImage? {
        let url = URL.documentsDirectory.appending(path: persistedFilename)
        guard let data = try? Data(contentsOf: url),
              let image = UIImage(data: data) else {
            return nil
        }
        return image
    }

    /// Generates a deterministic synthetic test pattern image.
    ///
    /// The image is 390×844 (iPhone-scale) with a diagonal gradient and
    /// deterministic pseudo-noise blocks. This exercises the full image
    /// preprocessing pipeline (resize to 128×128, BGRA conversion) with
    /// non-trivial pixel data, unlike a blank black image.
    private static func generateSyntheticTestPattern() -> UIImage {
        let width = 390
        let height = 844
        let size = CGSize(width: width, height: height)

        let renderer = UIGraphicsImageRenderer(size: size)
        return renderer.image { context in
            let cgContext = context.cgContext

            // Background diagonal gradient: dark blue to teal
            let colors: [CGFloat] = [
                0.05, 0.1, 0.3, 1.0,  // Dark blue
                0.1, 0.5, 0.5, 1.0    // Teal
            ]
            let colorSpace = CGColorSpaceCreateDeviceRGB()
            if let gradient = CGGradient(
                colorSpace: colorSpace,
                colorComponents: colors,
                locations: [0.0, 1.0],
                count: 2
            ) {
                cgContext.drawLinearGradient(
                    gradient,
                    start: .zero,
                    end: CGPoint(x: CGFloat(width), y: CGFloat(height)),
                    options: []
                )
            }

            // Deterministic pseudo-noise blocks to add visual complexity
            // Uses a simple LCG (linear congruential generator) for reproducibility
            var seed: UInt64 = 42
            let blockSize = 20

            for row in stride(from: 0, to: height, by: blockSize) {
                for col in stride(from: 0, to: width, by: blockSize) {
                    // LCG: next = (a * seed + c) mod m
                    seed = (seed &* 6_364_136_223_846_793_005 &+ 1_442_695_040_888_963_407)
                    let value = CGFloat((seed >> 33) % 100) / 400.0  // 0.0–0.25 range

                    UIColor(white: value, alpha: 0.3).setFill()
                    cgContext.fill(
                        CGRect(x: col, y: row, width: blockSize, height: blockSize)
                    )
                }
            }

            // Simulated UI elements: rectangles resembling a status bar and content
            UIColor.white.withAlphaComponent(0.8).setFill()
            cgContext.fill(CGRect(x: 0, y: 0, width: width, height: 54))  // Status bar

            UIColor.white.withAlphaComponent(0.15).setFill()
            cgContext.fill(CGRect(x: 20, y: 100, width: width - 40, height: 200))  // Content card
            cgContext.fill(CGRect(x: 20, y: 320, width: width - 40, height: 120))  // Secondary card
            cgContext.fill(CGRect(x: 20, y: 460, width: 160, height: 160))  // Grid item
            cgContext.fill(CGRect(x: 200, y: 460, width: 170, height: 160))  // Grid item
        }
    }
}

// MARK: - Errors

enum BenchmarkInputError: LocalizedError {
    case imageEncodingFailed

    var errorDescription: String? {
        switch self {
        case .imageEncodingFailed:
            "Failed to encode screenshot as PNG for benchmark persistence."
        }
    }
}
