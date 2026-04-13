import SwiftUI

/// Layout tokens for adaptive multi-device support.
///
/// Provides responsive column counts, max widths, and reading-line
/// constraints for iPhone, iPad, and larger displays.
enum AXLayout {

    /// Maximum content width on iPad / larger displays.
    /// Prevents ultra-wide card stretching.
    static let maxContentWidth: CGFloat = 600

    /// Optimal reading-line length — constrains text blocks.
    static let maxReadingWidth: CGFloat = 540

    /// Minimum touch target — Apple HIG requirement.
    static let minTouchTarget: CGFloat = 44

    /// Whether to use a centered column layout (iPad landscape, etc.).
    static func useCenteredLayout(for sizeClass: UserInterfaceSizeClass?)
        -> Bool
    {
        sizeClass == .regular
    }
}

// MARK: - Responsive Container Modifier

extension View {
    /// Constrains content to a readable width on larger screens.
    ///
    /// On compact (iPhone), this is a no-op — full-width layout.
    /// On regular (iPad), centers content within `AXLayout.maxContentWidth`.
    func axResponsiveContainer() -> some View {
        self.modifier(ResponsiveContainerModifier())
    }
}

private struct ResponsiveContainerModifier: ViewModifier {
    @Environment(\.horizontalSizeClass) private var sizeClass

    func body(content: Content) -> some View {
        if AXLayout.useCenteredLayout(for: sizeClass) {
            content
                .frame(maxWidth: AXLayout.maxContentWidth)
                .frame(maxWidth: .infinity)
        } else {
            content
        }
    }
}
