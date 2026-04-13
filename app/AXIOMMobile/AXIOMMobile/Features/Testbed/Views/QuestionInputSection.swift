import SwiftUI

struct QuestionInputSection: View {
    @Binding var question: String
    var isFocused: FocusState<Bool>.Binding
    var selectedModelID: String = ""

    var body: some View {
        GlassCard {
            VStack(alignment: .leading, spacing: AXSpacing.md) {
                SectionHeader("Question", icon: "text.bubble")

                TextField(
                    "e.g. Is Bluetooth on or off?",
                    text: $question,
                    axis: .vertical
                )
                .focused(isFocused)
                .lineLimit(2...5)
                .font(AXFont.body)
                .padding(AXSpacing.md)
                .background {
                    RoundedRectangle(cornerRadius: AXRadius.sm)
                        .fill(AXColor.glassFill)
                }
                .overlay {
                    RoundedRectangle(cornerRadius: AXRadius.sm)
                        .strokeBorder(
                            isFocused.wrappedValue
                                ? AXColor.accentPrimary.opacity(0.4)
                                : AXColor.glassStroke,
                            lineWidth: isFocused.wrappedValue
                                ? AXStroke.thin : AXStroke.hairline
                        )
                }
                .axAnimation(AXMotion.quick, value: isFocused.wrappedValue)

                if selectedModelID.hasPrefix("tiny_multimodal_v") {
                    supportedQuestionsHint
                }
            }
        }
    }

    // MARK: - Supported Questions Hint

    private var supportedQuestionsHint: some View {
        let meta = ModelMetadata.forModel(selectedModelID)
        let hintText: String = if meta.supportedQuestionTypes.isEmpty {
            "Is [setting] on or off? \u{00b7} What battery %? \u{00b7} What time is shown? \u{00b7} What temperature? \u{00b7} What Wi-Fi network?"
        } else {
            meta.supportedQuestionTypes
                .prefix(6)
                .joined(separator: " \u{00b7} ")
        }

        return VStack(alignment: .leading, spacing: AXSpacing.xs) {
            Text("Supported question types")
                .font(AXFont.caption.weight(.medium))
                .foregroundStyle(AXColor.textSecondary)

            Text(hintText)
                .font(AXFont.caption)
                .foregroundStyle(AXColor.textTertiary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .accessibilityLabel(
            "Supported questions: \(meta.supportedQuestionTypes.joined(separator: ", "))"
        )
    }
}
