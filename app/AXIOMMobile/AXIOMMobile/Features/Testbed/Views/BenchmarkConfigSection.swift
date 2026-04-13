import SwiftUI
import TipKit

struct BenchmarkConfigSection: View {
    @Binding var enabled: Bool
    @Binding var iterations: Int

    private let benchmarkTip = BenchmarkModeTip()

    var body: some View {
        GlassCard(.subdued) {
            VStack(alignment: .leading, spacing: AXSpacing.md) {
                Toggle(isOn: $enabled) {
                    SectionHeader(
                        "Benchmark",
                        icon: "timer",
                        tint: AXColor.statusWarning
                    )
                }
                .tint(AXColor.accentPrimary)

                if !enabled {
                    TipView(benchmarkTip, arrowEdge: .top)
                        .tipBackground(AXColor.glassFill)
                }

                if enabled {
                    VStack(alignment: .leading, spacing: AXSpacing.sm) {
                        Stepper(value: $iterations, in: 1...50) {
                            HStack(spacing: AXSpacing.xs) {
                                Text("Iterations")
                                    .font(AXFont.caption)
                                    .foregroundStyle(AXColor.textSecondary)
                                Text("\(iterations)")
                                    .font(AXFont.mono)
                                    .foregroundStyle(AXColor.textPrimary)
                            }
                        }
                        .sensoryFeedback(AXHaptics.tap, trigger: iterations)

                        Text(
                            "Runs inference repeatedly and logs latency statistics."
                        )
                        .font(AXFont.caption)
                        .foregroundStyle(AXColor.textTertiary)
                    }
                    .transition(AXTransition.sectionExpand)
                }
            }
        }
        .axAnimation(AXMotion.standard, value: enabled)
    }
}
