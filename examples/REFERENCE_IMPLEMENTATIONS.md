# Small reference implementations in other languages

The JavaScript and C# examples use the existing synthetic lending-library fixture. Each verifies the sealed original source and normalized message chunk using byte lengths and SHA-256, checks that every message's half-open byte selector decodes to its recorded text, and reads one exact evidence window (`WIN-00005`). Both print the cited line and fail with a nonzero exit code when the source, chunk, or window is inconsistent.

From the repository root:

```sh
node examples/reference-js/evidence.mjs examples/memory
node --test examples/reference-js/evidence.test.mjs
dotnet run --project examples/reference-csharp/ReferenceEvidence.csproj -- examples/memory
```

The JavaScript example needs Node.js 20 or later. The C# example needs the .NET 10 SDK. Neither needs a third-party package. Pass another evidence-window ID as the second argument to read a different window in the same fixture.

These are **bounded demonstrations of source and evidence integrity**, not full ALM implementations. They do not validate all 17 entity kinds, run the 56 portable conformance cases, provide a memory service, or enforce live authorization. The Python contract checker remains the authoritative validator for this fixture. Builders can port the demonstrated byte and pointer checks into their own runtime while implementing the remaining contracts in any language.
