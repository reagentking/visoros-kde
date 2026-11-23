// SPDX-License-Identifier: GPL-3.0-or-later
import QtQuick
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Kirigami.FormLayout {
    property alias cfg_warnAt: warn.value
    QQC2.SpinBox {
        id: warn
        Kirigami.FormData.label: "Warn (amber) at:"
        from: 10; to: 100; stepSize: 5
        textFromValue: (v) => v + "%"
    }
}
