// Apply AmogOS desktop defaults once while preserving valid taskbar launchers.
var amogosMusic = "applications:amogos.music.desktop";
var amogosDefaults = ["applications:org.kde.dolphin.desktop", "applications:firefox-esr.desktop", amogosMusic];
var amogosPanels = panels();
for (var p = 0; p < amogosPanels.length; p++) {
    var widgets = amogosPanels[p].widgets();
    for (var w = 0; w < widgets.length; w++) {
        var widget = widgets[w];
        if (widget.type !== "org.kde.plasma.icontasks" && widget.type !== "org.kde.plasma.taskmanager") continue;
        widget.currentConfigGroup = ["General"];
        var current = widget.readConfig("launchers", amogosDefaults);
        var pins = typeof current === "string" ? current.split(",") : current;
        var clean = [];
        for (var i = 0; i < pins.length; i++) {
            if (pins[i] && pins[i] !== "applications:systemsettings.desktop" && pins[i] !== "applications:org.kde.discover.desktop" && clean.indexOf(pins[i]) === -1) clean.push(pins[i]);
        }
        if (clean.indexOf(amogosMusic) === -1) clean.push(amogosMusic);
        widget.writeConfig("launchers", clean);
        widget.reloadConfig();
    }
}
var amogosDesktops = desktops();
for (var d = 0; d < amogosDesktops.length; d++) {
    amogosDesktops[d].wallpaperPlugin = "org.kde.image";
    amogosDesktops[d].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    amogosDesktops[d].writeConfig("Image", "file:///usr/share/wallpapers/AmogOSEngine/img1.png");
    amogosDesktops[d].reloadConfig();
}
