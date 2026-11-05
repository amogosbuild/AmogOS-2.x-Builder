// Create the standard desktop using persistent AmogOS wallpaper and widget defaults.
if (panels().length === 0) loadTemplate("org.kde.plasma.desktop.defaultPanel");
var amogosProfileDesktops = desktopsForActivity(currentActivity());
for (var i = 0; i < amogosProfileDesktops.length; i++) {
    amogosProfileDesktops[i].wallpaperPlugin = "org.kde.image";
    amogosProfileDesktops[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    amogosProfileDesktops[i].writeConfig("Image", "file:///usr/share/wallpapers/AmogOSEngine/img1.png");
}
