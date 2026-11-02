from pathlib import Path
import shutil

ROOT = Path('GameHelper2/Plugins/StashUtility')
HARNESS = Path('harness/stashutility-ci')

for f in ['WaystoneProfile.cs','ProfilePackService.cs','DefaultWaystonePresets.cs']:
    src = HARNESS / f
    dst = ROOT / ('Models' if f == 'WaystoneProfile.cs' else 'ProfilePacks') / f
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

# ---------------- Settings ----------------
settings_path = ROOT / 'StashUtilitySettings.cs'
s = settings_path.read_text(encoding='utf-8')
anchor = '        // Debug Probe Mode\n'
insert = '''        // Ordered Waystone profile engine. List order is priority; first match wins.\n        public bool EnableWaystoneProfiles = true;\n        public List<StashUtility.Models.WaystoneProfile> WaystoneProfiles = new();\n\n'''
if insert not in s:
    assert anchor in s, 'settings anchor not found'
    s = s.replace(anchor, insert + anchor, 1)
settings_path.write_text(s, encoding='utf-8')

# ---------------- Core ----------------
core_path = ROOT / 'StashUtilityCore.cs'
c = core_path.read_text(encoding='utf-8')

field_anchor = '        private string tabletSearchTerm = string.Empty;\n'
field_insert = '''        private StashUtility.ProfilePacks.ProfilePackService profilePackService;\n        private string profilePackStatus = string.Empty;\n        private string waystonePackName = "my-waystones";\n        private int selectedWaystonePackIndex = 0;\n        private int selectedTabletPackIndex = 0;\n        private int selectedJewelPackIndex = 0;\n'''
if field_insert not in c:
    assert field_anchor in c, 'field anchor not found'
    c = c.replace(field_anchor, field_anchor + field_insert, 1)

# initialize pack folders / profile list
init_anchor = '            InitReflection();\n'
init_insert = '''            Settings.WaystoneProfiles ??= new List<StashUtility.Models.WaystoneProfile>();\n            profilePackService = new StashUtility.ProfilePacks.ProfilePackService(DllDirectory);\n\n'''
if init_insert not in c:
    assert init_anchor in c, 'OnEnable anchor not found'
    c = c.replace(init_anchor, init_insert + init_anchor, 1)

# Show profile UI and hide legacy Waystone editor while profile mode is enabled.
ui_anchor = '''            if (Settings.EnableWaystoneManager)\n            {\n                ImGui.Indent();\n'''
ui_repl = '''            if (Settings.EnableWaystoneManager && Settings.EnableWaystoneProfiles)\n            {\n                ImGui.Indent();\n                DrawWaystoneProfilesUI();\n                ImGui.Unindent();\n            }\n\n            if (Settings.EnableWaystoneManager && !Settings.EnableWaystoneProfiles)\n            {\n                ImGui.Indent();\n'''
if ui_repl not in c:
    assert ui_anchor in c, 'Waystone UI anchor not found'
    c = c.replace(ui_anchor, ui_repl, 1)

# Keep old global minimum only in legacy mode.
c = c.replace('                if (tier < Settings.MinTier) return;', '                if (!Settings.EnableWaystoneProfiles && tier < Settings.MinTier) return;', 1)

# Track matched Waystone mod IDs.
vars_anchor = '            int jewelGoodCount = 0;\n'
vars_insert = '            var presentWaystoneModIds = new HashSet<string>();\n'
if vars_insert not in c:
    assert vars_anchor in c, 'evaluation vars anchor not found'
    c = c.replace(vars_anchor, vars_anchor + vars_insert, 1)

waystone_def_anchor = '''                        if (def != null)\n                        {\n                            if (!hasMemoryStats)\n'''
waystone_def_repl = '''                        if (def != null)\n                        {\n                            presentWaystoneModIds.Add(def.Id);\n                            if (!hasMemoryStats)\n'''
if waystone_def_repl not in c:
    assert waystone_def_anchor in c, 'waystone mod match anchor not found'
    c = c.replace(waystone_def_anchor, waystone_def_repl, 1)

# Evaluate profile once all stats/mods have been collected. First match wins and returns,
# so legacy Waystone good/bad/great rendering cannot interfere.
profile_eval_anchor = '            bool passesNumericalFilters = true;\n'
profile_eval = '''            if (isWaystone && Settings.EnableWaystoneProfiles)\n            {\n                var snapshot = new StashUtility.Models.WaystoneSnapshot\n                {\n                    Tier = tier, Revives = revives, ExplicitMods = explicitModsCount,\n                    ItemRarity = sumRarity, PackSize = sumPackSize, MonsterRarity = sumMonstRarity,\n                    MonsterEffectiveness = sumEffect, WaystoneDropChance = sumDropChance\n                };\n                var matchedProfile = FindFirstMatchingWaystoneProfile(snapshot, presentWaystoneModIds);\n                if (matchedProfile == null) return;\n                DrawWaystoneProfileHighlight(matchedProfile, pos, size, rarity);\n                return;\n            }\n\n'''
if profile_eval not in c:
    assert profile_eval_anchor in c, 'profile evaluation anchor not found'
    c = c.replace(profile_eval_anchor, profile_eval + profile_eval_anchor, 1)

# Add compact profile-pack controls into existing Tablet/Jewel managers where available.
tab_anchor = '            if (Settings.EnableTabletManager)\n            {\n'
if tab_anchor in c and '                DrawTabletPackUI();\n' not in c:
    c = c.replace(tab_anchor, tab_anchor + '                DrawTabletPackUI();\n', 1)

jewel_anchor = '            if (Settings.EnableJewelManager)\n            {\n'
if jewel_anchor in c and '                DrawJewelPackUI();\n' not in c:
    c = c.replace(jewel_anchor, jewel_anchor + '                DrawJewelPackUI();\n', 1)

# Helper/UI methods inserted before GetExplorerRootAddress.
method_anchor = '        private IntPtr GetExplorerRootAddress()\n'
methods = r'''        private StashUtility.Models.WaystoneProfile FindFirstMatchingWaystoneProfile(StashUtility.Models.WaystoneSnapshot snapshot, HashSet<string> presentModIds)
        {
            if (Settings.WaystoneProfiles == null) return null;
            foreach (var profile in Settings.WaystoneProfiles)
                if (profile != null && profile.Matches(snapshot, presentModIds)) return profile;
            return null;
        }

        private void DrawWaystoneProfileHighlight(StashUtility.Models.WaystoneProfile profile, Vector2 pos, Vector2 size, GameHelper.RemoteEnums.Rarity rarity)
        {
            float scale = size.X / 52.0f;
            float margin = Math.Max(0f, profile.BorderMargin) * scale;
            float activeBorderThickness = 0f;
            bool drawBorder = profile.IndicatorMode == StashUtility.Models.WaystoneIndicatorMode.Border || profile.IndicatorMode == StashUtility.Models.WaystoneIndicatorMode.BorderAndArrow;
            bool drawArrow = profile.IndicatorMode == StashUtility.Models.WaystoneIndicatorMode.Arrow || profile.IndicatorMode == StashUtility.Models.WaystoneIndicatorMode.BorderAndArrow;
            if (drawBorder)
            {
                float thickness = Math.Max(1f, profile.BorderThickness);
                activeBorderThickness = thickness;
                float inset = margin + thickness / 2f;
                AddStyledRect(ImGui.GetBackgroundDrawList(), pos + new Vector2(inset, inset), pos + size - new Vector2(inset, inset), ImGuiHelper.Color(profile.Color), thickness, Math.Clamp(profile.BorderStyle, 0, 2));
            }
            if (Settings.ShowRarityBorder)
            {
                Vector4 rarityCol = rarity switch
                {
                    GameHelper.RemoteEnums.Rarity.Normal => Settings.NormalRarityColor,
                    GameHelper.RemoteEnums.Rarity.Magic => Settings.MagicRarityColor,
                    GameHelper.RemoteEnums.Rarity.Rare => Settings.RareRarityColor,
                    GameHelper.RemoteEnums.Rarity.Unique => new Vector4(1f, .5f, 0f, 1f),
                    _ => Settings.NormalRarityColor
                };
                float offset = margin + activeBorderThickness;
                float sv = Settings.RarityIndicatorSize;
                var p0 = pos + new Vector2(size.X - offset - sv, offset);
                var p1 = pos + new Vector2(size.X - offset, offset);
                var p2 = pos + new Vector2(size.X - offset, offset + sv);
                ImGui.GetBackgroundDrawList().AddTriangleFilled(p0, p1, p2, ImGuiHelper.Color(rarityCol));
            }
            if (drawArrow)
            {
                float a = Math.Max(5f, profile.ArrowSize) * scale;
                float pad = 4f * scale + margin + activeBorderThickness;
                Vector2 tip = profile.ArrowPosition switch
                {
                    0 => pos + new Vector2(pad + a / 2, pad),
                    1 => pos + new Vector2(size.X - pad - a / 2, pad + (Settings.ShowRarityBorder ? Settings.RarityIndicatorSize : 0f)),
                    2 => pos + new Vector2(pad + a / 2, size.Y - pad - a),
                    3 => pos + new Vector2(size.X - pad - a / 2, size.Y - pad - a),
                    _ => pos + new Vector2(pad + a / 2, pad)
                };
                var dl = ImGui.GetBackgroundDrawList();
                dl.AddTriangleFilled(tip, tip + new Vector2(-a/2,a), tip + new Vector2(a/2,a), ImGuiHelper.Color(profile.ArrowColor));
                dl.AddTriangle(tip, tip + new Vector2(-a/2,a), tip + new Vector2(a/2,a), 0xFF000000, Math.Max(1f, 1.5f * scale));
            }
        }

        private void DrawWaystoneProfilesUI()
        {
            Settings.WaystoneProfiles ??= new List<StashUtility.Models.WaystoneProfile>();
            ImGui.SeparatorText("Waystone Profiles — first match wins");
            ImGui.TextWrapped("Priority is the list order. Use arrows to move a profile up/down.");
            if (ImGui.Button("+ Blank profile"))
            {
                Settings.WaystoneProfiles.Add(new StashUtility.Models.WaystoneProfile { Name = $"Profile {Settings.WaystoneProfiles.Count + 1}" });
                SaveSettings();
            }
            ImGui.SameLine();
            if (ImGui.BeginCombo("Add preset", "Choose..."))
            {
                foreach (var preset in StashUtility.ProfilePacks.DefaultWaystonePresets.CreateAll())
                    if (ImGui.Selectable(preset.Name)) { Settings.WaystoneProfiles.Add(preset); SaveSettings(); }
                ImGui.EndCombo();
            }
            ImGui.SameLine();
            if (ImGui.Button("Export pack"))
            {
                try { profilePackStatus = "Exported: " + profilePackService.ExportWaystones(waystonePackName, Settings.WaystoneProfiles); }
                catch (Exception ex) { profilePackStatus = ex.Message; }
            }
            ImGui.SetNextItemWidth(220f); ImGui.InputText("Pack name", ref waystonePackName, 80);
            var files = profilePackService?.ListWaystonePacks() ?? Array.Empty<string>();
            if (files.Count > 0)
            {
                selectedWaystonePackIndex = Math.Clamp(selectedWaystonePackIndex, 0, files.Count - 1);
                ImGui.SetNextItemWidth(300f);
                if (ImGui.BeginCombo("Import pack", files[selectedWaystonePackIndex]))
                {
                    for (int i = 0; i < files.Count; i++) if (ImGui.Selectable(files[i], i == selectedWaystonePackIndex)) selectedWaystonePackIndex = i;
                    ImGui.EndCombo();
                }
                ImGui.SameLine();
                if (ImGui.Button("Append")) { try { var p = profilePackService.ImportWaystones(files[selectedWaystonePackIndex]); Settings.WaystoneProfiles.AddRange(p.Profiles); SaveSettings(); profilePackStatus = $"Appended {p.Profiles.Count} profiles"; } catch (Exception ex) { profilePackStatus = ex.Message; } }
                ImGui.SameLine();
                if (ImGui.Button("Replace")) { try { var p = profilePackService.ImportWaystones(files[selectedWaystonePackIndex]); Settings.WaystoneProfiles = p.Profiles; SaveSettings(); profilePackStatus = $"Loaded {p.Profiles.Count} profiles"; } catch (Exception ex) { profilePackStatus = ex.Message; } }
            }
            if (!string.IsNullOrWhiteSpace(profilePackStatus)) ImGui.TextWrapped(profilePackStatus);

            for (int i = 0; i < Settings.WaystoneProfiles.Count; i++)
            {
                var p = Settings.WaystoneProfiles[i]; if (p == null) continue;
                ImGui.PushID(p.Id);
                ImGui.Checkbox("##enabled", ref p.Enabled); ImGui.SameLine();
                if (ImGui.SmallButton("↑") && i > 0) { (Settings.WaystoneProfiles[i-1], Settings.WaystoneProfiles[i]) = (Settings.WaystoneProfiles[i], Settings.WaystoneProfiles[i-1]); SaveSettings(); ImGui.PopID(); break; }
                ImGui.SameLine();
                if (ImGui.SmallButton("↓") && i < Settings.WaystoneProfiles.Count - 1) { (Settings.WaystoneProfiles[i+1], Settings.WaystoneProfiles[i]) = (Settings.WaystoneProfiles[i], Settings.WaystoneProfiles[i+1]); SaveSettings(); ImGui.PopID(); break; }
                ImGui.SameLine();
                if (ImGui.CollapsingHeader($"{i+1}. {p.Name}##header", ImGuiTreeNodeFlags.DefaultOpen))
                {
                    string n = p.Name ?? ""; if (ImGui.InputText("Name", ref n, 80)) p.Name = n;
                    string d = p.Description ?? ""; if (ImGui.InputTextMultiline("Description", ref d, 256, new Vector2(520,55))) p.Description = d;
                    ImGui.Checkbox("Match everything (catch-all)", ref p.MatchEverything);
                    if (!p.HasAnyCriteria() && !p.MatchEverything) ImGui.TextColored(new Vector4(1f,.75f,.2f,1f), "Empty profile does not match anything.");
                    string[] indicators = { "Border", "Arrow", "Border + Arrow" }; int ind = (int)p.IndicatorMode; if (ImGui.Combo("Indicator", ref ind, indicators, indicators.Length)) p.IndicatorMode = (StashUtility.Models.WaystoneIndicatorMode)ind;
                    ImGui.ColorEdit4("Color", ref p.Color); ImGui.ColorEdit4("Arrow color", ref p.ArrowColor);
                    string[] styles = { "Solid", "Dashed", "Dotted" }; ImGui.Combo("Border style", ref p.BorderStyle, styles, styles.Length);
                    ImGui.SliderFloat("Border thickness", ref p.BorderThickness, 1f, 10f); ImGui.SliderFloat("Border margin", ref p.BorderMargin, 0f, 10f); ImGui.SliderFloat("Arrow size", ref p.ArrowSize, 5f, 40f); ImGui.SliderInt("Arrow position", ref p.ArrowPosition, 0, 3);
                    DrawProfileRange("Tier", p.Tier, 1, 16); DrawProfileRange("Revives", p.Revives, 0, 5); DrawProfileRange("Explicit Mods", p.ExplicitMods, 0, 10); DrawProfileRange("Item Rarity", p.ItemRarity, 0, 250); DrawProfileRange("Pack Size", p.PackSize, 0, 150); DrawProfileRange("Monster Rarity", p.MonsterRarity, 0, 200); DrawProfileRange("Monster Effectiveness", p.MonsterEffectiveness, 0, 150); DrawProfileRange("Waystone Drop Chance", p.WaystoneDropChance, 0, 400);
                    DrawProfileModRules(p);
                    if (ImGui.Button("Duplicate")) { Settings.WaystoneProfiles.Insert(i+1, p.DeepClone()); SaveSettings(); ImGui.PopID(); break; }
                    ImGui.SameLine(); if (ImGui.Button("Delete")) { Settings.WaystoneProfiles.RemoveAt(i); SaveSettings(); ImGui.PopID(); break; }
                }
                ImGui.PopID(); ImGui.Separator();
            }
        }

        private void DrawProfileRange(string label, StashUtility.Models.IntRangeCriterion r, int low, int high)
        {
            ImGui.PushID(label); ImGui.TextUnformatted(label); ImGui.SameLine(210f); ImGui.Checkbox("Min", ref r.MinEnabled); if (r.MinEnabled) { ImGui.SameLine(); ImGui.SetNextItemWidth(110f); ImGui.SliderInt("##min", ref r.Min, low, high); } ImGui.SameLine(410f); ImGui.Checkbox("Max", ref r.MaxEnabled); if (r.MaxEnabled) { ImGui.SameLine(); ImGui.SetNextItemWidth(110f); ImGui.SliderInt("##max", ref r.Max, low, high); } ImGui.PopID();
        }

        private void DrawProfileModRules(StashUtility.Models.WaystoneProfile p)
        {
            if (!ImGui.TreeNode("Modifier rules")) return;
            DrawProfileModBucket("Require ANY", p.RequireAnyModIds); if (p.RequireAnyModIds.Count > 0) ImGui.SliderInt("Minimum ANY matches", ref p.MinAnyModMatches, 1, p.RequireAnyModIds.Count);
            DrawProfileModBucket("Require ALL", p.RequireAllModIds); DrawProfileModBucket("EXCLUDE", p.ExcludedModIds); ImGui.TreePop();
        }

        private void DrawProfileModBucket(string label, List<string> bucket)
        {
            ImGui.PushID(label);
            if (ImGui.BeginCombo($"Add to {label}", "Select mod..."))
            {
                ImGui.InputTextWithHint("##search", "Search...", ref waystoneSearchTerm, 64);
                foreach (var mod in Data.ModDatabase.AllWaystoneMods.Where(m => m.Name.Contains(waystoneSearchTerm, StringComparison.OrdinalIgnoreCase) || m.Id.Contains(waystoneSearchTerm, StringComparison.OrdinalIgnoreCase)))
                    if (ImGui.Selectable($"{mod.Name}##{mod.Id}")) { if (!bucket.Contains(mod.Id)) bucket.Add(mod.Id); SaveSettings(); }
                ImGui.EndCombo();
            }
            for (int i=0;i<bucket.Count;i++) { string id=bucket[i]; var def=Data.ModDatabase.AllWaystoneMods.FirstOrDefault(x=>x.Id==id); if (ImGui.SmallButton($"X##{i}")) { bucket.RemoveAt(i); SaveSettings(); break; } ImGui.SameLine(); ImGui.TextUnformatted(def?.Name ?? id); }
            ImGui.PopID();
        }

        private void DrawTabletPackUI()
        {
            if (profilePackService == null) return;
            if (ImGui.SmallButton("Export Tablet Pack")) { try { profilePackService.ExportTablets("tablets-export", Settings.TabletProfiles); profilePackStatus="Tablet pack exported"; } catch(Exception ex){ profilePackStatus=ex.Message; } }
            var files=profilePackService.ListTabletPacks(); if(files.Count==0)return; selectedTabletPackIndex=Math.Clamp(selectedTabletPackIndex,0,files.Count-1); ImGui.SameLine(); ImGui.SetNextItemWidth(260f); if(ImGui.BeginCombo("##tabletPack",files[selectedTabletPackIndex])){for(int i=0;i<files.Count;i++)if(ImGui.Selectable(files[i],i==selectedTabletPackIndex))selectedTabletPackIndex=i;ImGui.EndCombo();} ImGui.SameLine(); if(ImGui.SmallButton("Load Tablet Pack")){try{var pack=profilePackService.ImportTablets(files[selectedTabletPackIndex]);Settings.TabletProfiles=pack.Profiles;foreach(var t in StashUtilitySettings.TabletTypes)if(!Settings.TabletProfiles.ContainsKey(t))Settings.TabletProfiles[t]=new TabletProfile();SaveSettings();profilePackStatus="Tablet pack loaded";}catch(Exception ex){profilePackStatus=ex.Message;}}
        }

        private void DrawJewelPackUI()
        {
            if (profilePackService == null) return;
            if (ImGui.SmallButton("Export Jewel Pack")) { try { profilePackService.ExportJewels("jewels-export", Settings.JewelCategoryGroups); profilePackStatus="Jewel pack exported"; } catch(Exception ex){ profilePackStatus=ex.Message; } }
            var files=profilePackService.ListJewelPacks(); if(files.Count==0)return; selectedJewelPackIndex=Math.Clamp(selectedJewelPackIndex,0,files.Count-1); ImGui.SameLine(); ImGui.SetNextItemWidth(260f); if(ImGui.BeginCombo("##jewelPack",files[selectedJewelPackIndex])){for(int i=0;i<files.Count;i++)if(ImGui.Selectable(files[i],i==selectedJewelPackIndex))selectedJewelPackIndex=i;ImGui.EndCombo();} ImGui.SameLine(); if(ImGui.SmallButton("Load Jewel Pack")){try{var pack=profilePackService.ImportJewels(files[selectedJewelPackIndex]);Settings.JewelCategoryGroups=pack.Categories;SaveSettings();profilePackStatus="Jewel pack loaded";}catch(Exception ex){profilePackStatus=ex.Message;}}
        }

'''
if 'private StashUtility.Models.WaystoneProfile FindFirstMatchingWaystoneProfile' not in c:
    assert method_anchor in c, 'method insertion anchor not found'
    c = c.replace(method_anchor, methods + method_anchor, 1)

core_path.write_text(c, encoding='utf-8')
print('Profile engine patch applied successfully')
