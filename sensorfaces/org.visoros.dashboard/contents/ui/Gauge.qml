/*
    One dashboard gauge: a 180° arc, a big readout and a mono label.
    Turns amber (plus a ▲ in the label) past the warn threshold.
    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick
import QtQuick.Shapes
import org.kde.kirigami as Kirigami
import org.kde.ksysguard.sensors as Sensors

Item {
    id: gauge
    property alias sensorId: sensor.sensorId
    property int updateRateLimit: 0
    property int warnAt: 85
    property bool compact: false

    Sensors.Sensor {
        id: sensor
        updateRateLimit: gauge.updateRateLimit
    }

    // Percent sensors report max 0 or 100; fall back to 100.
    readonly property real range: sensor.maximum > sensor.minimum ? sensor.maximum - sensor.minimum : 100
    readonly property real fraction: Math.max(0, Math.min(1, (Number(sensor.value) - sensor.minimum) / range))
    readonly property bool warning: fraction * 100 >= warnAt
    // "cpu/all/usage" -> "CPU · USAGE" so two "Usage" gauges stay distinguishable
    readonly property string source: ({ cpu: "CPU", gpu: "GPU", memory: "RAM", disk: "DISK", network: "NET", power: "PWR", lmsensors: "SENSOR" })[String(sensorId).split("/")[0]] || String(sensorId).split("/")[0].toUpperCase()
    readonly property string label: source + " · " + (sensor.shortName || sensor.name).toUpperCase()
    readonly property color accent: warning ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.highlightColor

    readonly property real base: Math.min(width / 2, height * (compact ? 0.95 : 0.72))
    readonly property real stroke: Math.max(3, Math.round(base * 0.12))
    readonly property real r: Math.max(8, base - stroke)
    readonly property real cx: width / 2
    readonly property real cy: compact ? height - stroke : r + stroke

    Shape {
        anchors.fill: parent
        preferredRendererType: Shape.CurveRenderer
        ShapePath {
            fillColor: "transparent"
            strokeColor: Qt.alpha(Kirigami.Theme.textColor, 0.16)
            strokeWidth: gauge.stroke
            capStyle: ShapePath.FlatCap
            PathAngleArc { centerX: gauge.cx; centerY: gauge.cy; radiusX: gauge.r; radiusY: gauge.r; startAngle: 180; sweepAngle: 180 }
        }
        ShapePath {
            fillColor: "transparent"
            strokeColor: gauge.accent
            strokeWidth: gauge.stroke
            capStyle: ShapePath.FlatCap
            PathAngleArc { centerX: gauge.cx; centerY: gauge.cy; radiusX: gauge.r; radiusY: gauge.r; startAngle: 180; sweepAngle: 180 * gauge.fraction
                Behavior on sweepAngle { NumberAnimation { duration: 250; easing.type: Easing.OutCubic } }
            }
        }
    }

    Text {
        visible: !gauge.compact
        anchors.horizontalCenter: parent.horizontalCenter
        y: gauge.cy - height + gauge.r * 0.05
        text: sensor.formattedValue
        font.family: "Saira SemiCondensed"
        font.weight: Font.Bold
        font.pixelSize: Math.max(10, gauge.r * 0.46)
        color: Kirigami.Theme.textColor
    }
    Text {
        visible: !gauge.compact
        anchors.horizontalCenter: parent.horizontalCenter
        y: gauge.cy + gauge.stroke * 0.6
        text: (gauge.warning ? "▲ " : "") + gauge.label
        width: parent.width
        horizontalAlignment: Text.AlignHCenter
        elide: Text.ElideRight
        font.family: "Share Tech Mono"
        font.pixelSize: Math.max(8, gauge.r * 0.17)
        font.letterSpacing: 1.4
        color: gauge.warning ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.disabledTextColor
    }
}
