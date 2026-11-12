import AppKit

final class MenuHelper: NSObject, NSApplicationDelegate {
    var item: NSStatusItem!
    var inside = false
    var timer: Timer?
    var announced = false
    var announcedNotch = false
    let parent = getppid()

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        guard let button = item.button else { exit(1) }
        button.image = NSImage(systemSymbolName: "checklist", accessibilityDescription: "Sticky Card")
        button.toolTip = "Sticky Card — hover to open, right-click to quit"
        button.target = self
        button.action = #selector(clicked(_:))
        button.sendAction(on: [.leftMouseUp, .rightMouseUp])
        timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in self?.poll() }
    }

    @objc func clicked(_ sender: Any?) {
        if NSApp.currentEvent?.type == .rightMouseUp {
            let menu = NSMenu()
            let quit = NSMenuItem(title: "Quit Sticky Card", action: #selector(quitApp), keyEquivalent: "")
            quit.target = self
            menu.addItem(quit)
            item.menu = menu
            item.button?.performClick(nil)
            item.menu = nil
        }
    }

    @objc func quitApp() { print("quit"); fflush(stdout); NSApp.terminate(nil) }

    func poll() {
        if getppid() != parent { NSApp.terminate(nil); return }
        guard let button = item.button, let window = button.window else { return }
        let rect = window.convertToScreen(button.convert(button.bounds, to: nil))
        if !announcedNotch, let screen = window.screen,
           let left = screen.auxiliaryTopLeftArea, let right = screen.auxiliaryTopRightArea {
            print("notch \(Int(left.maxX)) \(Int(right.minX))")
            fflush(stdout)
            announcedNotch = true
        }
        if !announced && rect.minY >= 0 && rect.minX >= 0 {
            let mainTop = NSScreen.screens.first?.frame.maxY ?? 0
            print("ready \(Int(rect.midX)) \(Int(mainTop - rect.midY))")
            fflush(stdout)
            announced = true
        }
        let hovered = rect.contains(NSEvent.mouseLocation)
        if hovered != inside {
            inside = hovered
            if hovered {
                let mainTop = NSScreen.screens.first?.frame.maxY ?? 0
                print("enter \(Int(rect.maxX)) \(Int(mainTop - rect.minY))")
            } else { print("leave") }
            fflush(stdout)
        }
    }
}

let app = NSApplication.shared
let delegate = MenuHelper()
app.delegate = delegate
app.run()
