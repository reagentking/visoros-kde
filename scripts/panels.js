// VisorOS panel layout (Plasma shell script; run through scripts/apply-panels.sh).
// Idempotent: reshapes the existing per-screen panels instead of recreating them,
// so pinned launchers and tray settings are kept.
//
//  Primary (screen 0):  launcher · tasks · ─ · workspace switcher · ─ · tray · clock
//  Others:              tasks · ─ · tray · clock      (launcher removed)
//  Every bar starts on the top edge; move any of them afterwards in Edit Mode.

function byType(ws, t) { return ws.filter(function (w) { return w.type === t; }); }
var removed = [];
function drop(w) { removed.push(w.id); w.remove(); }
function live(ws) { return ws.filter(function (w) { return removed.indexOf(w.id) < 0; }); }
function ids(ws) { return live(ws).map(function (w) { return w.id; }); }

var ps = panels();
for (var i = 0; i < ps.length; i++) {
    var p = ps[i];
    p.location = "top";
    var ws = p.widgets();
    var order = [];

    if (p.screen === 0) {
        var pager = byType(ws, "org.kde.plasma.pager")[0];
        if (!pager) pager = p.addWidget("org.kde.plasma.pager");
        pager.currentConfigGroup = ["General"];
        pager.writeConfig("displayedText", 0);        // show desktop numbers
        pager.writeConfig("showWindowIcons", false);

        var spacers = live(byType(p.widgets(), "org.kde.plasma.panelspacer"));
        while (spacers.length < 2) { spacers.push(p.addWidget("org.kde.plasma.panelspacer")); }
        for (var s = 2; s < spacers.length; s++) drop(spacers[s]);

        ws = p.widgets();
        var launchers = byType(ws, "org.kde.plasma.kickoff");
        var tasks = byType(ws, "org.kde.plasma.icontasks");
        var clock = byType(ws, "org.kde.plasma.digitalclock");
        var placed = ids(launchers).concat(ids(tasks), [spacers[0].id, pager.id, spacers[1].id], ids(clock));
        var rest = ws.filter(function (w) { return placed.indexOf(w.id) < 0; });
        order = ids(launchers).concat(ids(tasks), [spacers[0].id, pager.id, spacers[1].id], ids(rest), ids(clock));
    } else {
        byType(ws, "org.kde.plasma.kickoff").forEach(drop);
        byType(ws, "org.kde.plasma.pager").forEach(drop);
        var sp = live(byType(p.widgets(), "org.kde.plasma.panelspacer"));
        if (sp.length === 0) sp.push(p.addWidget("org.kde.plasma.panelspacer"));
        for (var t = 1; t < sp.length; t++) drop(sp[t]);

        ws = p.widgets();
        var tasks2 = byType(ws, "org.kde.plasma.icontasks");
        var clock2 = byType(ws, "org.kde.plasma.digitalclock");
        var fixed = ids(tasks2).concat([sp[0].id], ids(clock2));
        var rest2 = ws.filter(function (w) { return fixed.indexOf(w.id) < 0; });
        order = ids(tasks2).concat([sp[0].id], ids(rest2), ids(clock2));
    }

    // Plasma rewrites AppletOrder from memory on exit, so the shell wrapper
    // writes these lines into the config while plasmashell is stopped.
    print("ORDER " + p.id + " " + order.join(";") + "\n");
}
