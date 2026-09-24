// Распознаёт текст на фото и в PDF встроенными средствами macOS (Vision, PDFKit): русский и английский.
// Использование:  ./ocr файл.jpg   или   ./ocr файл.pdf     — печатает текст в консоль.
// Собирается командой:  swiftc -O ocr.swift -o ocr   (приложение делает это само, если файла ocr нет).
import Vision
import AppKit
import PDFKit
import ImageIO

func recognize(_ image: CGImage, _ orientation: CGImagePropertyOrientation = .up) -> String {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["ru-RU", "en-US"]
    request.usesLanguageCorrection = true
    let handler = VNImageRequestHandler(cgImage: image, orientation: orientation, options: [:])
    try? handler.perform([request])
    return (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
}

let args = CommandLine.arguments
guard args.count > 1 else {
    FileHandle.standardError.write("нужен путь к файлу\n".data(using: .utf8)!)
    exit(1)
}
let url = URL(fileURLWithPath: args[1])

if url.pathExtension.lowercased() == "pdf" {
    guard let doc = PDFDocument(url: url) else {
        FileHandle.standardError.write("не удалось открыть PDF\n".data(using: .utf8)!)
        exit(2)
    }
    var pages: [String] = []
    for i in 0..<min(doc.pageCount, 20) {                       // не больше 20 страниц
        guard let page = doc.page(at: i) else { continue }
        let text = (page.string ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        if text.count > 80 { pages.append(text); continue }      // у страницы есть свой текст — берём его
        let box = page.bounds(for: .mediaBox)                    // иначе это скан: распознаём как картинку
        let scale = 2000 / max(box.width, box.height)
        let img = page.thumbnail(of: NSSize(width: box.width * scale, height: box.height * scale), for: .mediaBox)
        if let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) { pages.append(recognize(cg)) }
    }
    print(pages.joined(separator: "\n\n"))
} else {
    guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
          let cg = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        FileHandle.standardError.write("не удалось открыть картинку\n".data(using: .utf8)!)
        exit(2)
    }
    var orientation = CGImagePropertyOrientation.up              // телефон мог снять «боком» — учитываем поворот
    if let props = CGImageSourceCopyPropertiesAtIndex(src, 0, nil) as? [CFString: Any],
       let raw = props[kCGImagePropertyOrientation] as? UInt32,
       let o = CGImagePropertyOrientation(rawValue: raw) { orientation = o }
    print(recognize(cg, orientation))
}
