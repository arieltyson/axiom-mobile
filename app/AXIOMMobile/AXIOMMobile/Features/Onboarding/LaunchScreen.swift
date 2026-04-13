import SwiftUI

/// A branded launch screen displayed during app startup.
///
/// Uses the design system tokens for consistent visual identity.
/// Fades out automatically when the main content is ready.
struct LaunchScreen: View {

    @State private var logoScale: CGFloat = 0.8
    @State private var logoOpacity: Double = 0
    @State private var subtitleOpacity: Double = 0

    var body: some View {
        ZStack {
            // Background gradient matching the main app
            LinearGradient(
                colors: [
                    AXColor.backgroundGradientTop,
                    AXColor.backgroundBase,
                    AXColor.backgroundGradientBottom,
                ],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()

            VStack(spacing: AXSpacing.lg) {
                // App icon representation
                AppIconView(size: 96)
                    .scaleEffect(logoScale)
                    .opacity(logoOpacity)

                VStack(spacing: AXSpacing.xs) {
                    Text("AXIOM")
                        .font(.system(size: 32, weight: .bold, design: .default))
                        .foregroundStyle(AXColor.textPrimary)
                        .opacity(logoOpacity)

                    Text("Screenshot QA Research Testbed")
                        .font(AXFont.caption)
                        .foregroundStyle(AXColor.textTertiary)
                        .opacity(subtitleOpacity)
                }
            }
        }
        .onAppear {
            withAnimation(.smooth(duration: 0.6)) {
                logoScale = 1.0
                logoOpacity = 1.0
            }
            withAnimation(.smooth(duration: 0.5).delay(0.3)) {
                subtitleOpacity = 1.0
            }
        }
    }
}

// MARK: - App Icon View (Programmatic)

/// A programmatic app icon that can be rendered at any size.
///
/// Uses the AXIOM brand colors for a distinctive, research-oriented identity.
/// This same design should be exported as the 1024×1024 app icon asset.
struct AppIconView: View {

    var size: CGFloat = 1024

    private var cornerRadius: CGFloat { size * 0.22 }
    private var iconPadding: CGFloat { size * 0.15 }
    private var glyphSize: CGFloat { size * 0.40 }
    private var ringSize: CGFloat { size * 0.55 }
    private var ringStroke: CGFloat { size * 0.035 }

    var body: some View {
        ZStack {
            // Background
            RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [
                            Color(red: 0.08, green: 0.08, blue: 0.14),
                            Color(red: 0.04, green: 0.04, blue: 0.08),
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )

            // Subtle radial glow
            Circle()
                .fill(
                    RadialGradient(
                        colors: [
                            Color(red: 0.25, green: 0.40, blue: 0.95)
                                .opacity(0.25),
                            Color.clear,
                        ],
                        center: .center,
                        startRadius: 0,
                        endRadius: size * 0.45
                    )
                )

            // Concentric ring — precision/measurement motif
            Circle()
                .strokeBorder(
                    AngularGradient(
                        colors: [
                            Color(red: 0.35, green: 0.55, blue: 1.0)
                                .opacity(0.6),
                            Color(red: 0.55, green: 0.45, blue: 1.0)
                                .opacity(0.3),
                            Color(red: 0.35, green: 0.55, blue: 1.0)
                                .opacity(0.6),
                        ],
                        center: .center
                    ),
                    lineWidth: ringStroke
                )
                .frame(width: ringSize, height: ringSize)

            // Central icon — sparkles (ML inference)
            Image(systemName: "sparkles")
                .font(.system(size: glyphSize, weight: .light))
                .foregroundStyle(
                    LinearGradient(
                        colors: [
                            Color(red: 0.45, green: 0.65, blue: 1.0),
                            Color(red: 0.65, green: 0.55, blue: 1.0),
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )

            // Top-left "A" initial — subtle brand mark
            Text("A")
                .font(
                    .system(
                        size: size * 0.10, weight: .bold, design: .default
                    )
                )
                .foregroundStyle(
                    Color(red: 0.45, green: 0.65, blue: 1.0).opacity(0.5))
                .position(x: size * 0.20, y: size * 0.18)
        }
        .frame(width: size, height: size)
        .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
    }
}

#Preview("App Icon") {
    AppIconView(size: 256)
        .padding()
        .background(Color.gray.opacity(0.2))
}

#Preview("Launch Screen") {
    LaunchScreen()
}
