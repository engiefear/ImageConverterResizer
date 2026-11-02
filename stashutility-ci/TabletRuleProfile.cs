namespace StashUtility.Models
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Numerics;

    public sealed class TabletRuleProfile
    {
        public string Id = Guid.NewGuid().ToString("N");
        public string Name = "Tablet profile";
        public string Description = string.Empty;
        public bool Enabled = true;
        public string TabletType = "Any";
        public bool MatchEverything = false;
        public IntRangeCriterion ExplicitMods = new();
        public List<string> RequireAnyModIds = new();
        public int MinAnyModMatches = 1;
        public List<string> RequireAllModIds = new();
        public List<string> ExcludedModIds = new();
        public Vector4 Color = new(0.85f, 0.20f, 1.00f, 1.00f);
        public Vector4 ArrowColor = new(1.00f, 0.82f, 0.10f, 1.00f);
        public WaystoneIndicatorMode IndicatorMode = WaystoneIndicatorMode.BorderAndArrow;
        public int BorderStyle = 0;
        public float BorderThickness = 3f;
        public float BorderMargin = 4f;
        public int ArrowPosition = 0;
        public float ArrowSize = 18f;

        public bool HasAnyCriteria() => ExplicitMods.MinEnabled || ExplicitMods.MaxEnabled || RequireAnyModIds.Count > 0 || RequireAllModIds.Count > 0 || ExcludedModIds.Count > 0;

        public bool Matches(string detectedTabletType, int explicitMods, HashSet<string> presentModIds)
        {
            if (!Enabled) return false;
            if (!string.Equals(TabletType, "Any", StringComparison.OrdinalIgnoreCase) && !string.Equals(TabletType, detectedTabletType, StringComparison.OrdinalIgnoreCase)) return false;
            if (MatchEverything) return true;
            if (!HasAnyCriteria()) return false;
            if (!ExplicitMods.Matches(explicitMods)) return false;
            if (ExcludedModIds.Any(presentModIds.Contains)) return false;
            if (RequireAllModIds.Any(id => !presentModIds.Contains(id))) return false;
            if (RequireAnyModIds.Count > 0)
            {
                int needed = Math.Clamp(MinAnyModMatches, 1, RequireAnyModIds.Count);
                if (RequireAnyModIds.Count(presentModIds.Contains) < needed) return false;
            }
            return true;
        }

        public TabletRuleProfile DeepClone(string suffix = " copy") => new()
        {
            Id = Guid.NewGuid().ToString("N"), Name = (Name ?? "Tablet profile") + suffix, Description = Description ?? string.Empty,
            Enabled = Enabled, TabletType = TabletType ?? "Any", MatchEverything = MatchEverything, ExplicitMods = ExplicitMods.Clone(),
            RequireAnyModIds = new List<string>(RequireAnyModIds ?? new()), MinAnyModMatches = MinAnyModMatches,
            RequireAllModIds = new List<string>(RequireAllModIds ?? new()), ExcludedModIds = new List<string>(ExcludedModIds ?? new()),
            Color = Color, ArrowColor = ArrowColor, IndicatorMode = IndicatorMode, BorderStyle = BorderStyle,
            BorderThickness = BorderThickness, BorderMargin = BorderMargin, ArrowPosition = ArrowPosition, ArrowSize = ArrowSize
        };
    }
}
