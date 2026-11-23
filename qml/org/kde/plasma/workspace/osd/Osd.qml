/*
    VisorOS OSD window: shadows org.kde.plasma.workspace.osd/Osd.qml.
    Loaded via QML_IMPORT_PATH set in a plasmashell systemd drop-in
    (see scripts/osd-override.sh). OsdWindow comes from Plasma's own plugin.
    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick
import org.kde.kirigami as Kirigami
import org.kde.plasma.workspace.osd

OsdWindow {
    property alias timeout: osd.timeout
    property alias osdValue: osd.osdValue
    property alias osdMaxValue: osd.osdMaxValue
    property alias osdAdditionalText: osd.osdAdditionalText
    property alias icon: osd.icon
    property alias showingProgress: osd.showingProgress

    width: mainItem.implicitWidth + leftPadding + rightPadding
    height: mainItem.implicitHeight + topPadding + bottomPadding

    mainItem: OsdItem {
        id: osd
    }
}
