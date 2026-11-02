namespace StashUtility.ProfilePacks
{
    using StashUtility.Models;
    using System.Collections.Generic;
    using System.Numerics;

    public static class DefaultWaystonePresets
    {
        public static IReadOnlyList<WaystoneProfile> CreateAll() => new[]
        {
            Ritual(), SimulacrumSplinters(), HighEffectiveness(), AbyssBudget(), AbyssRareMonsters(), Expedition(), Breach(), WaystoneSustain()
        };

        private static WaystoneProfile Base(string name, string description, Vector4 color) => new()
        {
            Name = name, Description = description, Color = color, ArrowColor = color,
            Tier = new IntRangeCriterion { MinEnabled = true, Min = 15 }
        };

        public static WaystoneProfile Ritual()
        {
            var p = Base("Ritual", "Editable starter: pack size + monster rarity.", new Vector4(.72f,.30f,.95f,1f));
            p.PackSize = new IntRangeCriterion { MinEnabled = true, Min = 25 };
            p.MonsterRarity = new IntRangeCriterion { MinEnabled = true, Min = 15 };
            return p;
        }
        public static WaystoneProfile SimulacrumSplinters()
        {
            var p = Base("Simulacrum splinters / Delirium", "Editable starter: 5 mods + high monster rarity.", new Vector4(.25f,.55f,1f,1f));
            p.ExplicitMods = new IntRangeCriterion { MinEnabled = true, Min = 5, MaxEnabled = true, Max = 5 };
            p.MonsterRarity = new IntRangeCriterion { MinEnabled = true, Min = 100 };
            return p;
        }
        public static WaystoneProfile HighEffectiveness()
        {
            var p = Base("High effectiveness", "Generic editable profile.", new Vector4(.35f,.70f,1f,1f));
            p.MonsterEffectiveness = new IntRangeCriterion { MinEnabled = true, Min = 85 };
            return p;
        }
        public static WaystoneProfile AbyssBudget()
        {
            var p = Base("Abyss - budget rarity", "Editable item-rarity starter.", new Vector4(.20f,.82f,.42f,1f));
            p.ItemRarity = new IntRangeCriterion { MinEnabled = true, Min = 25 };
            return p;
        }
        public static WaystoneProfile AbyssRareMonsters()
        {
            var p = Base("Abyss - rare monster focus", "Editable monster-rarity starter.", new Vector4(.10f,.95f,.35f,1f));
            p.MonsterRarity = new IntRangeCriterion { MinEnabled = true, Min = 50 };
            return p;
        }
        public static WaystoneProfile Expedition()
        {
            var p = Base("Expedition", "Editable effectiveness / rarity starter.", new Vector4(.95f,.70f,.18f,1f));
            p.MonsterEffectiveness = new IntRangeCriterion { MinEnabled = true, Min = 30 };
            p.MonsterRarity = new IntRangeCriterion { MinEnabled = true, Min = 40 };
            p.ItemRarity = new IntRangeCriterion { MinEnabled = true, Min = 40 };
            return p;
        }
        public static WaystoneProfile Breach()
        {
            var p = Base("Breach - density", "Editable pack-size starter.", new Vector4(.85f,.25f,.55f,1f));
            p.PackSize = new IntRangeCriterion { MinEnabled = true, Min = 30 };
            return p;
        }
        public static WaystoneProfile WaystoneSustain()
        {
            var p = Base("Waystone sustain", "Editable drop-chance starter.", new Vector4(.20f,.85f,.95f,1f));
            p.WaystoneDropChance = new IntRangeCriterion { MinEnabled = true, Min = 120 };
            return p;
        }
    }
}
