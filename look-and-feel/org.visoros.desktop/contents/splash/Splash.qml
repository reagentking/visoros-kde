/*
    VisorOS splash: the back-end boot log.

      VISR OS // PLASMA 6 // CACHYOS
      [ OK ] kwin_wayland ................ COMPOSITOR
      [ OK ] plasmashell ................. SHELL
      [ .. ] restoring session_

                     V I S R   O S
                 ▮▮▮▮▮▮▮▮▮▮▯▯▯▯▯▯▯▯▯▯

    ksplash raises `stage` from 1 to 6 as the session starts; each stage
    turns one log line [ OK ] and fills its share of the progress segments.

    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick

Rectangle {
    id: root
    color: "#070b09"

    property int stage: 0

    readonly property color signal: "#6dff8f"
    readonly property color dim: "#2e7a45"
    readonly property string mono: "Share Tech Mono"
    readonly property string display: "Saira SemiCondensed"
    readonly property real u: Math.max(1, Math.min(width / 1920, height / 1080))

    // label shown for each stage; the line is "done" once stage passes it
    readonly property var steps: [
        ["kwin_wayland",   "COMPOSITOR"],
        ["plasmashell",    "SHELL"],
        ["kded6",          "SERVICES"],
        ["pipewire",       "AUDIO"],
        ["krunner",        "SEARCH"],
        ["session",        "RESTORED"]
    ]

    Column {
        id: log
        x: 48 * root.u
        y: 44 * root.u
        spacing: 8 * root.u

        Text {
            text: "VISR OS  //  PLASMA 6  //  CACHYOS"
            font.family: root.mono
            font.pixelSize: 15 * root.u
            font.letterSpacing: 2 * root.u
            color: root.signal
        }
        Item { width: 1; height: 6 * root.u }

        Repeater {
            model: root.steps.length
            Row {
                spacing: 10 * root.u
                readonly property bool done: root.stage > index + 1 || root.stage >= 6
                readonly property bool current: !done && root.stage === index + 1
                visible: done || current
                Text {
                    text: parent.done ? "[ OK ]" : "[ .. ]"
                    font.family: root.mono
                    font.pixelSize: 14 * root.u
                    color: parent.done ? root.dim : root.signal
                }
                Text {
                    text: root.steps[index][0] + " " + ".".repeat(Math.max(3, 26 - root.steps[index][0].length)) + " " + root.steps[index][1]
                    font.family: root.mono
                    font.pixelSize: 14 * root.u
                    color: root.signal
                    opacity: parent.done ? 0.85 : 1
                }
                Text {
                    visible: parent.current
                    text: "_"
                    font.family: root.mono
                    font.pixelSize: 14 * root.u
                    color: root.signal
                    SequentialAnimation on opacity {
                        loops: Animation.Infinite
                        NumberAnimation { to: 0; duration: 0 }
                        PauseAnimation { duration: 450 }
                        NumberAnimation { to: 1; duration: 0 }
                        PauseAnimation { duration: 450 }
                    }
                }
            }
        }
    }

    Column {
        anchors.centerIn: parent
        anchors.verticalCenterOffset: 40 * root.u
        spacing: 26 * root.u

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "VISR OS"
            font.family: root.display
            font.weight: Font.Bold
            font.pixelSize: 72 * root.u
            font.letterSpacing: 18 * root.u
            color: root.signal
        }

        Row {
            id: bar
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 5 * root.u
            readonly property int segments: 12
            readonly property int lit: Math.round(Math.min(root.stage, 6) / 6 * segments)
            Repeater {
                model: bar.segments
                Rectangle {
                    width: 34 * root.u
                    height: 9 * root.u
                    color: index < bar.lit ? root.signal : root.dim
                    opacity: index < bar.lit ? 1 : 0.45
                    Behavior on opacity { NumberAnimation { duration: 200 } }
                }
            }
        }
    }

    Text {
        anchors { right: parent.right; bottom: parent.bottom; margins: 40 * root.u }
        text: "NODE 01  ·  " + Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm")
        font.family: root.mono
        font.pixelSize: 12 * root.u
        font.letterSpacing: 1.5 * root.u
        color: root.dim
    }
}
