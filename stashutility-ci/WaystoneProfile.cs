namespace StashUtility.Models
{
    using System;
    using System.Collections.Generic;
    using System.Numerics;

    public sealed class IntRangeCriterion
    {
        public bool MinEnabled = false;
        public int Min = 0;
        public bool MaxEnabled = false;
        public int Max = 0;
        public bool IsActive => MinEnabled || MaxEnabled;
        public bool Matches(int value)
        {
            if (MinEnabled && value < Min) return false;
            if (MaxEnabled && value > Max) return false;
            return true;
        }
        public IntRangeCriterion Clone() => new() { MinEnabled = MinEnabled, Min = Min, MaxEnabled = MaxEnabled, Max = Max };
    }

    public enum WaystoneIndicatorMode { Border = 0, Arrow = 1, BorderAndArrow = 2 }

    public sealed class WaystoneSnapshot
    {
        public int Tier;
        public int Revives;
        public int ExplicitMods;
        public int ItemRarity;
        public int PackSize;
        public int MonsterRarity;
        public int MonsterEffectiveness;
        public int WaystoneDropChance;
    }

    public sealed class WaystoneProfile
    {
        public string Id = Guid.NewGuid().ToString("N");
        public string Name = "New profile";
        public string Description = string.Empty;
        public bool Enabled = true;
        public bool MatchEverything = false;

        public Vector4 Color = new(0.0f, 0.85f, 1.0f, 1.0f);
        public Vector4 ArrowColor = new(0.0f, 0.85f, 1.0f, 1.0f);
        public WaystoneIndicatorMode IndicatorMode = WaystoneIndicatorMode.Border;
        public int BorderStyle = 0;
        public float BorderThickness = 3.0f;
        public float BorderMargin = 4.0f;
        public int ArrowPosition = 0;
        public float ArrowSize = 20.0f;

        public IntRangeCriterion Tier = new();
        public IntRangeCriterion Revives = new();
        public IntRangeCriterion ExplicitMods = new();
        public IntRangeCriterion ItemRarity = new();
        public IntRangeCriterion PackSize = new();
        public IntRangeCriterion MonsterRarity = new();
        public IntRangeCriterion MonsterEffectiveness = new();
        public IntRangeCriterion WaystoneDropChance = new();

        public List<string> RequireAnyModIds = new();
        public int MinAnyModMatches = 1;
        public List<string> RequireAllModIds = new();
        public List<string> ExcludedModIds = new();

        public bool HasAnyCriteria() => Tier.IsActive || Revives.IsActive || ExplicitMods.IsActive || ItemRarity.IsActive || PackSize.IsActive || MonsterRarity.IsActive || MonsterEffectiveness.IsActive || WaystoneDropChance.IsActive || RequireAnyModIds.Count > 0 || RequireAllModIds.Count > 0 || ExcludedModIds.Count > 0;

        public bool Matches(WaystoneSnapshot s, HashSet<string> presentModIds)
        {
            if (!Enabled) return false;
            if (!HasAnyCriteria() && !MatchEverything) return false;
            if (!Tier.Matches(s.Tier) || !Revives.Matches(s.Revives) || !ExplicitMods.Matches(s.ExplicitMods) || !ItemRarity.Matches(s.ItemRarity) || !PackSize.Matches(s.PackSize) || !MonsterRarity.Matches(s.MonsterRarity) || !MonsterEffectiveness.Matches(s.MonsterEffectiveness) || !WaystoneDropChance.Matches(s.WaystoneDropChance)) return false;
            foreach (var id in ExcludedModIds) if (presentModIds.Contains(id)) return false;
            foreach (var id in RequireAllModIds) if (!presentModIds.Contains(id)) return false;
            if (RequireAnyModIds.Count > 0)
            {
                int need = Math.Clamp(MinAnyModMatches, 1, RequireAnyModIds.Count);
                int found = 0;
                foreach (var id in RequireAnyModIds) if (presentModIds.Contains(id)) found++;
                if (found < need) return false;
            }
            return true;
        }

        public WaystoneProfile DeepClone(string suffix = " copy") => new()
        {
            Id = Guid.NewGuid().ToString("N"), Name = Name + suffix, Description = Description, Enabled = Enabled, MatchEverything = MatchEverything,
            Color = Color, ArrowColor = ArrowColor, IndicatorMode = IndicatorMode, BorderStyle = BorderStyle, BorderThickness = BorderThickness, BorderMargin = BorderMargin, ArrowPosition = ArrowPosition, ArrowSize = ArrowSize,
            Tier = Tier.Clone(), Revives = Revives.Clone(), ExplicitMods = ExplicitMods.Clone(), ItemRarity = ItemRarity.Clone(), PackSize = PackSize.Clone(), MonsterRarity = MonsterRarity.Clone(), MonsterEffectiveness = MonsterEffectiveness.Clone(), WaystoneDropChance = WaystoneDropChance.Clone(),
            RequireAnyModIds = new List<string>(RequireAnyModIds), MinAnyModMatches = MinAnyModMatches, RequireAllModIds = new List<string>(RequireAllModIds), ExcludedModIds = new List<string>(ExcludedModIds)
        };
    }
}
