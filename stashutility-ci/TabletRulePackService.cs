namespace StashUtility.ProfilePacks
{
    using Newtonsoft.Json;
    using StashUtility.Models;
    using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Linq;

    public sealed class TabletRuleProfilePack
    {
        public string Schema = "stashutility.tablet-rules.v2";
        public string Name = "Tablet rule profiles";
        public string Description = string.Empty;
        public string CreatedUtc = DateTime.UtcNow.ToString("O");
        public List<TabletRuleProfile> Profiles = new();
    }

    public sealed class TabletRulePackService
    {
        public string DirectoryPath { get; }
        public TabletRulePackService(string dllDirectory)
        {
            DirectoryPath = Path.Combine(dllDirectory, "profiles", "tablets");
            Directory.CreateDirectory(DirectoryPath);
        }
        public IReadOnlyList<string> ListPacks() => Directory.GetFiles(DirectoryPath, "*.json").Select(Path.GetFileName).Where(x => !string.IsNullOrWhiteSpace(x)).OrderBy(x => x, StringComparer.OrdinalIgnoreCase).ToArray();
        private static string SafeName(string name)
        {
            if (string.IsNullOrWhiteSpace(name)) return "tablet-profiles";
            foreach (var c in Path.GetInvalidFileNameChars()) name = name.Replace(c, '_');
            return name.Trim();
        }
        public string Export(string name, List<TabletRuleProfile> profiles)
        {
            var pack = new TabletRuleProfilePack { Name = name, Profiles = (profiles ?? new()).Select(x => x.DeepClone("")).ToList() };
            var path = Path.Combine(DirectoryPath, SafeName(name) + ".json");
            File.WriteAllText(path, JsonConvert.SerializeObject(pack, Formatting.Indented));
            return path;
        }
        public TabletRuleProfilePack Import(string fileName)
        {
            var path = Path.Combine(DirectoryPath, Path.GetFileName(fileName));
            var json = File.ReadAllText(path);
            var probe = JsonConvert.DeserializeObject<Dictionary<string, object>>(json) ?? new();
            var schema = probe.TryGetValue("Schema", out var s1) ? s1?.ToString() : probe.TryGetValue("schema", out var s2) ? s2?.ToString() : string.Empty;
            if (string.Equals(schema, "stashutility.tablet-rules.v2", StringComparison.OrdinalIgnoreCase))
            {
                var pack = JsonConvert.DeserializeObject<TabletRuleProfilePack>(json) ?? throw new InvalidDataException("Invalid tablet rule profile pack.");
                foreach (var p in pack.Profiles ?? new()) p.Id = Guid.NewGuid().ToString("N");
                return pack;
            }
            if (string.Equals(schema, "stashutility.tablets.v1", StringComparison.OrdinalIgnoreCase))
            {
                var legacy = JsonConvert.DeserializeObject<TabletProfilePack>(json) ?? throw new InvalidDataException("Invalid legacy tablet pack.");
                var converted = new TabletRuleProfilePack { Name = legacy.Name + " (converted)", Description = "Converted from stashutility.tablets.v1" };
                foreach (var kv in legacy.Profiles ?? new())
                {
                    var src = kv.Value ?? new TabletProfile();
                    var any = new List<string>();
                    if (src.GodModPatterns != null) any.AddRange(src.GodModPatterns);
                    if (src.GoodModPatterns != null) any.AddRange(src.GoodModPatterns);
                    any = any.Distinct(StringComparer.OrdinalIgnoreCase).ToList();
                    converted.Profiles.Add(new TabletRuleProfile
                    {
                        Name = kv.Key.Replace(" Tablet", "") + " — Imported", TabletType = kv.Key,
                        RequireAnyModIds = any, MinAnyModMatches = 1,
                        ExcludedModIds = src.BadModPatterns?.Distinct(StringComparer.OrdinalIgnoreCase).ToList() ?? new(),
                        MatchEverything = any.Count == 0 && (src.BadModPatterns == null || src.BadModPatterns.Count == 0)
                    });
                }
                return converted;
            }
            throw new InvalidDataException($"Unsupported tablet profile schema: {schema}");
        }
    }
}
