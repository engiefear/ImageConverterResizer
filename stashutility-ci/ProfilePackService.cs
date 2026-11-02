namespace StashUtility.ProfilePacks
{
    using Newtonsoft.Json;
    using StashUtility.Models;
    using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Linq;

    public sealed class WaystoneProfilePack
    {
        public string Schema = "stashutility.waystones.v1";
        public string Name = "Waystone profiles";
        public string Description = string.Empty;
        public string CreatedUtc = DateTime.UtcNow.ToString("O");
        public List<WaystoneProfile> Profiles = new();
    }

    public sealed class TabletProfilePack
    {
        public string Schema = "stashutility.tablets.v1";
        public string Name = "Tablet profiles";
        public string Description = string.Empty;
        public string CreatedUtc = DateTime.UtcNow.ToString("O");
        public Dictionary<string, TabletProfile> Profiles = new();
    }

    public sealed class JewelProfilePack
    {
        public string Schema = "stashutility.jewels.v1";
        public string Name = "Jewel profiles";
        public string Description = string.Empty;
        public string CreatedUtc = DateTime.UtcNow.ToString("O");
        public Dictionary<string, List<StashUtility.Models.JewelGroup>> Categories = new();
    }

    public sealed class ProfilePackService
    {
        public string RootDirectory { get; }
        public ProfilePackService(string dllDirectory)
        {
            RootDirectory = Path.Combine(dllDirectory, "profiles");
            Directory.CreateDirectory(Path.Combine(RootDirectory, "waystones"));
            Directory.CreateDirectory(Path.Combine(RootDirectory, "tablets"));
            Directory.CreateDirectory(Path.Combine(RootDirectory, "jewels"));
        }
        public string WaystoneDirectory => Path.Combine(RootDirectory, "waystones");
        public string TabletDirectory => Path.Combine(RootDirectory, "tablets");
        public string JewelDirectory => Path.Combine(RootDirectory, "jewels");
        public IReadOnlyList<string> ListWaystonePacks() => ListJson(WaystoneDirectory);
        public IReadOnlyList<string> ListTabletPacks() => ListJson(TabletDirectory);
        public IReadOnlyList<string> ListJewelPacks() => ListJson(JewelDirectory);
        private static IReadOnlyList<string> ListJson(string dir) => Directory.GetFiles(dir, "*.json").Select(Path.GetFileName).Where(x => !string.IsNullOrWhiteSpace(x)).OrderBy(x => x, StringComparer.OrdinalIgnoreCase).ToArray();
        private static string SafeName(string name)
        {
            if (string.IsNullOrWhiteSpace(name)) return "profile-pack";
            foreach (var c in Path.GetInvalidFileNameChars()) name = name.Replace(c, '_');
            return name.Trim();
        }
        public string ExportWaystones(string name, List<WaystoneProfile> profiles)
        {
            var pack = new WaystoneProfilePack { Name = name, Profiles = profiles.Select(x => x.DeepClone("")).ToList() };
            var path = Path.Combine(WaystoneDirectory, SafeName(name) + ".json");
            File.WriteAllText(path, JsonConvert.SerializeObject(pack, Formatting.Indented));
            return path;
        }
        public WaystoneProfilePack ImportWaystones(string fileName)
        {
            var path = Path.Combine(WaystoneDirectory, Path.GetFileName(fileName));
            var pack = JsonConvert.DeserializeObject<WaystoneProfilePack>(File.ReadAllText(path)) ?? throw new InvalidDataException("Invalid waystone profile pack.");
            if (!string.Equals(pack.Schema, "stashutility.waystones.v1", StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException($"Unsupported schema: {pack.Schema}");
            foreach (var p in pack.Profiles) p.Id = Guid.NewGuid().ToString("N");
            return pack;
        }
        public string ExportTablets(string name, Dictionary<string, TabletProfile> profiles)
        {
            var copied = JsonConvert.DeserializeObject<Dictionary<string, TabletProfile>>(JsonConvert.SerializeObject(profiles)) ?? new();
            var pack = new TabletProfilePack { Name = name, Profiles = copied };
            var path = Path.Combine(TabletDirectory, SafeName(name) + ".json");
            File.WriteAllText(path, JsonConvert.SerializeObject(pack, Formatting.Indented));
            return path;
        }
        public TabletProfilePack ImportTablets(string fileName)
        {
            var path = Path.Combine(TabletDirectory, Path.GetFileName(fileName));
            var pack = JsonConvert.DeserializeObject<TabletProfilePack>(File.ReadAllText(path)) ?? throw new InvalidDataException("Invalid tablet profile pack.");
            if (!string.Equals(pack.Schema, "stashutility.tablets.v1", StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException($"Unsupported schema: {pack.Schema}");
            return pack;
        }
        public string ExportJewels(string name, Dictionary<string, List<StashUtility.Models.JewelGroup>> categories)
        {
            var copied = JsonConvert.DeserializeObject<Dictionary<string, List<StashUtility.Models.JewelGroup>>>(JsonConvert.SerializeObject(categories)) ?? new();
            var pack = new JewelProfilePack { Name = name, Categories = copied };
            var path = Path.Combine(JewelDirectory, SafeName(name) + ".json");
            File.WriteAllText(path, JsonConvert.SerializeObject(pack, Formatting.Indented));
            return path;
        }
        public JewelProfilePack ImportJewels(string fileName)
        {
            var path = Path.Combine(JewelDirectory, Path.GetFileName(fileName));
            var pack = JsonConvert.DeserializeObject<JewelProfilePack>(File.ReadAllText(path)) ?? throw new InvalidDataException("Invalid jewel profile pack.");
            if (!string.Equals(pack.Schema, "stashutility.jewels.v1", StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException($"Unsupported schema: {pack.Schema}");
            return pack;
        }
    }
}
