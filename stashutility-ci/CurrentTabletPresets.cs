namespace StashUtility.ProfilePacks
{
    using StashUtility.Models;
    using System.Collections.Generic;
    using System.Numerics;

    public static class CurrentTabletPresets
    {
        public static List<TabletRuleProfile> CreateAll() => new()
        {
            ExpeditionProfit(), RitualProfit(), AbyssDesecrated(), DeliriumSimulacrum(), BreachProfit(), TempleCrystals(), OverseerBossLoot(), IrradiatedJuice(), AnyAdditionalModifier()
        };
        public static List<TabletRuleProfile> CreateStarterPack() => new()
        {
            ExpeditionProfit(), RitualProfit(), AbyssDesecrated(), DeliriumSimulacrum(), BreachProfit(), TempleCrystals(), OverseerBossLoot(), IrradiatedJuice()
        };
        private static TabletRuleProfile P(string name, string type, Vector4 color, params string[] any) => new()
        {
            Name = name, TabletType = type, Color = color, ArrowColor = new Vector4(1f,.82f,.10f,1f),
            IndicatorMode = WaystoneIndicatorMode.BorderAndArrow, RequireAnyModIds = new List<string>(any), MinAnyModMatches = 1
        };
        public static TabletRuleProfile ExpeditionProfit() => P("Expedition — Profit", "Expedition Tablet", new Vector4(.95f,.55f,.12f,1f),
            "TowerMapAdditionalModifier","TowerExpeditionLogbookIncrease","TowerExpeditionRareMonsters","TowerExpeditionRelicModEffect","TowerExpeditionRunicMonsters","TowerExpeditionRelicIncrease","TowerExpeditionArtifactIncrease");
        public static TabletRuleProfile RitualProfit() => P("Ritual — Omens & Rerolls", "Ritual Tablet", new Vector4(.78f,.22f,.95f,1f),
            "TowerMapAdditionalModifier","TowerRitualOmenChance","TowerRitualAdditionalReroll","TowerRitualTributeIncrease","TowerRitualChanceForNoCost","TowerRitualMagicMonsters");
        public static TabletRuleProfile AbyssDesecrated() => P("Abyss — Desecrated", "Abyss Tablet", new Vector4(.32f,.85f,.48f,1f),
            "TowerMapAdditionalModifier","TowerAbyssExtraTickets","TowerAbyssRareMonsterIncrease","TowerAbyssIncreasedRewards","TowerAbyssEnhancedMonstersPerChasm","TowerAbyssAdditionalChance","TowerAbyss4AdditionalChance");
        public static TabletRuleProfile DeliriumSimulacrum() => P("Delirium — Simulacrum", "Delirium Tablet", new Vector4(.42f,.46f,1f,1f),
            "TowerMapAdditionalModifier","TowerDeliriumMonsterSplinterIncrease","TowerDeliriumDoodadsIncrease","TowerDeliriumPackSizeIncrease","TowerDeliriumAdditionalShardsChance","TowerDeliriumRareMonsterPause");
        public static TabletRuleProfile BreachProfit() => P("Breach — Wombgifts & Rares", "Breach Tablet", new Vector4(.20f,.78f,1f,1f),
            "TowerMapAdditionalModifier","TowerBreachWombgiftLevelChance","TowerBreachWombgiftQuantity","TowerBreachHivebloodQuantity","TowerBreachAdditionalRares","TowerBreachBossChance","TowerBreachMonsterQuantity");
        public static TabletRuleProfile TempleCrystals() => P("Temple — Crystals", "Temple Tablet", new Vector4(.95f,.30f,.30f,1f),
            "TowerMapAdditionalModifier","TowerIncursionTokenChance","TowerIncursionExtraPacks","TowerIncursionExtraPacksChance","TowerIncursionRareChestChance","TowerIncursionBossChance");
        public static TabletRuleProfile OverseerBossLoot() => P("Overseer — Boss Loot", "Overseer Tablet", new Vector4(1f,.76f,.16f,1f),
            "TowerMapAdditionalModifier","TowerMapBossQuantity","TowerMapBossRarity","TowerMapBossWaystoneChance","TowerMapBossAdditionalStrongbox","TowerAdditionalEssence");
        public static TabletRuleProfile IrradiatedJuice() => P("Irradiated — Juice", "Irradiated Tablet", new Vector4(.35f,1f,.72f,1f),
            "TowerMapAdditionalModifier","TowerRarePackIncrease","TowerMonsterRarityIncrease","TowerDroppedItemRarityIncrease","TowerPackSizeIncrease","TowerMonsterEffectiveness","TowerMagicPackIncrease");
        public static TabletRuleProfile AnyAdditionalModifier() => P("Any Tablet — Additional Modifiers", "Any", new Vector4(1f,.88f,.18f,1f), "TowerMapAdditionalModifier");
    }
}
