/*
    VisorOS Dashboard (compact, for panels): small arcs only.
    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.ksysguard.faces as Faces

Faces.CompactSensorFace {
    id: root
    readonly property int warnAt: controller.faceConfiguration.warnAt || 85
    Layout.preferredWidth: horizontalFormFactor ? height * 1.4 * Math.max(1, controller.highPrioritySensorIds.length) : -1

    contentItem: GridLayout {
        flow: root.horizontalFormFactor ? GridLayout.LeftToRight : GridLayout.TopToBottom
        rows: root.horizontalFormFactor ? 1 : -1
        columns: root.horizontalFormFactor ? -1 : 1
        columnSpacing: Kirigami.Units.smallSpacing
        rowSpacing: Kirigami.Units.smallSpacing
        Repeater {
            model: root.controller.highPrioritySensorIds
            Gauge {
                required property string modelData
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumWidth: Kirigami.Units.gridUnit
                Layout.minimumHeight: Kirigami.Units.gridUnit * 0.7
                compact: true
                sensorId: modelData
                warnAt: root.warnAt
                updateRateLimit: root.controller.updateRateLimit
            }
        }
    }
}
