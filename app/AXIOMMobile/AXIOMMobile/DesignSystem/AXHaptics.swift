import SwiftUI

/// Haptic feedback tokens for consistent tactile responses.
///
/// Maps logical events to Apple's `SensoryFeedback` types.
/// Feature views use these via `.sensoryFeedback()` modifiers.
enum AXHaptics {

    /// Inference completed successfully.
    static let inferenceComplete: SensoryFeedback = .success

    /// Benchmark batch finished.
    static let benchmarkComplete: SensoryFeedback = .success

    /// Export or save action succeeded.
    static let exportSuccess: SensoryFeedback = .success

    /// Screenshot selected or loaded.
    static let imageLoaded: SensoryFeedback = .selection

    /// Model selection changed.
    static let modelChanged: SensoryFeedback = .selection

    /// Toggle or switch flipped.
    static let toggleChanged: SensoryFeedback = .selection

    /// Destructive action (clear, delete).
    static let destructiveAction: SensoryFeedback = .warning

    /// Error or failure state.
    static let error: SensoryFeedback = .error

    /// General interactive tap — lightweight selection feedback.
    static let tap: SensoryFeedback = .selection
}
