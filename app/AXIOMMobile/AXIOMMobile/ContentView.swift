import SwiftUI

struct ContentView: View {
    @State private var isLaunching = true

    var body: some View {
        ZStack {
            TestbedView()
                .opacity(isLaunching ? 0 : 1)

            if isLaunching {
                LaunchScreen()
                    .transition(.opacity)
            }
        }
        .task {
            // Brief branded launch screen before revealing content.
            try? await Task.sleep(for: .seconds(1.2))
            withAnimation(.smooth(duration: 0.5)) {
                isLaunching = false
            }
        }
    }
}

#Preview {
    ContentView()
}
