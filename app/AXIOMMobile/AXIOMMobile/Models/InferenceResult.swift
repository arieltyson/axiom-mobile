import Foundation

struct InferenceResult {
    let answer: String
    let modelID: String
    let latencySeconds: Double
    let timestamp: Date
    let isPlaceholder: Bool

    /// Softmax probability of the top-1 predicted class (0.0–1.0).
    ///
    /// For classifier models, this is computed from the logits via softmax.
    /// A uniform guess would be 1/numClasses (e.g. ~0.78% for 128 classes).
    /// `nil` for placeholder results where no real inference occurred.
    let confidence: Double?

    /// The number of classes in the model's output vocabulary.
    /// Used to contextualize confidence (e.g. 1/numClasses = random baseline).
    let numClasses: Int?

    init(
        answer: String,
        modelID: String,
        latencySeconds: Double,
        timestamp: Date,
        isPlaceholder: Bool,
        confidence: Double? = nil,
        numClasses: Int? = nil
    ) {
        self.answer = answer
        self.modelID = modelID
        self.latencySeconds = latencySeconds
        self.timestamp = timestamp
        self.isPlaceholder = isPlaceholder
        self.confidence = confidence
        self.numClasses = numClasses
    }

    // MARK: - Confidence Assessment

    /// Confidence threshold for the model that produced this result.
    ///
    /// Loaded from the model's bundled metadata sidecar (e.g.
    /// `tiny_multimodal_v1_metadata.json`). Falls back to a conservative
    /// default if metadata is unavailable.
    var confidenceThreshold: Double {
        ModelMetadata.forModel(modelID).confidenceThreshold
    }

    /// Whether this result's confidence is too low to present as a valid answer.
    var isLowConfidence: Bool {
        guard let confidence, !isPlaceholder else { return false }
        return confidence < confidenceThreshold
    }
}

// MARK: - Model Metadata (loaded from bundled JSON sidecars)

/// Per-model metadata loaded from bundled JSON files.
///
/// Each Core ML model ships with a `{model_id}_metadata.json` sidecar
/// containing the empirically calibrated confidence threshold, class count,
/// supported question types, and task summary. This avoids hardcoding
/// model-specific constants in Swift.
struct ModelMetadata {
    let modelID: String
    let numClasses: Int
    let confidenceThreshold: Double
    let randomBaseline: Double
    let supportedQuestionTypes: [String]
    let taskSummary: String

    /// Default metadata for unknown models — conservative threshold.
    static let fallback = ModelMetadata(
        modelID: "unknown",
        numClasses: 0,
        confidenceThreshold: 0.50,
        randomBaseline: 0.0,
        supportedQuestionTypes: [],
        taskSummary: "Unknown model"
    )

    /// Cache of loaded metadata keyed by model ID.
    private static var cache: [String: ModelMetadata] = [:]

    /// Returns metadata for a given model ID, loading from bundle if needed.
    static func forModel(_ modelID: String) -> ModelMetadata {
        if let cached = cache[modelID] { return cached }

        let loaded = loadFromBundle(modelID: modelID)
        cache[modelID] = loaded
        return loaded
    }

    private static func loadFromBundle(modelID: String) -> ModelMetadata {
        guard let url = Bundle.main.url(
            forResource: "\(modelID)_metadata",
            withExtension: "json"
        ) else {
            return fallback
        }

        do {
            let data = try Data(contentsOf: url)
            let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            return ModelMetadata(
                modelID: json["model_id"] as? String ?? modelID,
                numClasses: json["num_classes"] as? Int ?? 0,
                confidenceThreshold: json["confidence_threshold"] as? Double ?? 0.50,
                randomBaseline: json["random_baseline"] as? Double ?? 0.0,
                supportedQuestionTypes: json["supported_question_types"] as? [String] ?? [],
                taskSummary: json["task_summary"] as? String ?? ""
            )
        } catch {
            return fallback
        }
    }
}
