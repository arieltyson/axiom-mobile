import SwiftUI
import TipKit

@main
struct AXIOMMobileApp: App {

    init() {
        // Configure TipKit for first-run onboarding tips.
        try? Tips.configure([
            .displayFrequency(.immediate),
            .datastoreLocation(.applicationDefault),
        ])
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
