import SwiftUI
import PhotosUI

struct ScreenshotSection: View {
    @Binding var selectedItem: PhotosPickerItem?
    let image: UIImage?
    let onClear: () -> Void
    var onSaveAsBenchmarkInput: (() -> Void)?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("Screenshot", systemImage: "photo")
                .font(.headline)

            if let image {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
                    .frame(maxHeight: 200)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .overlay(alignment: .topTrailing) {
                        Button("Remove", systemImage: "xmark.circle.fill") {
                            onClear()
                        }
                        .labelStyle(.iconOnly)
                        .buttonStyle(.plain)
                        .foregroundStyle(.white)
                        .shadow(radius: 2)
                        .padding(8)
                    }
                    .accessibilityLabel("Selected screenshot")
            }

            PhotosPicker(selection: $selectedItem, matching: .images) {
                Label(
                    image == nil ? "Select Screenshot" : "Change Screenshot",
                    systemImage: "photo.badge.plus"
                )
                .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)

            if image != nil, let onSave = onSaveAsBenchmarkInput {
                Button {
                    onSave()
                } label: {
                    Label(
                        "Save as Benchmark Input",
                        systemImage: "square.and.arrow.down"
                    )
                    .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .tint(.orange)
                .accessibilityHint(
                    "Persists this screenshot for repeatable auto-benchmark profiling sessions"
                )
            }
        }
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16))
    }
}
