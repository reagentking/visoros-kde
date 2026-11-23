/*
    VisorOS OSD body.

    Progress mode  (volume, brightness, mic):        Text mode (wi-fi, layout, desktop):
    ┌──────────────────────────────┐                 ┌──────────────────────────────┐
    │ AUDIO OUT                64  │                 │ SYSTEM                       │
    │ SPEAKERS               [icon]│                 │ [icon]  WI-FI ENABLED        │
    │ ▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▯▯▯▯▯▯▯▯▯     │                 │                              │
    └──────────────────────────────┘                 └──────────────────────────────┘
    Rounds beyond 100% (over-amplified volume) are drawn amber.

    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: item

    // Same interface as Plasma's own OsdItem (plasma-workspace 6.8)
    property int timeout: 1800
    property var osdValue
    property int osdMaxValue: 100
    property string osdAdditionalText: ""
    property string icon
    property bool showingProgress: false
    readonly property QtObject rootItem: item

    readonly property real maxValue: Math.max(1, rootItem.osdMaxValue || 100)
    readonly property real value: Number(rootItem.osdValue) || 0
    readonly property int rounds: 25
    readonly property int lit: Math.round(Math.min(value, maxValue) / maxValue * rounds)
    // index of the first round that represents >100%
    readonly property int overStart: maxValue > 100 ? Math.round(100 / maxValue * rounds) : rounds

    readonly property string displayFont: "Saira SemiCondensed"
    readonly property string monoFont: "Share Tech Mono"

    // Front-end label derived from the icon the OSD was asked to show.
    readonly property string kind: {
        const i = rootItem.icon || "";
        if (i.startsWith("audio-volume") || i.startsWith("player-volume")) return "AUDIO OUT";
        if (i.startsWith("microphone") || i.indexOf("mic") >= 0) return "MIC IN";
        if (i.indexOf("keyboard-brightness") >= 0) return "KEYBOARD";
        if (i.indexOf("brightness") >= 0 || i.indexOf("display") >= 0) return "DISPLAY";
        if (i.indexOf("battery") >= 0) return "POWER";
        return "SYSTEM";
    }

    implicitWidth: Kirigami.Units.gridUnit * 17
    implicitHeight: showingProgress ? Kirigami.Units.gridUnit * 6.5 : Kirigami.Units.gridUnit * 4.5

    // ---- header labels
    Column {
        id: labels
        anchors { left: parent.left; top: parent.top; leftMargin: Kirigami.Units.smallSpacing; topMargin: Kirigami.Units.smallSpacing }
        spacing: 2
        Text {
            text: item.kind
            font.family: item.monoFont
            font.pixelSize: Kirigami.Units.gridUnit * 0.62
            font.letterSpacing: 1.6
            color: Kirigami.Theme.highlightColor
            opacity: 0.9
        }
        Text {
            visible: text.length > 0
            text: (rootItem.osdAdditionalText || "").toUpperCase()
            width: item.width * 0.6
            elide: Text.ElideRight
            font.family: item.monoFont
            font.pixelSize: Kirigami.Units.gridUnit * 0.55
            font.letterSpacing: 1.4
            color: Kirigami.Theme.disabledTextColor
        }
    }

    // ---- progress mode: big counter + rounds
    Text {
        id: counter
        visible: rootItem.showingProgress
        anchors { right: parent.right; top: parent.top; rightMargin: Kirigami.Units.smallSpacing; topMargin: -Kirigami.Units.gridUnit * 0.35 }
        text: Math.round(item.value)
        font.family: item.displayFont
        font.weight: Font.Bold
        font.pixelSize: Kirigami.Units.gridUnit * 3.4
        color: item.value > 100 ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.textColor
    }

    Kirigami.Icon {
        visible: rootItem.showingProgress
        anchors { left: parent.left; leftMargin: Kirigami.Units.smallSpacing; verticalCenter: counter.verticalCenter; verticalCenterOffset: Kirigami.Units.gridUnit * 0.4 }
        width: Kirigami.Units.iconSizes.smallMedium
        height: width
        source: rootItem.icon
        isMask: true
        color: Kirigami.Theme.textColor
    }

    Row {
        id: roundsRow
        visible: rootItem.showingProgress
        anchors { left: parent.left; right: parent.right; bottom: parent.bottom; margins: Kirigami.Units.smallSpacing }
        height: Kirigami.Units.gridUnit * 0.95
        spacing: Math.max(2, Math.round(Kirigami.Units.gridUnit * 0.14))
        readonly property real roundWidth: (width - spacing * (item.rounds - 1)) / item.rounds

        Repeater {
            model: item.rounds
            Rectangle {
                width: roundsRow.roundWidth
                height: roundsRow.height
                radius: 0
                readonly property bool on: index < item.lit
                color: !on ? Kirigami.Theme.textColor
                     : (index >= item.overStart ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.textColor)
                opacity: on ? 1.0 : 0.16
                Behavior on opacity { NumberAnimation { duration: 90 } }
            }
        }
    }

    // ---- text mode: icon + message
    RowLayout {
        visible: !rootItem.showingProgress
        anchors { left: parent.left; right: parent.right; bottom: parent.bottom; margins: Kirigami.Units.smallSpacing }
        spacing: Kirigami.Units.largeSpacing
        Kirigami.Icon {
            Layout.preferredWidth: Kirigami.Units.iconSizes.medium
            Layout.preferredHeight: Kirigami.Units.iconSizes.medium
            source: rootItem.icon
            isMask: true
            color: Kirigami.Theme.textColor
        }
        Text {
            Layout.fillWidth: true
            text: String(rootItem.osdValue || "").toUpperCase()
            elide: Text.ElideRight
            maximumLineCount: 2
            wrapMode: Text.WordWrap
            font.family: item.displayFont
            font.weight: Font.DemiBold
            font.pixelSize: Kirigami.Units.gridUnit * 1.2
            font.letterSpacing: 1.2
            color: Kirigami.Theme.textColor
        }
    }
}
