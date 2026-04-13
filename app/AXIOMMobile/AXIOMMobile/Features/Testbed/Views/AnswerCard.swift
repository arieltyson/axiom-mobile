import SwiftUI

struct AnswerCard: View {
    let result: InferenceResult

    @State private var appeared = false

    var body: some View {
        GlassCard(.hero) {
            VStack(alignment: .leading, spacing: AXSpacing.md) {
                HStack {
                    SectionHeader(
                        "Answer",
                        icon: "sparkles",
                        tint: AXColor.accentSecondary
                    )
                    Spacer()
                    latencyBadge
                }

                Text(result.answer)
                    .font(.title3.weight(.medium))
                    .foregroundStyle(AXColor.textPrimary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(AXSpacing.lg)
                    .background {
                        RoundedRectangle(cornerRadius: AXRadius.md)
                            .fill(
                                LinearGradient(
                                    colors: [
                                        AXColor.accentPrimary.opacity(0.08),
                                        AXColor.accentSecondary.opacity(0.04),
                                    ],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                    }
                    .overlay {
                        RoundedRectangle(cornerRadius: AXRadius.md)
                            .strokeBorder(
                                AXColor.accentPrimary.opacity(0.15),
                                lineWidth: AXStroke.hairline
                            )
                    }

                if result.isPlaceholder {
                    StatusBadge(
                        "Placeholder \u{2014} model not connected",
                        variant: .warning,
                        icon: "info.circle"
                    )
                } else if result.modelID == "tiny_multimodal_v0" {
                    Text(
                        "This model classifies mobile app screenshots into a fixed set of 24 answer categories. Results on non-screenshot images or open-ended questions may not be meaningful."
                    )
                    .font(AXFont.caption)
                    .foregroundStyle(AXColor.textTertiary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
        }
        .axShadow(appeared ? AXElevation.medium : AXElevation.none)
        .scaleEffect(appeared ? 1.0 : 0.97)
        .onAppear {
            withAnimation(AXMotion.gentle) {
                appeared = true
            }
        }
        .accessibilityElement(children: .combine)
    }

    private var latencyBadge: some View {
        let ms = Int(result.latencySeconds * 1000)
        return StatusBadge(
            "\(ms) ms",
            variant: ms < 400 ? .success : .warning,
            icon: "bolt.fill"
        )
    }
}
