// Replace application-menu branding once without changing the menu or panel layout.
var amogosMenuPanels = panels();
for (var p = 0; p < amogosMenuPanels.length; p++) {
    var widgets = amogosMenuPanels[p].widgets();
    for (var w = 0; w < widgets.length; w++) {
        var menu = widgets[w];
        if (menu.type !== "org.kde.plasma.kickoff") continue;
        menu.currentConfigGroup = ["General"];
        menu.writeConfig("icon", "/usr/share/pixmaps/amogos-menu.png");
        menu.reloadConfig();
    }
}
