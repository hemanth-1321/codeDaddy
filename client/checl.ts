// check-imports.ts
import fs from "fs";
import path from "path";

// Root folder of your project
const SRC_DIR = path.join(process.cwd(), "src");

function checkImports(dir: string) {
  const files = fs.readdirSync(dir);

  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      checkImports(fullPath);
    } else if (file.endsWith(".ts") || file.endsWith(".tsx")) {
      const content = fs.readFileSync(fullPath, "utf-8");
      const importRegex = /import\s+(?:.*?\s+from\s+)?["'](.+)["']/g;
      let match;
      while ((match = importRegex.exec(content)) !== null) {
        const importPath = match[1];

        // Skip node_modules packages
        if (importPath.startsWith(".") || importPath.startsWith("@")) {
          let resolvedPath = importPath;

          // Resolve alias @/ -> src/
          if (importPath.startsWith("@/")) {
            resolvedPath = path.join(SRC_DIR, importPath.slice(2));
          } else {
            resolvedPath = path.join(path.dirname(fullPath), importPath);
          }

          // Try with extensions
          const possibleExts = ["", ".ts", ".tsx", ".js", ".jsx"];
          const exists = possibleExts.some((ext) =>
            fs.existsSync(resolvedPath + ext)
          );

          if (!exists) {
            console.log(
              `❌ Missing import in ${fullPath}: "${importPath}" does not exist`
            );
          }
        }
      }
    }
  }
}

checkImports(SRC_DIR);
