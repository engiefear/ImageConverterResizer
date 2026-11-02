from pathlib import Path

ROOT = Path('GameHelper2/Plugins/StashUtility')
core_path = ROOT / 'StashUtilityCore.cs'
c = core_path.read_text(encoding='utf-8')

# Strong visual separation between the three managers.
sections = [
    (
        '            ImGui.Checkbox(PluginText.T("stashutility.enable_waystone_manager", "Enable Waystone Manager"), ref Settings.EnableWaystoneManager);\n',
        '''            ImGui.Spacing();\n            ImGui.Spacing();\n            ImGui.PushStyleColor(ImGuiCol.Text, new Vector4(0.15f, 0.85f, 1.00f, 1.00f));\n            ImGui.SeparatorText("WAYSTONES");\n            ImGui.PopStyleColor();\n            ImGui.TextDisabled("Ordered profiles — first matching profile wins");\n\n'''
    ),
    (
        '            ImGui.Checkbox(PluginText.T("stashutility.enable_tablet_manager", "Enable Tablet Manager"), ref Settings.EnableTabletManager);\n',
        '''            ImGui.Spacing();\n            ImGui.Spacing();\n            ImGui.PushStyleColor(ImGuiCol.Text, new Vector4(0.90f, 0.35f, 1.00f, 1.00f));\n            ImGui.SeparatorText("TABLETS");\n            ImGui.PopStyleColor();\n            ImGui.TextDisabled("Profiles + JSON import from profiles/tablets");\n\n'''
    ),
    (
        '            ImGui.Checkbox(PluginText.T("stashutility.enable_jewel_manager", "Enable Jewel Manager"), ref Settings.EnableJewelManager);\n',
        '''            ImGui.Spacing();\n            ImGui.Spacing();\n            ImGui.PushStyleColor(ImGuiCol.Text, new Vector4(0.25f, 1.00f, 0.45f, 1.00f));\n            ImGui.SeparatorText("JEWELS");\n            ImGui.PopStyleColor();\n            ImGui.TextDisabled("Jewel groups + JSON profile packs");\n\n'''
    ),
]

for anchor, banner in sections:
    if banner not in c:
        if anchor not in c:
            raise RuntimeError(f'Could not find UI section anchor: {anchor.strip()}')
        c = c.replace(anchor, banner + anchor, 1)

# Make Tablet import self-explanatory and useful even when the folder is empty.
old = '''        private void DrawTabletPackUI()\n        {\n            if (profilePackService == null) return;\n            if (ImGui.SmallButton("Export Tablet Pack")) { try { profilePackService.ExportTablets("tablets-export", Settings.TabletProfiles); profilePackStatus="Tablet pack exported"; } catch(Exception ex){ profilePackStatus=ex.Message; } }\n            var files=profilePackService.ListTabletPacks(); if(files.Count==0)return; selectedTabletPackIndex=Math.Clamp(selectedTabletPackIndex,0,files.Count-1); ImGui.SameLine(); ImGui.SetNextItemWidth(260f); if(ImGui.BeginCombo("##tabletPack",files[selectedTabletPackIndex])){for(int i=0;i<files.Count;i++)if(ImGui.Selectable(files[i],i==selectedTabletPackIndex))selectedTabletPackIndex=i;ImGui.EndCombo();} ImGui.SameLine(); if(ImGui.SmallButton("Load Tablet Pack")){try{var pack=profilePackService.ImportTablets(files[selectedTabletPackIndex]);Settings.TabletProfiles=pack.Profiles;foreach(var t in StashUtilitySettings.TabletTypes)if(!Settings.TabletProfiles.ContainsKey(t))Settings.TabletProfiles[t]=new TabletProfile();SaveSettings();profilePackStatus="Tablet pack loaded";}catch(Exception ex){profilePackStatus=ex.Message;}}\n        }\n'''
new = '''        private void DrawTabletPackUI()\n        {\n            if (profilePackService == null) return;\n            ImGui.TextDisabled("Drop *.json into: profiles/tablets — the list refreshes automatically");\n            if (ImGui.SmallButton("Export Tablet Pack"))\n            {\n                try\n                {\n                    var path = profilePackService.ExportTablets("tablets-export", Settings.TabletProfiles);\n                    profilePackStatus = "Tablet pack exported: " + path;\n                }\n                catch (Exception ex) { profilePackStatus = ex.Message; }\n            }\n\n            var files = profilePackService.ListTabletPacks();\n            if (files.Count == 0)\n            {\n                ImGui.SameLine();\n                ImGui.TextDisabled("No tablet profile JSON files found");\n                return;\n            }\n\n            selectedTabletPackIndex = Math.Clamp(selectedTabletPackIndex, 0, files.Count - 1);\n            ImGui.SameLine();\n            ImGui.SetNextItemWidth(300f);\n            if (ImGui.BeginCombo("##tabletPack", files[selectedTabletPackIndex]))\n            {\n                for (int i = 0; i < files.Count; i++)\n                    if (ImGui.Selectable(files[i], i == selectedTabletPackIndex)) selectedTabletPackIndex = i;\n                ImGui.EndCombo();\n            }\n            ImGui.SameLine();\n            if (ImGui.SmallButton("Load Tablet Pack"))\n            {\n                try\n                {\n                    var pack = profilePackService.ImportTablets(files[selectedTabletPackIndex]);\n                    Settings.TabletProfiles = pack.Profiles;\n                    foreach (var t in StashUtilitySettings.TabletTypes)\n                        if (!Settings.TabletProfiles.ContainsKey(t)) Settings.TabletProfiles[t] = new TabletProfile();\n                    SaveSettings();\n                    profilePackStatus = "Tablet pack loaded: " + pack.Name;\n                }\n                catch (Exception ex) { profilePackStatus = ex.Message; }\n            }\n        }\n'''
if old in c:
    c = c.replace(old, new, 1)
elif 'Drop *.json into: profiles/tablets' not in c:
    raise RuntimeError('Could not locate DrawTabletPackUI implementation')

core_path.write_text(c, encoding='utf-8')
print('v2 UI/tablet import patch applied')
