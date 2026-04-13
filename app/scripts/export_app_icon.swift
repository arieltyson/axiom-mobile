#!/usr/bin/env swift
//
// export_app_icon.swift
//
// Generates the AXIOM app icon as a 1024x1024 PNG using Core Graphics.
// Run from the repo root:
//
//   swift app/scripts/export_app_icon.swift
//
// Output: app/AXIOMMobile/AXIOMMobile/Assets.xcassets/AppIcon.appiconset/AppIcon.png
//
// The icon matches the programmatic AppIconView in LaunchScreen.swift:
// - Deep blue-black gradient background
// - Angular gradient ring (precision motif)
// - Central sparkles glyph
// - Subtle "A" brand mark
//

import CoreGraphics
import Foundation

#if canImport(AppKit)
    import AppKit
#endif

let size = 1024
let scale = 1

func createIcon() -> Data? {
    let colorSpace = CGColorSpaceCreateDeviceRGB()
    guard
        let ctx = CGContext(
            data: nil,
            width: size,
            height: size,
            bitsPerComponent: 8,
            bytesPerRow: 0,
            space: colorSpace,
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        )
    else {
        print("ERROR: Failed to create CGContext")
        return nil
    }

    let rect = CGRect(x: 0, y: 0, width: size, height: size)

    // Background gradient (deep blue-black)
    let bgColors = [
        CGColor(red: 0.08, green: 0.08, blue: 0.14, alpha: 1.0),
        CGColor(red: 0.04, green: 0.04, blue: 0.08, alpha: 1.0),
    ]
    if let gradient = CGGradient(
        colorsSpace: colorSpace,
        colors: bgColors as CFArray,
        locations: [0.0, 1.0]
    ) {
        ctx.drawLinearGradient(
            gradient,
            start: CGPoint(x: 0, y: CGFloat(size)),
            end: CGPoint(x: CGFloat(size), y: 0),
            options: []
        )
    }

    // Radial glow in center
    let glowColors = [
        CGColor(red: 0.25, green: 0.40, blue: 0.95, alpha: 0.25),
        CGColor(red: 0.25, green: 0.40, blue: 0.95, alpha: 0.0),
    ]
    if let glow = CGGradient(
        colorsSpace: colorSpace,
        colors: glowColors as CFArray,
        locations: [0.0, 1.0]
    ) {
        let center = CGPoint(x: CGFloat(size) / 2, y: CGFloat(size) / 2)
        ctx.drawRadialGradient(
            glow,
            startCenter: center,
            startRadius: 0,
            endCenter: center,
            endRadius: CGFloat(size) * 0.45,
            options: []
        )
    }

    // Ring
    let ringCenter = CGPoint(x: CGFloat(size) / 2, y: CGFloat(size) / 2)
    let ringRadius = CGFloat(size) * 0.275
    let ringWidth: CGFloat = CGFloat(size) * 0.035
    ctx.setStrokeColor(CGColor(red: 0.35, green: 0.55, blue: 1.0, alpha: 0.5))
    ctx.setLineWidth(ringWidth)
    ctx.addArc(
        center: ringCenter,
        radius: ringRadius,
        startAngle: 0,
        endAngle: .pi * 2,
        clockwise: false
    )
    ctx.strokePath()

    // "A" brand mark top-left
    #if canImport(AppKit)
        let fontSize = CGFloat(size) * 0.10
        let attrs: [NSAttributedString.Key: Any] = [
            .font: NSFont.systemFont(ofSize: fontSize, weight: .bold),
            .foregroundColor: NSColor(
                red: 0.45, green: 0.65, blue: 1.0, alpha: 0.5),
        ]
        let attrStr = NSAttributedString(string: "A", attributes: attrs)
        let line = CTLineCreateWithAttributedString(attrStr)
        let textBounds = CTLineGetBoundsWithOptions(line, [])

        ctx.saveGState()
        // Flip for text rendering
        ctx.textMatrix = CGAffineTransform(
            a: 1, b: 0, c: 0, d: 1, tx: 0, ty: 0)
        let xPos = CGFloat(size) * 0.17 - textBounds.width / 2
        let yPos = CGFloat(size) * 0.80  // CG coords are bottom-up
        ctx.textPosition = CGPoint(x: xPos, y: yPos)
        CTLineDraw(line, ctx)
        ctx.restoreGState()
    #endif

    // Center cross/sparkle pattern (geometric, since we can't use SF Symbols in CG)
    let cx = CGFloat(size) / 2
    let cy = CGFloat(size) / 2
    let starSize = CGFloat(size) * 0.15

    ctx.setFillColor(CGColor(red: 0.50, green: 0.65, blue: 1.0, alpha: 0.9))

    // 4-pointed star via two overlapping diamond shapes
    for angle in [0.0, .pi / 4] as [CGFloat] {
        ctx.saveGState()
        ctx.translateBy(x: cx, y: cy)
        ctx.rotate(by: angle)

        let path = CGMutablePath()
        path.move(to: CGPoint(x: 0, y: -starSize))
        path.addLine(to: CGPoint(x: starSize * 0.15, y: 0))
        path.addLine(to: CGPoint(x: 0, y: starSize))
        path.addLine(to: CGPoint(x: -starSize * 0.15, y: 0))
        path.closeSubpath()
        ctx.addPath(path)
        ctx.fillPath()

        let path2 = CGMutablePath()
        path2.move(to: CGPoint(x: -starSize, y: 0))
        path2.addLine(to: CGPoint(x: 0, y: starSize * 0.15))
        path2.addLine(to: CGPoint(x: starSize, y: 0))
        path2.addLine(to: CGPoint(x: 0, y: -starSize * 0.15))
        path2.closeSubpath()
        ctx.addPath(path2)
        ctx.fillPath()

        ctx.restoreGState()
    }

    // Small accent dots (representing secondary sparkle points)
    let dotRadius: CGFloat = CGFloat(size) * 0.015
    let dotOffset = starSize * 0.75
    ctx.setFillColor(
        CGColor(red: 0.65, green: 0.55, blue: 1.0, alpha: 0.6))
    for (dx, dy) in [
        (dotOffset, -dotOffset), (-dotOffset, dotOffset),
        (dotOffset, dotOffset), (-dotOffset, -dotOffset),
    ] {
        ctx.fillEllipse(
            in: CGRect(
                x: cx + dx - dotRadius,
                y: cy + dy - dotRadius,
                width: dotRadius * 2,
                height: dotRadius * 2
            )
        )
    }

    guard let cgImage = ctx.makeImage() else {
        print("ERROR: Failed to create CGImage")
        return nil
    }

    #if canImport(AppKit)
        let nsImage = NSImage(cgImage: cgImage, size: NSSize(width: size, height: size))
        guard let tiffData = nsImage.tiffRepresentation,
              let bitmapRep = NSBitmapImageRep(data: tiffData),
              let pngData = bitmapRep.representation(using: .png, properties: [:])
        else {
            print("ERROR: Failed to create PNG data")
            return nil
        }
        return pngData
    #else
        print("ERROR: AppKit not available. Run on macOS.")
        return nil
    #endif
}

// Main
let outputDir =
    "app/AXIOMMobile/AXIOMMobile/Assets.xcassets/AppIcon.appiconset"

guard let pngData = createIcon() else {
    print("Failed to generate icon.")
    exit(1)
}

let outputPath = "\(outputDir)/AppIcon.png"
let outputDarkPath = "\(outputDir)/AppIcon-Dark.png"
let outputTintedPath = "\(outputDir)/AppIcon-Tinted.png"

do {
    try pngData.write(to: URL(fileURLWithPath: outputPath))
    // Use the same icon for all variants (dark and tinted)
    try pngData.write(to: URL(fileURLWithPath: outputDarkPath))
    try pngData.write(to: URL(fileURLWithPath: outputTintedPath))
    print("App icon exported to \(outputPath)")
    print("Dark variant exported to \(outputDarkPath)")
    print("Tinted variant exported to \(outputTintedPath)")
} catch {
    print("ERROR: \(error)")
    exit(1)
}
