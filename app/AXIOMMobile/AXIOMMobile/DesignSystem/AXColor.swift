import SwiftUI

// MARK: - Semantic Color Tokens

/// Centralized color vocabulary for the AXIOM design system.
///
/// Every feature view consumes these tokens — never raw RGB values.
/// All colors adapt to Light / Dark / High-Contrast automatically
/// via `Color(light:dark:)` or system-provided roles.
enum AXColor {

    // MARK: Accent

    /// Primary interactive accent — buttons, links, active controls.
    /// Light: deeper blue for WCAG AA contrast on white. Dark: bright blue.
    static let accentPrimary = Color(
        light: .init(red: 0.16, green: 0.35, blue: 0.88),
        dark: .init(red: 0.35, green: 0.55, blue: 1.0)
    )

    /// Secondary accent for supporting indicators and highlights.
    /// Light: richer purple for readability. Dark: soft violet.
    static let accentSecondary = Color(
        light: .init(red: 0.38, green: 0.25, blue: 0.85),
        dark: .init(red: 0.55, green: 0.45, blue: 1.0)
    )

    /// Subtle glow / emphasis tint for elevated surfaces.
    static let accentGlow = Color(
        light: .init(red: 0.30, green: 0.50, blue: 1.0).opacity(0.12),
        dark: .init(red: 0.35, green: 0.55, blue: 1.0).opacity(0.10)
    )

    // MARK: Background

    /// Canvas / root background.
    /// Light: warm off-white with slight blue tint. Dark: near-black.
    static let backgroundBase = Color(
        light: .init(red: 0.96, green: 0.96, blue: 0.98),
        dark: .init(red: 0.04, green: 0.04, blue: 0.06)
    )

    /// Gradient top — subtle warmth in light, deep blue-black in dark.
    static let backgroundGradientTop = Color(
        light: .init(red: 0.97, green: 0.97, blue: 0.99),
        dark: .init(red: 0.06, green: 0.06, blue: 0.10)
    )

    /// Gradient bottom — slight cool shift in light, deepest dark.
    static let backgroundGradientBottom = Color(
        light: .init(red: 0.94, green: 0.94, blue: 0.96),
        dark: .init(red: 0.02, green: 0.02, blue: 0.04)
    )

    // MARK: Glass

    /// Fill tint for glass cards (additive in dark, subtractive in light).
    /// Light: higher opacity for cleaner card surfaces against gradient.
    static let glassFill = Color(
        light: .init(white: 1.0).opacity(0.75),
        dark: .init(white: 1.0).opacity(0.05)
    )

    /// Stroke for glass card borders.
    /// Light: slightly stronger for visible card edges on white.
    static let glassStroke = Color(
        light: .init(white: 0.0).opacity(0.08),
        dark: .init(white: 1.0).opacity(0.08)
    )

    /// Highlight edge on glass cards (top or leading).
    static let glassHighlight = Color(
        light: .init(white: 1.0).opacity(0.95),
        dark: .init(white: 1.0).opacity(0.12)
    )

    // MARK: Text

    /// Primary text — headings, body, values.
    static let textPrimary = Color.primary

    /// Secondary text — captions, subtitles, supporting copy.
    static let textSecondary = Color.secondary

    /// Tertiary text — least-important metadata.
    /// Light: darker for better readability. Dark: soft white.
    static let textTertiary = Color(
        light: .init(white: 0.0).opacity(0.38),
        dark: .init(white: 1.0).opacity(0.35)
    )

    // MARK: Status

    /// Success — thresholds met, ready states.
    static let statusSuccess = Color(
        light: .init(red: 0.20, green: 0.70, blue: 0.40),
        dark: .init(red: 0.30, green: 0.85, blue: 0.50)
    )

    /// Warning — partial, attention needed.
    static let statusWarning = Color(
        light: .init(red: 0.90, green: 0.65, blue: 0.15),
        dark: .init(red: 1.0, green: 0.75, blue: 0.25)
    )

    /// Critical — failure, blocked.
    static let statusCritical = Color(
        light: .init(red: 0.90, green: 0.25, blue: 0.20),
        dark: .init(red: 1.0, green: 0.35, blue: 0.30)
    )

    /// Informational — neutral callouts.
    static let statusInfo = Color(
        light: .init(red: 0.30, green: 0.55, blue: 0.85),
        dark: .init(red: 0.45, green: 0.70, blue: 1.0)
    )
}

// MARK: - Adaptive Color Initializer

extension Color {
    /// Creates an adaptive color that resolves to `light` or `dark` variants.
    init(light: Color, dark: Color) {
        self.init(
            uiColor: UIColor { traits in
                traits.userInterfaceStyle == .dark
                    ? UIColor(dark)
                    : UIColor(light)
            }
        )
    }
}
