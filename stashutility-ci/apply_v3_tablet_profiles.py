from pathlib import Path
import re
import shutil

ROOT = Path('GameHelper2/Plugins/StashUtility')
HARNESS = Path('harness/stashutility-ci')

# Copy v3 source files.
for f in ['TabletRuleProfile.cs', 'CurrentTabletPresets.cs', 'TabletRulePackService.cs']:
    src = HARNESS / f
    dst = ROOT / ('Models' if f == 'TabletRuleProfile.cs' else 'ProfilePacks') / f
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

# ---------------- Current tablet mod database ----------------
moddb = ROOT / 'Data' / 'ModDatabase.cs'
m = moddb.read_text(encoding='utf-8')
stale_ids = [
    'TowerExpeditionIncreasedVerisium',
    'TowerExpeditionUnearthedRares',
    'TowerExpeditionAdditionalSentinels',
    'TowerExpeditionIncreasedMonsterRarity',
    'TowerExpeditionFrozenBosses',
    'TowerExpeditionBuriedStrongboxes',
    'TowerExpeditionVaalRemnants',
    'TowerExpeditionChanceForVerisiumRemnant',
    'TowerExpeditionChanceForTwinnedElites',
    'TowerExpedition2RunicModPassoverChance',
]
for stale in stale_ids:
    m, count = re.subn(r'^\s*new TabletMod\("' + re.escape(stale) + r'".*\n', '', m, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f'Expected stale tablet mod not found exactly once: {stale}')

m = m.replace('new TabletMod("TowerExpeditionExplosionRadius", "% increased Expedition Explosive Area of Effect in Map", "suffix", "Expedition") { MinRoll = 5, MaxRoll = 10 }',
              'new TabletMod("TowerExpeditionExplosionRadius", "% increased Expedition Explosive Radius in Map", "suffix", "Expedition") { MinRoll = 15, MaxRoll = 30 }')
m = m.replace('new TabletMod("TowerExpeditionLogbookIncrease", "% increased Quantity of Expedition Logbooks dropped by Runic Monsters in Map", "suffix", "Expedition") { MinRoll = 15, MaxRoll = 25 }',
              'new TabletMod("TowerExpeditionLogbookIncrease", "% increased Quantity of Expedition Logbooks dropped by Runic Monsters in Map", "suffix", "Expedition") { MinRoll = 15, MaxRoll = 30 }')
m = m.replace('new TabletMod("TowerExpeditionRunicMonsters", "Map contains % increased number of Runic Monster Markers", "suffix", "Expedition") { MinRoll = 15, MaxRoll = 25 }',
              'new TabletMod("TowerExpeditionRunicMonsters", "Map contains % increased number of Runic Monster Markers", "suffix", "Expedition") { MinRoll = 15, MaxRoll = 30 }')

section = m[m.index('public static readonly List<TabletMod> AllTabletMods'):m.index('public static readonly List<JewelMod> AllJewelMods')]
count_mods = section.count('new TabletMod(')
if count_mods != 83:
    raise RuntimeError(f'Current tablet DB sanity check failed: expected 83 mods, got {count_mods}')
for stale in stale_ids:
    if stale in section:
        raise RuntimeError(f'Stale Aldur tablet mod survived cleanup: {stale}')
moddb.write_text(m, encoding='utf-8')
print('Tablet database cleaned and validated: 83 current mods')

# ---------------- Settings ----------------
settings_path = ROOT / 'StashUtilitySettings.cs'
s = settings_path.read_text(encoding='utf-8')
anchor = '        // Debug Probe Mode\n'
insert = '''        // Ordered Tablet rule profiles. List order is priority; first match wins.\n        public bool EnableTabletRuleProfiles = true;\n        public bool ShowLegacyTabletEditor = false;\n        public List<StashUtility.Models.TabletRuleProfile> TabletRuleProfiles = new();\n\n'''
if insert not in s:
    if anchor not in s: raise RuntimeError('settings tablet profile anchor not found')
    s = s.replace(anchor, insert + anchor, 1)
settings_path.write_text(s, encoding='utf-8')

# ---------------- Core fields/init ----------------
core_path = ROOT / 'StashUtilityCore.cs'
c = core_path.read_text(encoding='utf-8')
field_anchor = '        private StashUtility.ProfilePacks.ProfilePackService profilePackService;\n'
field_insert = '''        private StashUtility.ProfilePacks.TabletRulePackService tabletRulePackService;\n        private string tabletRulePackName = "current-tablet-profiles";\n        private int selectedTabletRulePackIndex = 0;\n'''
if field_insert not in c:
    if field_anchor not in c: raise RuntimeError('profile pack service field anchor not found')
    c = c.replace(field_anchor, field_anchor + field_insert, 1)

init_anchor = '            profilePackService = new StashUtility.ProfilePacks.ProfilePackService(DllDirectory);\n'
init_insert = '''            Settings.TabletRuleProfiles ??= new List<StashUtility.Models.TabletRuleProfile>();\n            tabletRulePackService = new StashUtility.ProfilePacks.TabletRulePackService(DllDirectory);\n            SanitizeTabletProfiles();\n'''
if init_insert not in c:
    if init_anchor not in c: raise RuntimeError('profile pack init anchor not found')
    c = c.replace(init_anchor, init_anchor + init_insert, 1)

# Track current tablet mod IDs for ordered rule matching.
waystone_set = '            var presentWaystoneModIds = new HashSet<string>();\n'
tablet_vars = '''            var presentTabletModIds = new HashSet<string>();\n            string detectedTabletType = isTablet ? DetectTabletType(name, path) : null;\n'''
if tablet_vars not in c:
    if waystone_set not in c: raise RuntimeError('waystone mod set anchor not found')
    c = c.replace(waystone_set, waystone_set + tablet_vars, 1)

# Add IDs whenever the existing tablet decoder recognizes a current mod.
search_from = c.index('var def = Data.ModDatabase.AllTabletMods')
def_pos = c.index('if (def != null)', search_from)
brace_pos = c.index('{', def_pos)
add_line = '\n                                presentTabletModIds.Add(def.Id);'
if add_line.strip() not in c[def_pos:def_pos+600]:
    c = c[:brace_pos+1] + add_line + c[brace_pos+1:]

# Ordered Tablet profiles take over rendering when enabled.
num_anchor = '            bool passesNumericalFilters = true;\n'
tablet_eval = '''            if (isTablet && Settings.EnableTabletRuleProfiles)\n            {\n                var matchedTabletProfile = FindFirstMatchingTabletRuleProfile(detectedTabletType, explicitModsCount, presentTabletModIds);\n                if (matchedTabletProfile == null) return;\n                DrawTabletRuleProfileHighlight(matchedTabletProfile, pos, size, rarity);\n                return;\n            }\n\n'''
if tablet_eval not in c:
    if num_anchor not in c: raise RuntimeError('numerical filter anchor not found')
    c = c.replace(num_anchor, tablet_eval + num_anchor, 1)

# Replace v2 compact pack row with the v3 rule-profile UI and hide legacy editor by default.
old_call = '                DrawTabletPackUI();\n'
new_call = '''                DrawTabletRuleProfilesUI();\n                ImGui.Checkbox("Show legacy / manual Tablet editor", ref Settings.ShowLegacyTabletEditor);\n                ImGuiHelper.ToolTip("Legacy Good/Bad/God editor is kept for compatibility. Ordered profiles above are the recommended mode.");\n                if (Settings.ShowLegacyTabletEditor)\n                {\n                    DrawTabletPackUI();\n'''
if new_call not in c:
    if old_call not in c: raise RuntimeError('DrawTabletPackUI call anchor not found')
    c = c.replace(old_call, new_call, 1)
    jewel_banner = '            ImGui.PushStyleColor(ImGuiCol.Text, new Vector4(0.25f, 1.00f, 0.45f, 1.00f));\n            ImGui.SeparatorText("JEWELS");'
    jidx = c.index(jewel_banner)
    manager_close = c.rfind('\n            }\n', 0, jidx)
    if manager_close < 0: raise RuntimeError('Could not locate Tablet Manager closing brace')
    c = c[:manager_close] + '\n                }\n' + c[manager_close:]

# ---------------- Methods ----------------
method_anchor = '        private IntPtr GetExplorerRootAddress()\n'
methods = r'''        private string DetectTabletType(string itemName, string itemPath)
        {
            string name = itemName ?? string.Empty;
            string path = itemPath ?? string.Empty;
            if (name.Contains("Breach", StringComparison.OrdinalIgnoreCase)) return "Breach Tablet";
            if (name.Contains("Expedition", StringComparison.OrdinalIgnoreCase)) return "Expedition Tablet";
            if (name.Contains("Delirium", StringComparison.OrdinalIgnoreCase)) return "Delirium Tablet";
            if (name.Contains("Ritual", StringComparison.OrdinalIgnoreCase)) return "Ritual Tablet";
            if (name.Contains("Irradiated", StringComparison.OrdinalIgnoreCase)) return "Irradiated Tablet";
            if (name.Contains("Overseer", StringComparison.OrdinalIgnoreCase)) return "Overseer Tablet";
            if (name.Contains("Abyss", StringComparison.OrdinalIgnoreCase)) return "Abyss Tablet";
            if (name.Contains("Temple", StringComparison.OrdinalIgnoreCase) || name.Contains("Incursion", StringComparison.OrdinalIgnoreCase)) return "Temple Tablet";
            if (path.Contains("BreachAugment", StringComparison.OrdinalIgnoreCase)) return "Breach Tablet";
            if (path.Contains("ExpeditionAugment", StringComparison.OrdinalIgnoreCase)) return "Expedition Tablet";
            if (path.Contains("DeliriumAugment", StringComparison.OrdinalIgnoreCase)) return "Delirium Tablet";
            if (path.Contains("RitualAugment", StringComparison.OrdinalIgnoreCase)) return "Ritual Tablet";
            if (path.Contains("GenericAugment", StringComparison.OrdinalIgnoreCase)) return "Irradiated Tablet";
            if (path.Contains("MapBossAugment", StringComparison.OrdinalIgnoreCase)) return "Overseer Tablet";
            if (path.Contains("AbyssAugment", StringComparison.OrdinalIgnoreCase)) return "Abyss Tablet";
            if (path.Contains("IncursionAugment", StringComparison.OrdinalIgnoreCase)) return "Temple Tablet";
            return "Unknown Tablet";
        }

        private void SanitizeTabletProfiles()
        {
            var valid = Data.ModDatabase.AllTabletMods.Select(x => x.Id).ToHashSet(StringComparer.OrdinalIgnoreCase);
            Settings.TabletRuleProfiles ??= new List<StashUtility.Models.TabletRuleProfile>();
            foreach (var p in Settings.TabletRuleProfiles.Where(x => x != null))
            {
                p.RequireAnyModIds = (p.RequireAnyModIds ?? new()).Where(valid.Contains).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
                p.RequireAllModIds = (p.RequireAllModIds ?? new()).Where(valid.Contains).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
                p.ExcludedModIds = (p.ExcludedModIds ?? new()).Where(valid.Contains).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
            }
            if (Settings.TabletProfiles != null)
            {
                foreach (var lp in Settings.TabletProfiles.Values.Where(x => x != null))
                {
                    lp.GoodModPatterns = (lp.GoodModPatterns ?? new()).Where(valid.Contains).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
                    lp.BadModPatterns = (lp.BadModPatterns ?? new()).Where(valid.Contains).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
                    lp.GodModPatterns = (lp.GodModPatterns ?? new()).Where(valid.Contains).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
                    lp.ModRequiredMinRolls = (lp.ModRequiredMinRolls ?? new Dictionary<string,float>()).Where(kv => valid.Contains(kv.Key)).ToDictionary(kv => kv.Key, kv => kv.Value, StringComparer.OrdinalIgnoreCase);
                }
            }
        }

        private StashUtility.Models.TabletRuleProfile FindFirstMatchingTabletRuleProfile(string tabletType, int explicitMods, HashSet<string> presentModIds)
        {
            if (Settings.TabletRuleProfiles == null) return null;
            foreach (var p in Settings.TabletRuleProfiles)
                if (p != null && p.Matches(tabletType, explicitMods, presentModIds)) return p;
            return null;
        }

        private void DrawTabletRuleProfileHighlight(StashUtility.Models.TabletRuleProfile profile, Vector2 pos, Vector2 size, GameHelper.RemoteEnums.Rarity rarity)
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
                AddStyledRect(ImGui.GetBackgroundDrawList(), pos + new Vector2(inset,inset), pos + size - new Vector2(inset,inset), ImGuiHelper.Color(profile.Color), thickness, Math.Clamp(profile.BorderStyle,0,2));
            }
            if (Settings.ShowRarityBorder)
            {
                Vector4 rarityCol = rarity switch
                {
                    GameHelper.RemoteEnums.Rarity.Normal => Settings.NormalRarityColor,
                    GameHelper.RemoteEnums.Rarity.Magic => Settings.MagicRarityColor,
                    GameHelper.RemoteEnums.Rarity.Rare => Settings.RareRarityColor,
                    GameHelper.RemoteEnums.Rarity.Unique => new Vector4(1f,.5f,0f,1f),
                    _ => Settings.NormalRarityColor
                };
                float offset = margin + activeBorderThickness;
                float sv = Settings.RarityIndicatorSize;
                ImGui.GetBackgroundDrawList().AddTriangleFilled(pos + new Vector2(size.X-offset-sv,offset), pos + new Vector2(size.X-offset,offset), pos + new Vector2(size.X-offset,offset+sv), ImGuiHelper.Color(rarityCol));
            }
            if (drawArrow)
            {
                float a = Math.Max(5f, profile.ArrowSize) * scale;
                float pad = 4f * scale + margin + activeBorderThickness;
                Vector2 tip = profile.ArrowPosition switch
                {
                    0 => pos + new Vector2(pad+a/2,pad), 1 => pos + new Vector2(size.X-pad-a/2,pad+(Settings.ShowRarityBorder?Settings.RarityIndicatorSize:0f)),
                    2 => pos + new Vector2(pad+a/2,size.Y-pad-a), 3 => pos + new Vector2(size.X-pad-a/2,size.Y-pad-a), _ => pos + new Vector2(pad+a/2,pad)
                };
                var dl = ImGui.GetBackgroundDrawList();
                dl.AddTriangleFilled(tip, tip+new Vector2(-a/2,a), tip+new Vector2(a/2,a), ImGuiHelper.Color(profile.ArrowColor));
                dl.AddTriangle(tip, tip+new Vector2(-a/2,a), tip+new Vector2(a/2,a), 0xFF000000, Math.Max(1f,1.5f*scale));
            }
        }

        private void DrawTabletRuleProfilesUI()
        {
            Settings.TabletRuleProfiles ??= new List<StashUtility.Models.TabletRuleProfile>();
            ImGui.SeparatorText("Tablet Profiles — first match wins");
            ImGui.TextDisabled("Put the most specific / valuable profiles at the top. No roll threshold is required unless you use the legacy editor.");

            if (ImGui.Button("+ Blank Tablet profile")) { Settings.TabletRuleProfiles.Add(new StashUtility.Models.TabletRuleProfile { Name=$"Tablet Profile {Settings.TabletRuleProfiles.Count+1}" }); SaveSettings(); }
            ImGui.SameLine();
            if (ImGui.Button("+ Current starter pack")) { Settings.TabletRuleProfiles.AddRange(StashUtility.ProfilePacks.CurrentTabletPresets.CreateStarterPack()); SaveSettings(); }
            ImGui.SameLine();
            if (ImGui.BeginCombo("Add Tablet preset", "Choose..."))
            {
                foreach (var preset in StashUtility.ProfilePacks.CurrentTabletPresets.CreateAll())
                    if (ImGui.Selectable(preset.Name)) { Settings.TabletRuleProfiles.Add(preset); SaveSettings(); }
                ImGui.EndCombo();
            }

            ImGui.TextDisabled("Import: drop *.json into profiles/tablets — the list refreshes automatically");
            if (tabletRulePackService != null)
            {
                var files = tabletRulePackService.ListPacks();
                if (files.Count > 0)
                {
                    selectedTabletRulePackIndex = Math.Clamp(selectedTabletRulePackIndex,0,files.Count-1);
                    ImGui.SetNextItemWidth(300f);
                    if (ImGui.BeginCombo("Tablet profile pack", files[selectedTabletRulePackIndex]))
                    {
                        for (int i=0;i<files.Count;i++) if (ImGui.Selectable(files[i], i==selectedTabletRulePackIndex)) selectedTabletRulePackIndex=i;
                        ImGui.EndCombo();
                    }
                    ImGui.SameLine();
                    if (ImGui.SmallButton("Append##tabletRules"))
                    {
                        try { var pack=tabletRulePackService.Import(files[selectedTabletRulePackIndex]); SanitizeImportedTabletProfiles(pack.Profiles); Settings.TabletRuleProfiles.AddRange(pack.Profiles); SaveSettings(); profilePackStatus=$"Tablet profiles appended: {pack.Name}"; } catch(Exception ex){profilePackStatus=ex.Message;}
                    }
                    ImGui.SameLine();
                    if (ImGui.SmallButton("Replace##tabletRules"))
                    {
                        try { var pack=tabletRulePackService.Import(files[selectedTabletRulePackIndex]); SanitizeImportedTabletProfiles(pack.Profiles); Settings.TabletRuleProfiles=pack.Profiles; SaveSettings(); profilePackStatus=$"Tablet profiles loaded: {pack.Name}"; } catch(Exception ex){profilePackStatus=ex.Message;}
                    }
                }
                ImGui.SetNextItemWidth(220f); ImGui.InputText("Export name##tabletRules", ref tabletRulePackName, 80);
                ImGui.SameLine();
                if (ImGui.SmallButton("Export profiles##tabletRules")) { try { profilePackStatus="Exported: "+tabletRulePackService.Export(tabletRulePackName,Settings.TabletRuleProfiles); } catch(Exception ex){profilePackStatus=ex.Message;} }
            }
            if (!string.IsNullOrWhiteSpace(profilePackStatus)) ImGui.TextWrapped(profilePackStatus);

            for (int i=0;i<Settings.TabletRuleProfiles.Count;i++)
            {
                var p=Settings.TabletRuleProfiles[i]; if(p==null) continue;
                ImGui.PushID(p.Id);
                ImGui.Checkbox("##enabled", ref p.Enabled); ImGui.SameLine();
                if(ImGui.SmallButton("↑") && i>0){(Settings.TabletRuleProfiles[i-1],Settings.TabletRuleProfiles[i])=(Settings.TabletRuleProfiles[i],Settings.TabletRuleProfiles[i-1]);SaveSettings();ImGui.PopID();break;}
                ImGui.SameLine();
                if(ImGui.SmallButton("↓") && i<Settings.TabletRuleProfiles.Count-1){(Settings.TabletRuleProfiles[i+1],Settings.TabletRuleProfiles[i])=(Settings.TabletRuleProfiles[i],Settings.TabletRuleProfiles[i+1]);SaveSettings();ImGui.PopID();break;}
                ImGui.SameLine();
                ImGui.ColorButton("##swatch", p.Color, ImGuiColorEditFlags.NoTooltip, new Vector2(18,18)); ImGui.SameLine();
                if(ImGui.CollapsingHeader($"{i+1}. {p.Name}##tabletProfile", ImGuiTreeNodeFlags.DefaultOpen))
                {
                    string n=p.Name??""; if(ImGui.InputText("Name",ref n,80)){p.Name=n;SaveSettings();}
                    string d=p.Description??""; if(ImGui.InputTextMultiline("Description",ref d,256,new Vector2(520,45))){p.Description=d;SaveSettings();}
                    string[] types=(new[]{"Any"}).Concat(StashUtilitySettings.TabletTypes).ToArray(); int ti=Math.Max(0,Array.FindIndex(types,x=>string.Equals(x,p.TabletType,StringComparison.OrdinalIgnoreCase))); if(ImGui.Combo("Applies to",ref ti,types,types.Length)){p.TabletType=types[ti];SaveSettings();}
                    if(ImGui.Checkbox("Match everything in this Tablet type",ref p.MatchEverything)) SaveSettings();
                    if(!p.MatchEverything && !p.HasAnyCriteria()) ImGui.TextColored(new Vector4(1f,.75f,.2f,1f),"Empty profile does not match anything.");

                    DrawProfileRange("Explicit Mods##tablet",p.ExplicitMods,0,6);
                    DrawTabletRuleModBucket("Require ANY",p.RequireAnyModIds,p,"At least N of these modifiers must be present.");
                    if(p.RequireAnyModIds.Count>0){int max=Math.Max(1,p.RequireAnyModIds.Count);p.MinAnyModMatches=Math.Clamp(p.MinAnyModMatches,1,max);if(ImGui.SliderInt("Minimum ANY matches",ref p.MinAnyModMatches,1,max))SaveSettings();}
                    DrawTabletRuleModBucket("Require ALL",p.RequireAllModIds,p,"Every modifier in this list must be present.");
                    DrawTabletRuleModBucket("EXCLUDE",p.ExcludedModIds,p,"If any of these modifiers is present, this profile will not match.");

                    string[] indicators={"Border","Arrow","Border + Arrow"}; int ind=(int)p.IndicatorMode; if(ImGui.Combo("Indicator",ref ind,indicators,indicators.Length)){p.IndicatorMode=(StashUtility.Models.WaystoneIndicatorMode)ind;SaveSettings();}
                    if(ImGui.ColorEdit4("Profile color",ref p.Color)) SaveSettings();
                    if(ImGui.ColorEdit4("Arrow color",ref p.ArrowColor)) SaveSettings();
                    string[] styles={"Solid","Dashed","Dotted"}; if(ImGui.Combo("Border style",ref p.BorderStyle,styles,styles.Length))SaveSettings();
                    if(ImGui.SliderFloat("Border thickness",ref p.BorderThickness,1f,10f))SaveSettings();
                    if(ImGui.SliderFloat("Border margin",ref p.BorderMargin,0f,10f))SaveSettings();
                    if(ImGui.SliderFloat("Arrow size",ref p.ArrowSize,5f,40f))SaveSettings();
                    if(ImGui.SliderInt("Arrow position",ref p.ArrowPosition,0,3))SaveSettings();
                    if(ImGui.Button("Duplicate##tabletRule")){Settings.TabletRuleProfiles.Insert(i+1,p.DeepClone());SaveSettings();ImGui.PopID();break;}
                    ImGui.SameLine(); if(ImGui.Button("Delete##tabletRule")){Settings.TabletRuleProfiles.RemoveAt(i);SaveSettings();ImGui.PopID();break;}
                }
                ImGui.PopID(); ImGui.Separator();
            }
        }

        private void SanitizeImportedTabletProfiles(List<StashUtility.Models.TabletRuleProfile> profiles)
        {
            var valid=Data.ModDatabase.AllTabletMods.Select(x=>x.Id).ToHashSet(StringComparer.OrdinalIgnoreCase);
            foreach(var p in (profiles??new()).Where(x=>x!=null))
            {
                p.RequireAnyModIds=(p.RequireAnyModIds??new()).Where(valid.Contains).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
                p.RequireAllModIds=(p.RequireAllModIds??new()).Where(valid.Contains).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
                p.ExcludedModIds=(p.ExcludedModIds??new()).Where(valid.Contains).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
            }
        }

        private void DrawTabletRuleModBucket(string label, List<string> bucket, StashUtility.Models.TabletRuleProfile profile, string help)
        {
            bucket ??= new List<string>();
            if(!ImGui.TreeNode($"{label} ({bucket.Count})##tabletBucket")) return;
            ImGui.TextDisabled(help);
            ImGui.SetNextItemWidth(260f); ImGui.InputText("Search modifier##tabletRuleSearch",ref tabletSearchTerm,96);
            string category=(profile.TabletType??"Any").Replace(" Tablet","");
            var candidates=Data.ModDatabase.AllTabletMods.Where(x => profile.TabletType=="Any" || x.Category=="General" || x.Category.Equals(category,StringComparison.OrdinalIgnoreCase)).Where(x=>string.IsNullOrWhiteSpace(tabletSearchTerm)||x.Name.Contains(tabletSearchTerm,StringComparison.OrdinalIgnoreCase)||x.Id.Contains(tabletSearchTerm,StringComparison.OrdinalIgnoreCase)).OrderBy(x=>x.Category).ThenBy(x=>x.Name).ToList();
            ImGui.SetNextItemWidth(520f);
            if(ImGui.BeginCombo($"Add modifier##{label}","Select..."))
            {
                foreach(var mod in candidates)
                {
                    bool exists=bucket.Contains(mod.Id);
                    if(ImGui.Selectable($"[{mod.Category}] {mod.Name}##{mod.Id}",exists) && !exists){bucket.Add(mod.Id);SaveSettings();}
                }
                ImGui.EndCombo();
            }
            for(int i=0;i<bucket.Count;i++)
            {
                string id=bucket[i]; var def=Data.ModDatabase.AllTabletMods.FirstOrDefault(x=>x.Id==id);
                if(ImGui.SmallButton($"X##tabletRule_{label}_{i}")){bucket.RemoveAt(i);SaveSettings();break;}
                ImGui.SameLine(); ImGui.TextUnformatted(def==null?id:$"[{def.Category}] {def.Name}");
            }
            ImGui.TreePop();
        }

'''
if 'private void DrawTabletRuleProfilesUI()' not in c:
    if method_anchor not in c: raise RuntimeError('method insertion anchor not found')
    c = c.replace(method_anchor, methods + method_anchor, 1)

core_path.write_text(c, encoding='utf-8')
print('v3 tablet profile engine patch applied')
