/*
    VisorOS Dashboard (full): a row of arc gauges for the main sensors, then
    segmented bars for the secondary sensors, like a vehicle dashboard.
    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.ksysguard.sensors as Sensors
import org.kde.ksysguard.faces as Faces

Faces.SensorFace {
    id: root
    readonly property int warnAt: controller.faceConfiguration.warnAt || 85

    Layout.minimumWidth: Kirigami.Units.gridUnit * 10
    Layout.preferredWidth: Kirigami.Units.gridUnit * 18
    Layout.minimumHeight: Kirigami.Units.gridUnit * 7

    contentItem: ColumnLayout {
        spacing: Kirigami.Units.largeSpacing

        Text {
            Layout.fillWidth: true
            visible: root.controller.showTitle && text.length > 0
            text: (root.controller.title || "").toUpperCase()
            font.family: "Saira SemiCondensed"
            font.weight: Font.Medium
            font.pixelSize: Kirigami.Units.gridUnit * 0.9
            font.letterSpacing: 2
            color: Kirigami.Theme.textColor
            elide: Text.ElideRight
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: Kirigami.Units.gridUnit * 4
            spacing: Kirigami.Units.largeSpacing
            Repeater {
                model: root.controller.highPrioritySensorIds
                Gauge {
                    required property string modelData
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    sensorId: modelData
                    warnAt: root.warnAt
                    updateRateLimit: root.controller.updateRateLimit
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 1
            visible: root.controller.lowPrioritySensorIds.length > 0
            color: Qt.alpha(Kirigami.Theme.textColor, 0.16)
        }

        Repeater {
            model: root.controller.lowPrioritySensorIds
            RowLayout {
                id: row
                required property string modelData
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing

                Sensors.Sensor { id: s; sensorId: row.modelData; updateRateLimit: root.controller.updateRateLimit }
                readonly property real range: s.maximum > s.minimum ? s.maximum - s.minimum : 100
                readonly property real fraction: Math.max(0, Math.min(1, (Number(s.value) - s.minimum) / range))
                readonly property int segments: 12

                Text {
                    Layout.preferredWidth: Kirigami.Units.gridUnit * 5
                    text: (s.shortName || s.name).toUpperCase()
                    elide: Text.ElideRight
                    font.family: "Share Tech Mono"
                    font.pixelSize: Kirigami.Units.gridUnit * 0.62
                    font.letterSpacing: 1.2
                    color: Kirigami.Theme.disabledTextColor
                }
                Row {
                    Layout.fillWidth: true
                    spacing: 2
                    Repeater {
                        model: row.segments
                        Rectangle {
                            width: (parent.width - 2 * (row.segments - 1)) / row.segments
                            height: Kirigami.Units.gridUnit * 0.5
                            readonly property bool on: index < Math.round(row.fraction * row.segments)
                            color: on ? (row.fraction * 100 >= root.warnAt ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.highlightColor)
                                      : Qt.alpha(Kirigami.Theme.textColor, 0.14)
                        }
                    }
                }
                Text {
                    Layout.preferredWidth: Kirigami.Units.gridUnit * 4
                    horizontalAlignment: Text.AlignRight
                    text: s.formattedValue
                    font.family: "Share Tech Mono"
                    font.pixelSize: Kirigami.Units.gridUnit * 0.68
                    color: Kirigami.Theme.textColor
                }
            }
        }
    }
}
