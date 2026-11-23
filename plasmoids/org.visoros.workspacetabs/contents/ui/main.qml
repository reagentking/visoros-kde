/*
    Workspace Tabs (VisorOS): virtual desktops drawn as front-end menu tabs.

      [1]  2   3        active = solid light chip, cut top-right corner, dark number
       ·   ·            small square under a tab = desktop has windows

    Click to switch, scroll to cycle, right-click to add/remove desktops.
    Stacks vertically when the panel is on a side edge.
    Desktop changes go through KWin's D-Bus API (org.kde.plasma.workspace.dbus).

    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick
import QtQuick.Layouts
import QtQuick.Shapes
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import org.kde.taskmanager as TaskManager
import org.kde.plasma.workspace.dbus as DBus

PlasmoidItem {
    id: root

    preferredRepresentation: fullRepresentation
    readonly property bool vertical: Plasmoid.formFactor === PlasmaCore.Types.Vertical

    TaskManager.VirtualDesktopInfo { id: vdi }

    // ---------------------------------------------------------------- occupancy
    TaskManager.TasksModel {
        id: tasks
        filterByVirtualDesktop: false
        filterByScreen: false
        groupMode: TaskManager.TasksModel.GroupDisabled
        onCountChanged: refreshTimer.restart()
        onDataChanged: refreshTimer.restart()
    }
    property var occupied: ({})
    Timer {
        id: refreshTimer
        interval: 150
        onTriggered: {
            const occ = {};
            for (let i = 0; i < tasks.count; ++i) {
                const idx = tasks.makeModelIndex(i);
                if (tasks.data(idx, TaskManager.AbstractTasksModel.IsOnAllVirtualDesktops)) continue;
                const ds = tasks.data(idx, TaskManager.AbstractTasksModel.VirtualDesktops) || [];
                for (const d of ds) occ[d] = true;
            }
            root.occupied = occ;
        }
    }
    Component.onCompleted: refreshTimer.start()
    Connections {
        target: vdi
        function onDesktopIdsChanged() { refreshTimer.restart() }
    }

    // ---------------------------------------------------------------- KWin calls
    function kwin(path, iface, member, args, signature) {
        DBus.SessionBus.asyncCall({ service: "org.kde.KWin", path: path, iface: iface, member: member,
                                    arguments: args, signature: signature },
                                  () => {}, (e) => console.warn("workspacetabs:", member, e.message));
    }
    function activate(index) {
        kwin("/KWin", "org.kde.KWin", "setCurrentDesktop", [new DBus.int32(index + 1)], "(i)");
    }
    function addDesktop() {
        const n = vdi.numberOfDesktops;
        kwin("/VirtualDesktopManager", "org.kde.KWin.VirtualDesktopManager", "createDesktop",
             [new DBus.uint32(n), new DBus.string("Desktop " + (n + 1))], "(us)");
    }
    function removeLastDesktop() {
        const n = vdi.numberOfDesktops;
        if (n > 1)
            kwin("/VirtualDesktopManager", "org.kde.KWin.VirtualDesktopManager", "removeDesktop",
                 [new DBus.string(String(vdi.desktopIds[n - 1]))], "(s)");
    }
    function cycle(step) {
        const n = vdi.numberOfDesktops;
        const cur = vdi.desktopIds.indexOf(vdi.currentDesktop);
        activate(((cur + step) % n + n) % n);
    }

    Plasmoid.contextualActions: [
        PlasmaCore.Action {
            text: "Add Virtual Desktop"
            icon.name: "list-add"
            onTriggered: root.addDesktop()
        },
        PlasmaCore.Action {
            text: "Remove Last Virtual Desktop"
            icon.name: "list-remove"
            enabled: vdi.numberOfDesktops > 1
            onTriggered: root.removeLastDesktop()
        }
    ]

    // ---------------------------------------------------------------- view
    fullRepresentation: Item {
        id: view
        readonly property real thickness: root.vertical ? width : height
        readonly property real cell: Math.max(Kirigami.Units.iconSizes.small, Math.round(thickness * 0.64))
        readonly property real gap: Math.round(cell * 0.22)

        Layout.minimumWidth: root.vertical ? cell : grid.implicitWidth
        Layout.preferredWidth: Layout.minimumWidth
        Layout.minimumHeight: root.vertical ? grid.implicitHeight : cell
        Layout.preferredHeight: Layout.minimumHeight

        GridLayout {
            id: grid
            anchors.centerIn: parent
            flow: root.vertical ? GridLayout.TopToBottom : GridLayout.LeftToRight
            rows: root.vertical ? -1 : 1
            columns: root.vertical ? 1 : -1
            rowSpacing: view.gap
            columnSpacing: view.gap

            Repeater {
                model: vdi.desktopIds

                delegate: Item {
                    id: tab
                    required property var modelData
                    required property int index
                    readonly property bool active: modelData === vdi.currentDesktop
                    readonly property bool busy: root.occupied[modelData] === true
                    readonly property real chamfer: Math.round(view.cell * 0.28)

                    Layout.preferredWidth: view.cell
                    Layout.preferredHeight: view.cell

                    // inactive: hairline outline, faint fill on hover
                    Rectangle {
                        anchors.fill: parent
                        visible: !tab.active
                        color: hover.hovered ? Qt.alpha(Kirigami.Theme.highlightColor, 0.14) : "transparent"
                        border.width: 1
                        border.color: Qt.alpha(Kirigami.Theme.textColor, hover.hovered ? 0.45 : 0.22)
                    }

                    // active: solid light chip with one cut corner
                    Shape {
                        anchors.fill: parent
                        visible: tab.active
                        preferredRendererType: Shape.CurveRenderer
                        ShapePath {
                            strokeWidth: 0
                            strokeColor: "transparent"
                            fillColor: Kirigami.Theme.highlightColor
                            startX: 0; startY: 0
                            PathLine { x: tab.width - tab.chamfer; y: 0 }
                            PathLine { x: tab.width; y: tab.chamfer }
                            PathLine { x: tab.width; y: tab.height }
                            PathLine { x: 0; y: tab.height }
                            PathLine { x: 0; y: 0 }
                        }
                    }

                    Text {
                        anchors.centerIn: parent
                        anchors.verticalCenterOffset: -Math.round(view.cell * 0.07)
                        text: tab.index + 1
                        font.family: "Saira SemiCondensed"
                        font.weight: tab.active ? Font.Bold : Font.Medium
                        font.pixelSize: Math.round(view.cell * 0.56)
                        color: tab.active ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.textColor
                        opacity: tab.active ? 1 : 0.75
                    }

                    // occupied marker
                    Rectangle {
                        visible: tab.busy
                        width: Math.max(2, Math.round(view.cell * 0.12)); height: width
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: Math.round(view.cell * 0.09)
                        color: tab.active ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.textColor
                        opacity: tab.active ? 0.8 : 0.6
                    }

                    HoverHandler { id: hover }
                    TapHandler { onTapped: root.activate(tab.index) }
                    PlasmaCore.ToolTipArea {
                        anchors.fill: parent
                        mainText: vdi.desktopNames[tab.index] || ("Desktop " + (tab.index + 1))
                        subText: tab.busy ? "Has open windows" : "Empty"
                    }
                }
            }
        }

        WheelHandler {
            property real acc: 0
            onWheel: (event) => {
                acc += event.angleDelta.y || event.angleDelta.x;
                if (Math.abs(acc) >= 120) { root.cycle(acc > 0 ? -1 : 1); acc = 0; }
            }
        }
    }
}
