import SwiftUI

/// Transition presets for consistent card/section appearance.
///
/// Respects Reduce Motion — transitions degrade gracefully to opacity-only
/// when the system accessibility setting is enabled.
enum AXTransition {

    /// Card entrance from below — hero and standard cards.
    static let cardEntrance: AnyTransition = .asymmetric(
        insertion: .opacity.combined(with: .move(edge: .bottom))
            .combined(with: .scale(scale: 0.97)),
        removal: .opacity
    )

    /// Result / answer appearance — scale up from center with fade.
    static let resultAppearance: AnyTransition = .asymmetric(
        insertion: .opacity.combined(with: .scale(scale: 0.95)),
        removal: .opacity
    )

    /// Section expansion — top-aligned slide with fade.
    static let sectionExpand: AnyTransition =
        .opacity.combined(with: .move(edge: .top))

    /// Subtle fade-only — for status badges, small elements.
    static let subtle: AnyTransition = .opacity
}

// MARK: - Staggered Appearance Modifier

extension View {
    /// Applies a staggered entrance animation to a card at a given index.
    ///
    /// Cards appear sequentially with a short delay between each,
    /// creating a pleasant cascade effect on first load.
    /// Respects Reduce Motion.
    func axStaggeredAppearance(index: Int, isVisible: Bool) -> some View {
        self.modifier(
            StaggeredAppearanceModifier(index: index, isVisible: isVisible)
        )
    }
}

private struct StaggeredAppearanceModifier: ViewModifier {
    let index: Int
    let isVisible: Bool

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    private var delay: Double {
        reduceMotion ? 0 : Double(index) * 0.06
    }

    func body(content: Content) -> some View {
        content
            .opacity(isVisible ? 1 : 0)
            .offset(y: isVisible || reduceMotion ? 0 : 12)
            .scaleEffect(isVisible || reduceMotion ? 1 : 0.97)
            .animation(
                reduceMotion
                    ? .none
                    : AXMotion.gentle.delay(delay),
                value: isVisible
            )
    }
}
