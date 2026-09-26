// Bounded ALM reference example: verify captured source bytes and read one evidence window.
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

static class Program
{
    static readonly UTF8Encoding Utf8 = new(false, true);

    static string Text(JsonNode? node) => node?.GetValue<string>() ?? throw new InvalidDataException("missing text field");
    static int Number(JsonNode? node) => node?.GetValue<int>() ?? throw new InvalidDataException("missing integer field");

    static string FixturePath(string root, string name)
    {
        if (string.IsNullOrEmpty(name) || name.Contains('\\') || Path.IsPathFullyQualified(name))
            throw new InvalidDataException($"unsafe fixture path: {name}");
        var path = Path.GetFullPath(Path.Combine(root, name));
        var relative = Path.GetRelativePath(root, path);
        if (relative == "." || relative == ".." || relative.StartsWith(".." + Path.DirectorySeparatorChar))
            throw new InvalidDataException($"unsafe fixture path: {name}");
        return path;
    }

    static byte[] Bytes(string root, string name) => File.ReadAllBytes(FixturePath(root, name));

    static JsonNode Json(string root, string name) =>
        JsonNode.Parse(Utf8.GetString(Bytes(root, name))) ?? throw new InvalidDataException($"empty JSON: {name}");

    static void CheckDigest(byte[] bytes, int length, string digest, string label)
    {
        if (bytes.Length != length || !SHA256.HashData(bytes).AsSpan().SequenceEqual(Convert.FromHexString(digest)))
            throw new InvalidDataException($"{label}: byte length or SHA-256 mismatch");
    }

    static object ReadEvidence(string root, string windowId)
    {
        root = Path.GetFullPath(root);
        if (windowId.Length == 0 || windowId.Any(c => !char.IsAsciiLetterOrDigit(c) && c != '-'))
            throw new InvalidDataException("unsafe window ID");
        var manifest = Json(root, "log-manifest/LOG-EXAMPLE.json");
        var window = Json(root, $"evidence-window/{windowId}.json");
        if (Text(manifest["format_version"]) != "1" || Text(window["format_version"]) != "1" ||
            Text(window["id"]) != windowId || Text(window["log_id"]) != Text(manifest["id"]) ||
            Text(window["instance_id"]) != Text(manifest["instance_id"]) ||
            Text(window["source_digest"]) != Text(manifest["original_sha256"]))
            throw new InvalidDataException("window does not identify the sealed source");

        var original = Bytes(root, Text(manifest["original_file"]));
        CheckDigest(original, Number(manifest["original_byte_length"]), Text(manifest["original_sha256"]), "original");
        if (!Text(manifest["original_encoding"]).Equals("UTF-8", StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("this example supports UTF-8 sources only");

        var messages = new Dictionary<int, JsonNode>();
        int nextOrdinal = 1, nextChunk = 1, previousEnd = 0;
        foreach (var chunk in manifest["chunks"]?.AsArray() ?? throw new InvalidDataException("missing chunks"))
        {
            if (chunk is null || Number(chunk["number"]) != nextChunk++ || Number(chunk["message_start"]) != nextOrdinal)
                throw new InvalidDataException("chunk numbering or message coverage is not contiguous");
            var raw = Bytes(root, Text(chunk["file"]));
            CheckDigest(raw, Number(chunk["byte_length"]), Text(chunk["sha256"]), $"chunk {Number(chunk["number"])}");
            var chunkText = Utf8.GetString(raw);
            if (!chunkText.EndsWith('\n') || chunkText.Contains('\r'))
                throw new InvalidDataException($"chunk {Number(chunk["number"])}: expected LF-terminated JSONL");
            foreach (var line in chunkText[..^1].Split('\n'))
            {
                var message = JsonNode.Parse(line) ?? throw new InvalidDataException("empty message");
                int start = Number(message["original_byte_start"]), end = Number(message["original_byte_end"]);
                if (Text(message["log_id"]) != Text(manifest["id"]) ||
                    Text(message["instance_id"]) != Text(manifest["instance_id"]) ||
                    Number(message["ordinal"]) != nextOrdinal || start < previousEnd || end < start || end > original.Length)
                    throw new InvalidDataException($"invalid message order or source selector at ordinal {nextOrdinal}");
                if (Utf8.GetString(original, start, end - start) != Text(message["text"]))
                    throw new InvalidDataException($"source text mismatch at ordinal {nextOrdinal}");
                messages.Add(nextOrdinal, message);
                previousEnd = end;
                nextOrdinal++;
            }
            if (Number(chunk["message_end"]) != nextOrdinal - 1)
                throw new InvalidDataException("chunk message end disagrees with rows");
        }
        if (Text(manifest["completeness"]) == "complete" && manifest["missing_ranges"]?.AsArray().Count != 0)
            throw new InvalidDataException("complete log declares missing ranges");
        int first = Number(window["message_start"]), last = Number(window["message_end"]);
        if (first < 1 || first > last) throw new InvalidDataException("invalid evidence window bounds");
        var cited = new List<object>();
        for (int ordinal = first; ordinal <= last; ordinal++)
        {
            if (!messages.TryGetValue(ordinal, out var message))
                throw new InvalidDataException($"missing cited message {ordinal}");
            cited.Add(new { ordinal, timestamp = Text(message["timestamp"]), text = Text(message["text"]) });
        }
        return new { windowId, logId = Text(manifest["id"]), cited };
    }

    static int Main(string[] args)
    {
        try
        {
            var root = args.Length > 0 ? args[0] : "examples/memory";
            var result = ReadEvidence(root, args.Length > 1 ? args[1] : "WIN-00005");
            Console.WriteLine(JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true }));
            return 0;
        }
        catch (Exception error) when (error is IOException or JsonException or ArgumentException or InvalidOperationException or FormatException)
        {
            Console.Error.WriteLine(error.Message);
            return 1;
        }
    }
}
